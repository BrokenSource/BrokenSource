# pyright: reportMissingImports=false

import functools
import multiprocessing
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

import numpy
import typer
from halo import Halo
from PIL import Image
from pydantic import Field, PrivateAttr

import Broken
from Broken import (
    BrokenEnum,
    BrokenResolution,
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

class DepthEstimator(ExternalTorchBase, ExternalModelsBase, ABC):

    _cache: Path = PrivateAttr(default=Broken.PROJECT.DIRECTORIES.CACHE/"DepthEstimator")
    """Path where the depth map will be cached. Broken.PROJECT is the current working project"""

    def normalize(self, array: numpy.ndarray) -> numpy.ndarray: # Fixme: Better place
        return (array - array.min()) / ((array.max() - array.min()) or 1)

    def estimate(self,
        image: LoadableImage,
        cache: bool=True
    ) -> numpy.ndarray:

        # Load image and find expected cache path
        image = numpy.array(LoaderImage(image).convert("RGB"))
        cached_image = self._cache/f"{image_hash(image)}-{self.__class__.__name__}-{self.model}.png"
        cached_image.parent.mkdir(parents=True, exist_ok=True)

        # Load cached estimation if found
        if (cache and cached_image.exists()):
            depth = numpy.array(Image.open(cached_image))
        else:
            self.load_torch()
            self.load_model()
            with self._lock, Halo(f"Estimating Depthmap (Torch: {self.device})"):
                torch.set_num_threads(max(4, multiprocessing.cpu_count()//2))
                depth = self._estimate(image)
            depth = (self.normalize(depth) * (2**16 - 1)).astype(numpy.uint16)
            Image.fromarray(depth).save(cached_image)
        return self.normalize(self._post_processing(depth))

    def normal_map(self, depth: numpy.ndarray) -> numpy.ndarray:
        """Estimates a normal map from a depth map using heuristics"""
        depth = numpy.array(depth)
        if depth.ndim == 3:
            depth = depth[..., 0]
        dx = numpy.arctan2(200*numpy.gradient(depth, axis=1), 1)
        dy = numpy.arctan2(200*numpy.gradient(depth, axis=0), 1)
        normal = numpy.dstack((-dx, dy, numpy.ones_like(depth)))
        return self.normalize(normal).astype(numpy.float32)

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

class DepthAnythingBase(DepthEstimator):
    class Model(BrokenEnum):
        Small = "small"
        Base  = "base"
        Large = "large"

    model: Annotated[Model, typer.Option("--model", "-m",
        help="[bold red](🔴 Basic)[reset] What model of DepthAnythingV2 to use")] = \
        Field(default=Model.Base)

    _processor: Any = PrivateAttr(default=None)

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
    """Configure and use DepthAnythingV1 [dim](by https://github.com/LiheYoung/Depth-Anything)[reset]"""
    def _model_prefix(self) -> str:
        return  "LiheYoung/depth-anything-"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.3)
        depth = maximum_filter(input=depth, size=5)
        return depth

class DepthAnythingV2(DepthAnythingBase):
    """Configure and use DepthAnythingV2 [dim](by https://github.com/DepthAnything/Depth-Anything-V2)[reset]"""
    def _model_prefix(self) -> str:
        return "depth-anything/Depth-Anything-V2-"

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.6)
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

class ZoeDepth(DepthEstimator):
    """Configure and use ZoeDepth        [dim](by https://github.com/isl-org/ZoeDepth)[reset]"""
    class Model(BrokenEnum):
        N  = "n"
        K  = "k"
        NK = "nk"

    model: Annotated[Model, typer.Option("--model", "-m",
        help="[bold red](🔴 Basic)[reset] What model of ZoeDepth to use")] = \
        Field(default=Model.N)

    def _load_model(self) -> None:
        install(packages="timm", pypi="timm==0.6.7", args="--no-deps")

        log.info(f"Loading Depth Estimator model (ZoeDepth-{self.model.value})")
        self._model = torch.hub.load(
            "isl-org/ZoeDepth", f"ZoeD_{self.model.value.upper()}",
            pretrained=True, trust_repo=True
        ).to(self.device)

    # Downscale for the largest component to be 512 pixels (Zoe precision), invert for 0=infinity
    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        depth = Image.fromarray(1 - self.normalize(self._model.infer_pil(image)))
        new = BrokenResolution.fit(old=depth.size, max=(512, 512), ar=depth.size[0]/depth.size[1])
        return numpy.array(depth.resize(new, resample=Image.LANCZOS)).astype(numpy.float32)

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        return depth

# ------------------------------------------------------------------------------------------------ #

class Marigold(DepthEstimator):
    """Configure and use Marigold        [dim](by https://github.com/prs-eth/Marigold)[reset]"""

    def _load_model(self) -> None:
        install("accelerate", "diffusers", "matplotlib")

        from diffusers import DiffusionPipeline

        log.info("Loading Depth Estimator model (Marigold)")
        self._model = DiffusionPipeline.from_pretrained(
            "prs-eth/marigold-v1-0",
            custom_pipeline="marigold_depth_estimation",
            torch_dtype=torch.float16,
            variant="fp16",
        ).to(self.device)

    def _estimate(self, image: numpy.ndarray) -> numpy.ndarray:
        return (1 - self._model(
            Image.fromarray(image),
            denoising_steps=10,
            ensemble_size=10,
            match_input_res=False,
            show_progress_bar=True,
            color_map=None,
            processing_res=792,
        ).depth_np)

    def _post_processing(self, depth: numpy.ndarray) -> numpy.ndarray:
        return depth

# ------------------------------------------------------------------------------------------------ #
