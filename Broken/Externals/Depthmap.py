# pyright: reportMissingImports=false

import copy
import functools
import hashlib
import multiprocessing
from abc import ABC, abstractmethod
from io import BytesIO
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypeAlias, Union

import numpy
from diskcache import Cache as DiskCache
from halo import Halo
from PIL import Image
from PIL.Image import Image as ImageType
from pydantic import Field, PrivateAttr
from typer import Option

import Broken
from Broken import (
    BrokenCache,
    BrokenEnum,
    BrokenPath,
    BrokenResolution,
    BrokenTyper,
    Environment,
    install,
    log,
)
from Broken.Externals import ExternalModelsBase, ExternalTorchBase
from Broken.Loaders import LoadableImage, LoadImage
from Broken.Types import MiB

if TYPE_CHECKING:
    import diffusers
    import torch

# ------------------------------------------------------------------------------------------------ #

class DepthEstimatorBase(
    ExternalTorchBase,
    ExternalModelsBase,
    ABC
):
    _cache: DiskCache = PrivateAttr(default_factory=lambda: DiskCache(
        directory=(Broken.PROJECT.DIRECTORIES.CACHE/"DepthEstimator"),
        size_limit=int(Environment.float("DEPTHMAP_CACHE_SIZE_MB", 50)*MiB),
    ))
    """DiskCache object for caching depth maps"""

    _format: str = PrivateAttr("png")
    """The format to save the depth map as"""

    @staticmethod
    def normalize(array: numpy.ndarray) -> numpy.ndarray: # Fixme: Better place?
        return (array - array.min()) / ((array.max() - array.min()) or 1)

    @classmethod
    def normalize_uint16(cls, array: numpy.ndarray) -> numpy.ndarray: # Fixme: Better place?
        return ((2**16 - 1) * cls.normalize(array.astype(numpy.float32))).astype(numpy.uint16)

    @staticmethod
    def image_hash(image: LoadableImage) -> int: # Fixme: Better place?
        # Fixme: Speed gains on improving this heuristic, but it's good enough for now
        return int(hashlib.sha256(LoadImage(image).tobytes()).hexdigest(), 16)

    def estimate(self,
        image: LoadableImage,
        cache: bool=True
    ) -> numpy.ndarray:

        # Hashlib for deterministic hashes, join class name, model, and image hash
        image: ImageType = numpy.array(LoadImage(image).convert("RGB"))
        image_hash: str = f"{hash(self)}{DepthEstimatorBase.image_hash(image)}"
        image_hash: int = int(hashlib.sha256(image_hash.encode()).hexdigest(), 16)

        # Estimate if not on cache
        if (not cache) or (depth := self._cache.get(image_hash)) is None:
            self.load_torch()
            self.load_model()
            torch.set_num_threads(multiprocessing.cpu_count())
            depth = DepthEstimatorBase.normalize_uint16(self._estimate(image))
            Image.fromarray(depth).save(buffer := BytesIO(), format=self._format)
            self._cache.set(key=image_hash, value=buffer.getvalue())
        else:
            # Load the virtual file raw bytes as numpy
            depth = numpy.array(Image.open(BytesIO(depth)))

        return DepthEstimatorBase.normalize(self._post_processing(depth))

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

class DepthAnythingBase(DepthEstimatorBase):
    class Model(str, BrokenEnum):
        Small = "small"
        Base  = "base"
        Large = "large"

    model: Annotated[Model, Option("--model", "-m",
        help="[bold red](🔴 Basic)[/] What model of DepthAnythingV2 to use")] = \
        Field(Model.Small)

    _processor: Any = PrivateAttr(None)

    @property
    @abstractmethod
    def _huggingface_model(self) -> str:
        ...

    def _load_model(self) -> None:
        import transformers
        log.info(f"Loading Depth Estimator model ({self._huggingface_model})")
        if (self.model != self.Model.Small):
            log.warning("[bold light_coral]• This model's license is CC BY-NC 4.0[/]")
        self._processor = BrokenCache.lru(transformers.AutoImageProcessor.from_pretrained)(self._huggingface_model, use_fast=False)
        self._model = BrokenCache.lru(transformers.AutoModelForDepthEstimation.from_pretrained)(self._huggingface_model)
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

    @property
    def _huggingface_model(self) -> str:
        return f"LiheYoung/depth-anything-{self.model.value}-hf"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.3)
        depth = maximum_filter(input=depth, size=5)
        return depth

class DepthAnythingV2(DepthAnythingBase):
    """Configure and use DepthAnythingV2 [dim](by https://github.com/DepthAnything/Depth-Anything-V2)[/]"""
    type: Annotated[Literal["depthanything2"], BrokenTyper.exclude()] = "depthanything2"
    indoor:  bool = Field(False, help="Use an indoor fine-tuned metric model")
    outdoor: bool = Field(False, help="Use an outdoor fine-tuned metric model")

    @property
    def _huggingface_model(self) -> str:
        if (self.indoor):
            return f"depth-anything/Depth-Anything-V2-Metric-Indoor-{self.model.value}-hf"
        elif (self.outdoor):
            return f"depth-anything/Depth-Anything-V2-Metric-Outdoor-{self.model.value}-hf"
        else:
            return f"depth-anything/Depth-Anything-V2-{self.model.value}-hf"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        if (self.indoor or self.outdoor):
            depth = (numpy.max(depth) - depth)
        depth = gaussian_filter(input=depth, sigma=0.6)
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

class DepthPro(DepthEstimatorBase):
    """Configure and use DepthPro        [dim](by Apple https://github.com/apple/ml-depth-pro)[/]"""
    type: Annotated[Literal["depthpro"], BrokenTyper.exclude()] = "depthpro"

    _model: Any = PrivateAttr(None)
    _transform: Any = PrivateAttr(None)

    def _load_model(self) -> None:
        log.info("Loading Depth Estimator model (DepthPro)")
        install(packages="depth_pro", pypi="git+https://github.com/apple/ml-depth-pro")

        # Download external checkpoint model
        checkpoint = BrokenPath.get_external("https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt")

        import torch
        from depth_pro import create_model_and_transforms
        from depth_pro.depth_pro import DEFAULT_MONODEPTH_CONFIG_DICT

        # Change the checkpoint URI to the downloaded checkpoint
        config = copy.deepcopy(DEFAULT_MONODEPTH_CONFIG_DICT)
        config.checkpoint_uri = checkpoint

        with Halo("Creating DepthPro model"):
            self._model, self._transform = BrokenCache.lru(
                create_model_and_transforms
            )(
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

class ZoeDepth(DepthEstimatorBase):
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
        self._model = BrokenCache.lru(torch.hub.load)(
            "isl-org/ZoeDepth", f"ZoeD_{self.model.value.upper()}",
            pretrained=True, trust_repo=True
        ).to(self.device)

    # Downscale for the largest component to be 512 pixels (Zoe precision), invert for 0=infinity
    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        depth = Image.fromarray(1 - DepthEstimatorBase.normalize(self._model.infer_pil(image)))
        new = BrokenResolution.fit(old=depth.size, max=(512, 512), ar=depth.size[0]/depth.size[1])
        return numpy.array(depth.resize(new, resample=Image.LANCZOS)).astype(numpy.float32)

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        return depth

# ------------------------------------------------------------------------------------------------ #

class Marigold(DepthEstimatorBase):
    """Configure and use Marigold        [dim](by https://github.com/prs-eth/Marigold)[/]"""
    type: Annotated[Literal["marigold"], BrokenTyper.exclude()] = "marigold"

    class Variant(str, BrokenEnum):
        FP16 = "fp16"
        FP32 = "fp32"

    variant: Annotated[Variant, Option("--variant", "-v",
        help="What variant of Marigold to use")] = \
        Field(Variant.FP16)

    def _load_model(self) -> None:
        install(packages=("accelerate", "diffusers", "matplotlib"))

        from diffusers import DiffusionPipeline

        log.info("Loading Depth Estimator model (Marigold)")
        log.warning("Note: Use FP16 for CPU, but it's VERY SLOW")
        self._model = BrokenCache.lru(DiffusionPipeline.from_pretrained)(
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
    DepthEstimatorBase,
    DepthAnythingV1,
    DepthAnythingV2,
    DepthPro,
    ZoeDepth,
    Marigold,
]
