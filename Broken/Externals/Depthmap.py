# pyright: reportMissingImports=false
import copy
import sys
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal, Optional, TypeAlias, Union

import numpy as np
import spaces
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
    BrokenModel,
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

# Fixme: Better place?
class _TempHelper:

    @staticmethod
    def normalize(
        array: np.ndarray,
        dtype: np.dtype=np.float32,
        min: Optional[float]=None,
        max: Optional[float]=None,
    ) -> np.ndarray:

        # Get the dtype information
        info = (np.iinfo(dtype) if np.issubdtype(dtype, np.integer) else np.finfo(dtype))

        # Optionally override target dtype min and max
        min = (info.min if (min is None) else min)
        max = (info.max if (max is None) else max)

        # Work with float64 as array might be low precision
        return np.interp(
            x=array.astype(np.float64),
            xp=(np.min(array), np.max(array)),
            fp=(min, max),
        ).astype(dtype)

    @staticmethod
    def image_hash(image: Union[ImageType, np.ndarray]) -> int:
        import xxhash
        return xxhash.xxh3_64_intdigest(image.tobytes())

# ------------------------------------------------------------------------------------------------ #

class DepthEstimatorBase(
    ExternalTorchBase,
    ExternalModelsBase,
    ABC
):
    _cache: DiskCache = PrivateAttr(default_factory=lambda: DiskCache(
        directory=BrokenPath.mkdir(Broken.PROJECT.DIRECTORIES.CACHE/"DepthEstimator"),
        size_limit=int(Environment.float("DEPTHMAP_CACHE_SIZE_MB", 50)*MiB),
    ))
    """DiskCache object for caching depth maps"""

    thicken: Annotated[bool, Option("--thicken", "-t", " /--raw")] = Field(True, exclude=True)
    """Extrude the edges to mitigate artifacts in DepthFlow"""

    class DTypeEnum(str, BrokenEnum):
        float64 = "float64"
        float32 = "float32"
        float16 = "float16"
        uint16  = "uint16"
        uint8   = "uint8"

    dtype: Annotated[DTypeEnum, Option("--dtype", "-d")] = Field(DTypeEnum.uint16)
    """The final data format to work, save the depthmap with"""

    @property
    def np_dtype(self) -> np.dtype:
        return getattr(np, self.dtype.value)

    @spaces.GPU(duration=15)
    def estimate(self,
        image: LoadableImage,
        cache: bool=True,
    ) -> np.ndarray[np.float32]:
        import gzip

        # Uniquely identify the image and current parameters
        image = LoadImage(image).convert("RGB")
        key: str = f"{hash(self)}{_TempHelper.image_hash(image)}"
        key: int = xxhash.xxh3_64_intdigest(key)

        # Estimate if not on cache
        if (not cache) or (depth := self._cache.get(key)) is None:
            self.load_torch()
            self.load_model()

            # Estimate and convert to target dtype
            depth = self._estimate(image)
            depth = _TempHelper.normalize(depth, dtype=self.np_dtype)

            # Save the array as a gzip compressed numpy file
            np.save(buffer := BytesIO(), depth, allow_pickle=False)
            self._cache.set(key, gzip.compress(buffer.getvalue()))
        else:
            # Load the compressed gzip numpy file from cache
            depth = np.load(BytesIO(gzip.decompress(depth)))

        # Optionally thicken the depth map array
        depth = _TempHelper.normalize(depth, dtype=np.float32, min=0, max=1)
        depth = (self._thicken(depth) if self.thicken else depth)
        return depth

    @abstractmethod
    def _estimate(self, image: np.ndarray) -> np.ndarray:
        """The implementation shall return a normalized numpy f32 array of the depth map"""
        ...

    @abstractmethod
    def _thicken(self, depth: np.ndarray) -> np.ndarray:
        return depth

    # # Command line interface

    @classmethod
    def cli(cls, typer: BrokenTyper, name: str) -> BrokenTyper:

        # Workaround to order the IO fields first
        class InputsOutputs(BrokenModel):
            input: Annotated[str, Option("--input", "-i")] = Field(None, exclude=True)
            """Path of the image or URL to estimate"""

            output: Annotated[Optional[Path], Option("--output", "-o")] = Field(None, exclude=True)
            """Path to save the depthmap, defaults to '(input).depth.png'"""

        # Todo: Common "Single • multi smart IO handler" class
        class CommandLine(cls, InputsOutputs):
            def _post(self):
                if (self.output is None):
                    self.output = Path(self.input).with_suffix(".depth.png")
                log.info(f"Estimating depthmap for {self.input}")
                depth = self.estimate(image=self.input)
                depth = _TempHelper.normalize(depth, dtype=self.dtype)
                Image.fromarray(depth).save(self.output)
                log.info(f"Depthmap saved to {self.output}")

        return (typer.command(
            target=CommandLine, name=name,
            description=cls.__doc__,
            post=CommandLine._post,
        ) or typer)

# ------------------------------------------------------------------------------------------------ #

class DepthAnythingBase(DepthEstimatorBase):
    class Model(str, BrokenEnum):
        Small = "small"
        Base  = "base"
        Large = "large"

    model: Annotated[Model, Option("--model", "-m")] = Field(Model.Small)
    """The model of DepthAnythingV2 to use"""

    _processor: Any = PrivateAttr(None)

    @property
    @abstractmethod
    def _huggingface_model(self) -> str:
        ...

    def _load_model(self) -> None:
        import transformers
        log.info(f"Loading Depth Estimator model ({self._huggingface_model})")
        if (self.model != self.Model.Small):
            log.warning("[bold light_coral]• This depth estimator model is licensed under CC BY-NC 4.0 (non-commercial)[/]")
        self._processor = BrokenCache.lru(transformers.AutoImageProcessor.from_pretrained)(self._huggingface_model, use_fast=False)
        self._model = BrokenCache.lru(transformers.AutoModelForDepthEstimation.from_pretrained)(self._huggingface_model)
        self._model.to(self.device)

    def _estimate(self, image: np.ndarray) -> np.ndarray:
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

    def _thicken(self, depth: np.ndarray) -> np.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        depth = gaussian_filter(input=depth, sigma=0.3)
        depth = maximum_filter(input=depth, size=5)
        return depth

class DepthAnythingV2(DepthAnythingBase):
    """Configure and use DepthAnythingV2 [dim](by https://github.com/DepthAnything/Depth-Anything-V2)[/]"""
    type: Annotated[Literal["depthanything2"], BrokenTyper.exclude()] = "depthanything2"

    indoor: Annotated[bool, Option("--indoor")] = Field(False)
    """Use the indoors fine-tuned metric model variant [bold dim](Not recommended for DepthFlow)[/]"""

    outdoor: Annotated[bool, Option("--outdoor")] = Field(False)
    """Use the outdoor fine-tuned metric model variant [bold dim](Not recommended for DepthFlow)[/]"""

    @property
    def _huggingface_model(self) -> str:
        if (self.indoor):
            return f"depth-anything/Depth-Anything-V2-Metric-Indoor-{self.model.value}-hf"
        elif (self.outdoor):
            return f"depth-anything/Depth-Anything-V2-Metric-Outdoor-{self.model.value}-hf"
        else:
            return f"depth-anything/Depth-Anything-V2-{self.model.value}-hf"

    def _thicken(self, depth: np.ndarray) -> np.ndarray:
        from scipy.ndimage import gaussian_filter, maximum_filter
        if (self.indoor or self.outdoor):
            depth = (np.max(depth) - depth)
        depth = gaussian_filter(input=depth, sigma=0.6)
        depth = maximum_filter(input=depth, size=5)
        return depth

# ------------------------------------------------------------------------------------------------ #

class DepthPro(DepthEstimatorBase):
    """Configure and use DepthPro        [dim](by https://github.com/apple/ml-depth-pro)[/]"""
    type: Annotated[Literal["depthpro"], BrokenTyper.exclude()] = "depthpro"

    _model: Any = PrivateAttr(None)
    _transform: Any = PrivateAttr(None)

    def _load_model(self) -> None:
        log.info("Loading Depth Estimator model (DepthPro)")
        install(package="depth_pro", pypi="git+https://github.com/apple/ml-depth-pro")

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

    def _estimate(self, image: np.ndarray) -> np.ndarray:

        # Infer, transfer to CPU, invert depth values
        depth = self._model.infer(self._transform(image))["depth"]
        depth = depth.detach().cpu().numpy().squeeze()
        depth = (np.max(depth) - depth)

        # Limit resolution to 1024 as there's no gains in interpoilation
        depth = np.array(Image.fromarray(depth).resize(BrokenResolution.fit(
            old=depth.shape, max=(1024, 1024),
            ar=(depth.shape[1]/depth.shape[0]),
        ), resample=Image.LANCZOS))

        return depth

    def _thicken(self, depth: np.ndarray) -> np.ndarray:
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
        install(package="timm", pypi="timm==0.6.7", args="--no-deps")

        log.info(f"Loading Depth Estimator model (ZoeDepth-{self.model.value})")
        self._model = BrokenCache.lru(torch.hub.load)(
            "isl-org/ZoeDepth", f"ZoeD_{self.model.value.upper()}",
            pretrained=True, trust_repo=True
        ).to(self.device)

    # Downscale for the largest component to be 512 pixels (Zoe precision), invert for 0=infinity
    def _estimate(self, image: np.ndarray) -> np.ndarray:
        depth = Image.fromarray(1 - DepthEstimatorBase.normalize(self._model.infer_pil(image)))
        new = BrokenResolution.fit(old=depth.size, max=(512, 512), ar=depth.size[0]/depth.size[1])
        return np.array(depth.resize(new, resample=Image.LANCZOS)).astype(np.float32)

    def _thicken(self, depth: np.ndarray) -> np.ndarray:
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
        install(package=("accelerate", "diffusers", "matplotlib"))

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

    def _estimate(self, image: np.ndarray) -> np.ndarray:
        return (1 - self._model(
            Image.fromarray(image),
            match_input_res=False,
            show_progress_bar=True,
            color_map=None,
        ).depth_np)

    def _thicken(self, depth: np.ndarray) -> np.ndarray:
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
