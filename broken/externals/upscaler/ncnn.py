import io
import shutil
from abc import abstractmethod
from pathlib import Path
from subprocess import DEVNULL
from typing import Annotated, Literal

from PIL import Image
from PIL.Image import Image as ImageType
from pydantic import Field, field_validator
from typer import Option

from broken import (
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    Environment,
    denum,
    every,
    log,
    shell,
)
from broken.core.typerx import BrokenTyper
from broken.externals.upscaler import UpscalerBase


class UpscalerNCNN_Base(UpscalerBase):

    denoise: Annotated[int, Option("--denoise", "-n", min=0, max=3)] = \
        Field(3, ge=0)
    """Denoiser intensity, great for digital art, 'fake, uncanny' otherwise"""

    tile_size: Annotated[int, Option("--tile-size", "-t", min=0)] = \
        Field(0, ge=0, exclude=True)
    """Processing chunk size, increases VRAM and Speed, 0 is auto, must be >= 32"""

    tta: Annotated[bool, Option("--tta", "-x")] = \
        Field(False)
    """Enable test-time augmentation (Similar to SSAA) [red](8x SLOWER)[/]"""

    cpu: Annotated[bool, Option("--cpu", "-c")] = \
        Field(False, exclude=True)
    """Use CPU for processing instead of the GPU [yellow](SLOW)[/]"""

    gpu: Annotated[int, Option("--gpu", "-g", min=0)] = \
        Field(0, ge=0, exclude=True)
    """Use the Nth GPU in the system for processing"""

    load_threads: Annotated[int, Option("--load-threads", "-lt", min=1)] = \
        Field(1, ge=1, exclude=True)
    """Number of loading threads"""

    proc_threads: Annotated[int, Option("--proc-threads", "-pt", min=1)] = \
        Field(2, ge=1, exclude=True)
    """Number of processing threads"""

    save_threads: Annotated[int, Option("--save-threads", "-st", min=1)] = \
        Field(2, ge=1, exclude=True)
    """Number of saving threads"""

    @property
    def _lpc(self) -> str:
        return f"{self.load_threads}:{self.proc_threads}:{self.save_threads}"

    @field_validator("tile_size", mode="plain")
    def _validate_tile_size(cls, value):
        if not ((value == 0) or (value >= 32)):
            raise ValueError("Tile size must be 0 or >= 32 for NCNN Upscalers")
        return value

    # # Metadata for automatic downloads

    @staticmethod
    @abstractmethod
    def _download_url() -> str:
        """https://.../stuff-{platform}.zip"""
        ...

    @staticmethod
    @abstractmethod
    def _binary_name() -> str:
        ...

    def download(self) -> Path:
        BrokenPath.update_externals_path()
        if (binary := shutil.which(self._binary_name())):
            return BrokenPath.get(binary)
        EXECUTABLE = self._binary_name() + (".exe"*BrokenPlatform.OnWindows)
        return BrokenPath.make_executable(next(BrokenPath.get_external(self._download_url()).rglob(EXECUTABLE)))

    def _load_model(self):
        self.download()

# ------------------------------------------------------------------------------------------------ #

class Waifu2x(UpscalerNCNN_Base):
    """Configure and use Waifu2x    [dim](by https://github.com/nihui/waifu2x-ncnn-vulkan)[/]"""
    type: Annotated[Literal["waifu2x"], BrokenTyper.exclude()] = "waifu2x"

    class Model(str, BrokenEnum):
        Cunet = "models_cunet"
        Anime = "models_upconv_7_anime_style_art_rgb"
        Photo = "models_upconv_7_photo"

    model: Annotated[Model, Option("--model", "-m")] = Field(Model.Cunet)
    """The upscaling model to use"""

    @staticmethod
    def _download_url() -> str:
        release, tag = ("https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download", "20220728")
        return f"{release}/{tag}/waifu2x-ncnn-vulkan-{tag}-{BrokenPlatform.System.replace('linux', 'ubuntu')}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "waifu2x-ncnn-vulkan"

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in (allowed := {1, 2, 4, 8, 16, 32}):
            raise ValueError(f"Scale must be one of {allowed} for Waifu2x")
        return value

    @field_validator("denoise", mode="plain")
    def _validate_denoise(cls, value):
        if value not in (allowed := {-1, 0, 1, 2, 3}):
            raise ValueError(f"Denoise must be one of {allowed} for Waifu2x")
        return value

    def _upscale(self,
        input: ImageType, *,
        echo: bool=True,
        single_core: bool=False
    ) -> ImageType:
        with self.path_image() as output:
            with self.path_image(input) as input:
                shell(
                    self.download(),
                    "-i", input,
                    "-o", output,
                    every("-n", self.denoise),
                    every("-s", self.scale),
                    every("-t", self.tile_size),
                    "-g", (self.gpu if not self.cpu else -1),
                    "-j", self._lpc,
                    "-x"*self.tta,
                    # "-m", self.model.value, # Fixme: Doko?
                    single_core=single_core,
                    cwd=self.download().parent,
                    stderr=DEVNULL,
                    echo=echo,
                )
                return Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #

class Realesr(UpscalerNCNN_Base):
    """Configure and use RealESRGAN [dim](by https://github.com/xinntao/Real-ESRGAN)[/]"""
    type: Annotated[Literal["realesr"], BrokenTyper.exclude()] = "realesr"

    class Model(str, BrokenEnum):
        realesr_animevideov3    = "realesr_animevideov3"
        realesrgan_x4plus       = "realesrgan_x4plus"
        realesrgan_x4plus_anime = "realesrgan_x4plus_anime"
        realesrnet_x4plus       = "realesrnet_x4plus"

    model: Annotated[Model, Option("--model", "-m")] = Field(Model.realesr_animevideov3)
    """The upscaling model to use"""

    @staticmethod
    def _download_url() -> str:
        release, tag, version = ("https://github.com/xinntao/Real-ESRGAN/releases/download", "v0.2.5.0", "20220424")
        return f"{release}/{tag}/realesrgan-ncnn-vulkan-{version}-{BrokenPlatform.System.replace('linux', 'ubuntu')}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "realesrgan-ncnn-vulkan"

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in (allowed := {1, 2, 3, 4}):
            raise ValueError(f"Scale must be one of {allowed} for RealESRGAN")
        return value

    def _upscale(self,
        input: ImageType, *,
        echo: bool=True,
        single_core: bool=False
    ) -> ImageType:
        with self.path_image() as output:
            with self.path_image(input) as input:
                shell(
                    self.download(),
                    "-i", input,
                    "-o", output,
                    every("-s", self.scale),
                    every("-t", self.tile_size),
                    every("-g", self.gpu if not self.cpu else -1),
                    every("-n", self.model.name.replace("_", "-")),
                    "-j", self._lpc,
                    "-x"*self.tta,
                    stderr=DEVNULL,
                    single_core=single_core,
                    cwd=self.download().parent,
                    echo=echo,
                )
                return Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #

class Upscayl(UpscalerNCNN_Base):
    """Configure and use Upscayl    [dim](by https://github.com/upscayl/upscayl)[/]"""
    type: Annotated[Literal["upscayl"], BrokenTyper.exclude()] = "upscayl"

    class Model(str, BrokenEnum):
        DigitalArt      = "digital-art"
        HighFidelity    = "high-fidelity"
        Remacri         = "remacri"
        Ultramix        = "ultramix-balanced"
        Ultrasharp      = "ultrasharp"
        UpscaylLite     = "upscayl-lite"
        UpscaylStandard = "upscayl-standard"

    model: Annotated[Model, Option("--model", "-m")] = Field(Model.DigitalArt)
    """The upscaling model to use"""

    @staticmethod
    def _download_url() -> str:
        release, tag = ("https://github.com/upscayl/upscayl/releases/download", "2.15.0")
        platform = BrokenPlatform.System.replace("windows", "win").replace("macos", "mac")
        return f"{release}/v{tag}/upscayl-{tag}-{platform}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "upscayl-bin"

    def download(self) -> Path:
        if BrokenPlatform.OnLinux:
            Environment.add_to_path("/opt/Upscayl/resources/bin") # Ubuntu package
            Environment.add_to_path("/opt/upscayl/bin") # Arch Linux
        return UpscalerNCNN_Base.download(self)

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in (allowed := {2, 3, 4}):
            raise ValueError(f"Scale must be one of {allowed} for Upscayl")
        return value

    @field_validator("denoise", mode="plain")
    def _validate_denoise(cls, value):
        if value not in (allowed := {-1, 0, 1, 2, 3}):
            raise ValueError(f"Denoise must be one of {allowed} for Upscayl")
        return value

    def _upscale(self,
        input: ImageType, *,
        echo: bool=True,
        single_core: bool=False
    ) -> ImageType:

        # Warn non-commercial models
        if (self.model in (
            Upscayl.Model.Remacri,
            Upscayl.Model.Ultramix,
            Upscayl.Model.Ultrasharp,
        )):
            log.warn("[bold light_coral]• This upscaler model is non-commercial[/]")

        with self.path_image() as output:
            with self.path_image(input) as input:
                binary = self.download()
                shell(
                    binary,
                    "-i", input,
                    "-o", output,
                    "-m", "../models",
                    every("-s", self.scale),
                    every("-t", self.tile_size),
                    "-g", (self.gpu if not self.cpu else -1),
                    "-j", self._lpc,
                    "-x"*self.tta,
                    "-n", denum(self.model) + "-4x",
                    single_core=single_core,
                    stderr=DEVNULL,
                    echo=echo,
                )
                return Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #
