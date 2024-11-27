# pyright: reportMissingImports=false

import contextlib
import copy
import functools
import itertools
import multiprocessing
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypeAlias, Union

import numpy
from halo import Halo
from PIL import Image
from pydantic import Field, PrivateAttr
from typer import Option

import Broken
from Broken import (
    BrokenEnum,
    BrokenPath,
    BrokenResolution,
    BrokenTyper,
    image_hash,
    install,
    log,
)
from Broken.Externals import ExternalModelsBase, ExternalTorchBase
from Broken.Loaders import LoadableImage, LoaderImage

if TYPE_CHECKING:
    import diffusers
    import torch

# ------------------------------------------------------------------------------------------------ #

MODELS_CACHE = (Broken.BROKEN.DIRECTORIES.EXTERNAL_MODELS)

os.environ.update(dict(
    TORCH_HOME=str(MODELS_CACHE),
    HF_HOME=str(MODELS_CACHE),
))

# ------------------------------------------------------------------------------------------------ #

class BaseEstimator(
    ExternalTorchBase,
    ExternalModelsBase,
    ABC
):
    _cache: Path = PrivateAttr(default=Broken.PROJECT.DIRECTORIES.CACHE/"DepthEstimator")
    """Path where the depth map will be cached. Broken.PROJECT is the current working project"""

    _format: str = PrivateAttr("png")
    """The format to save the depth map as"""

    @staticmethod
    def normalize(array: numpy.ndarray) -> numpy.ndarray: # Fixme: Better place
        return (array - array.min()) / ((array.max() - array.min()) or 1)

    @staticmethod
    def normalize_uint16(array: numpy.ndarray) -> numpy.ndarray:
        return ((2**16 - 1) * BaseEstimator.normalize(array.astype(numpy.float32))).astype(numpy.uint16)

    def estimate(self,
        image: LoadableImage,
        cache: bool=True
    ) -> numpy.ndarray:

        # Load image and find expected cache path
        image = numpy.array(LoaderImage(image).convert("RGB"))
        cached_image = self._cache/f"{self.__class__.__name__}-{self.model}-{image_hash(image)}.{self._format}"
        cached_image.parent.mkdir(parents=True, exist_ok=True)

        # Load cached estimation if found
        if (cache and cached_image.exists()):
            depth = numpy.array(Image.open(cached_image))
            cached_image.touch()
        else:
            self.load_torch()
            self.load_model()
            with self._lock, Halo(f"Estimating Depthmap (Torch: {self.device})"):
                torch.set_num_threads(max(4, multiprocessing.cpu_count()//2))
                depth = self._estimate(image)
            depth = BaseEstimator.normalize_uint16(depth)
            Image.fromarray(depth).save(cached_image)
            with contextlib.suppress(Exception):
                self.cleanup()

        return BaseEstimator.normalize(self._post_processing(depth))

    def normal_map(self, depth: numpy.ndarray) -> numpy.ndarray:
        """Estimates a normal map from a depth map using heuristics"""
        depth = numpy.array(depth)
        if depth.ndim == 3:
            depth = depth[..., 0]
        dx = numpy.arctan2(200*numpy.gradient(depth, axis=1), 1)
        dy = numpy.arctan2(200*numpy.gradient(depth, axis=0), 1)
        normal = numpy.dstack((-dx, dy, numpy.ones_like(depth)))
        return BaseEstimator.normalize(normal).astype(numpy.float32)

    def cleanup(self, maximum: int=20) -> None:
        files = list(os.scandir(self._cache))

        if (overflow := (len(files) - maximum)) > 0:
            files = sorted(files, key=os.path.getmtime)

            for file in itertools.islice(files, overflow):
                log.debug(f"Removing old depthmap: {file.path}")
                os.unlink(file.path)

    @functools.wraps(estimate)
    @abstractmethod
    def _estimate(self):
        """The implementation shall return a normalized numpy f32 array of the depth map"""
        ...

    @abstractmethod
    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        """A step to apply post processing on the depth map if needed"""
        return depth

# ------------------------------------------------------------------------------------------------ #

class DepthAnythingBase(BaseEstimator):
    class Model(str, BrokenEnum):
        Small = "small"
        Base  = "base"
        Large = "large"

    model: Annotated[Model, Option("--model", "-m",
        help="[bold red](🔴 Basic)[/] What model of DepthAnythingV2 to use")] = \
        Field(Model.Small)

    _processor: Any = PrivateAttr(None)

    @abstractmethod
    def _model_prefix(self) -> str:
        ...

    def _load_model(self) -> None:
        import transformers
        HUGGINGFACE_MODEL = (f"{self._model_prefix()}{self.model.value}-hf")
        log.info(f"Loading Depth Estimator model ({HUGGINGFACE_MODEL})")
        self._processor = transformers.AutoImageProcessor.from_pretrained(HUGGINGFACE_MODEL)
        self._model = transformers.AutoModelForDepthEstimation.from_pretrained(HUGGINGFACE_MODEL)
        self._model.to(self.device)

    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        inputs = self._processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            depth = self._model(**inputs).predicted_depth
        return depth.squeeze(1).cpu().numpy()[0]

class DepthAnythingV1(DepthAnythingBase):
    """Configure and use DepthAnythingV1 [dim](by https://github.com/LiheYoung/Depth-Anything)[/]"""
    type: Annotated[Literal["depthanything"], BrokenTyper.exclude()] = "depthanything"

    def _model_prefix(self) -> str:
        return "LiheYoung/depth-anything-"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.3)
        depth = maximum_filter(input=depth, size=5)
        return depth

class DepthAnythingV2(DepthAnythingBase):
    """Configure and use DepthAnythingV2 [dim](by https://github.com/DepthAnything/Depth-Anything-V2)[/]"""
    type: Annotated[Literal["depthanything2"], BrokenTyper.exclude()] = "depthanything2"

    def _model_prefix(self) -> str:
        return "depth-anything/Depth-Anything-V2-"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.6)
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

class DepthPro(BaseEstimator):
    """Configure and use DepthPro        [dim](by Apple https://github.com/apple/ml-depth-pro)[/]"""
    type: Annotated[Literal["depthpro"], BrokenTyper.exclude()] = "depthpro"

    _model: Any = PrivateAttr(None)
    _transform: Any = PrivateAttr(None)

    def _load_model(self) -> None:
        log.info("Loading Depth Estimator model (DepthPro)")
        install("depth_pro", pypi="git+https://github.com/apple/ml-depth-pro")

        # Download external checkpoint model
        checkpoint = BrokenPath.get_external("https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt")

        import torch
        from depth_pro import create_model_and_transforms
        from depth_pro.depth_pro import DEFAULT_MONODEPTH_CONFIG_DICT

        # Change the checkpoint URI to the downloaded checkpoint
        config = copy.deepcopy(DEFAULT_MONODEPTH_CONFIG_DICT)
        config.checkpoint_uri = checkpoint

        with Halo("Creating DepthPro model"):
            self._model, self._transform = create_model_and_transforms(
                precision=torch.float16,
                device=self.device,
                config=config
            )
            self._model.eval()

    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:

        # Infer, transfer to CPU, invert depth values
        depth = self._model.infer(self._transform(image))["depth"]
        depth = depth.detach().cpu().numpy().squeeze()
        depth = (numpy.max(depth) - depth)

        # Limit resolution to 1024 as there's no gains in interpoilation
        depth = numpy.array(Image.fromarray(depth).resize(BrokenResolution.fit(
            old=depth.shape, max=(1024, 1024),
            ar=(depth.shape[1]/depth.shape[0]),
        ), resample=Image.LANCZOS))

        return depth

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import maximum_filter
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

class ZoeDepth(BaseEstimator):
    """Configure and use ZoeDepth        [dim](by https://github.com/isl-org/ZoeDepth)[/]"""
    type: Annotated[Literal["zoedepth"], BrokenTyper.exclude()] = "zoedepth"

    class Model(str, BrokenEnum):
        N  = "n"
        K  = "k"
        NK = "nk"

    model: Annotated[Model, Option("--model", "-m",
        help="[bold red](🔴 Basic)[/] What model of ZoeDepth to use")] = \
        Field(Model.N)

    def _load_model(self) -> None:
        install(packages="timm", pypi="timm==0.6.7", args="--no-deps")

        log.info(f"Loading Depth Estimator model (ZoeDepth-{self.model.value})")
        self._model = torch.hub.load(
            "isl-org/ZoeDepth", f"ZoeD_{self.model.value.upper()}",
            pretrained=True, trust_repo=True
        ).to(self.device)

    # Downscale for the largest component to be 512 pixels (Zoe precision), invert for 0=infinity
    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        depth = Image.fromarray(1 - BaseEstimator.normalize(self._model.infer_pil(image)))
        new = BrokenResolution.fit(old=depth.size, max=(512, 512), ar=depth.size[0]/depth.size[1])
        return numpy.array(depth.resize(new, resample=Image.LANCZOS)).astype(numpy.float32)

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        return depth

# ------------------------------------------------------------------------------------------------ #

class Marigold(BaseEstimator):
    """Configure and use Marigold        [dim](by https://github.com/prs-eth/Marigold)[/]"""
    type: Annotated[Literal["marigold"], BrokenTyper.exclude()] = "marigold"

    class Variant(str, BrokenEnum):
        FP16 = "fp16"
        FP32 = "fp32"

    variant: Annotated[Variant, Option("--variant", "-v",
        help="What variant of Marigold to use")] = \
        Field(Variant.FP16)

    def _load_model(self) -> None:
        install("accelerate", "diffusers", "matplotlib")

        from diffusers import DiffusionPipeline

        log.info("Loading Depth Estimator model (Marigold)")
        log.warning("Note: Use FP16 for CPU, but it's VERY SLOW")
        self._model = DiffusionPipeline.from_pretrained(
            "prs-eth/marigold-depth-lcm-v1-0",
            custom_pipeline="marigold_depth_estimation",
            torch_dtype=dict(
                fp16=torch.float16,
                fp32=torch.float32,
            )[self.variant.value],
            variant=self.variant.value,
        ).to(self.device)

    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        return (1 - self._model(
            Image.fromarray(image),
            match_input_res=False,
            show_progress_bar=True,
            color_map=None,
        ).depth_np)

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.6)
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

DepthEstimator: TypeAlias = Union[
    DepthAnythingV1,
    DepthAnythingV2,
    DepthPro,
    ZoeDepth,
    Marigold,
]
