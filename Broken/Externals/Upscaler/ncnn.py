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

from Broken import (
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenTyper,
    denum,
    every,
    shell,
)
from Broken.Externals.Upscaler import UpscalerBase


class UpscalerNCNN_Base(UpscalerBase):
    denoise: Annotated[int, Option("--denoise", "-n", min=0, max=3,
        help="[bold yellow](🟡 Specific)[/] Denoiser intensity. Great for digital art, 'fake, uncanny' otherwise")] = \
        Field(3, gt=-1)

    tile_size: Annotated[int, Option("--tile-size", "-t", min=0,
        help="[bold yellow](🟡 Specific)[/] Processing chunk size, increases VRAM and Speed, 0 is auto, must be >= 32")] = \
        Field(0, gt=-1)

    tta: Annotated[bool, Option("--tta", "-x",
        help="[bold yellow](🟡 Specific)[/] Enable test-time augmentation (Similar to SSAA) [red](8x SLOWER)[/]")] = \
        Field(False)

    cpu: Annotated[bool, Option("--cpu", "-c",
        help="[bold yellow](🟡 Specific)[/] Use CPU for processing instead of the GPU [yellow](SLOW)[/]")] = \
        Field(False)

    gpu: Annotated[int, Option("--gpu", "-g", min=0,
        help="[bold yellow](🟡 Specific)[/] Use the Nth GPU for processing")] = \
        Field(0, gt=-1)

    load_threads: Annotated[int, Option("--load-threads", "-lt", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Load Threads")] \
        = Field(1, gt=0)

    proc_threads: Annotated[int, Option("--proc-threads", "-pt", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Process Threads")] \
        = Field(2, gt=0)

    save_threads: Annotated[int, Option("--save-threads", "-st", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Saving Threads")] \
        = Field(2, gt=0)

    @property
    def _lpc(self) -> str:
        return f"{self.load_threads}:{self.proc_threads}:{self.save_threads}"

    def _single_core(self):
        """Make the process only use one random core"""
        import os
        import random
        import resource
        core = random.choice(range(os.cpu_count()))
        os.sched_setaffinity(0, {core})
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))

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
        models_cunet = "models_cunet"
        models_upconv_7_anime_style_art_rgb = "models_upconv_7_anime_style_art_rgb"
        models_upconv_7_photo = "models_upconv_7_photo"

    model: Annotated[Model, Option("--model", "-m",
        help="(🔵 Special ) Model to use for Waifu2x")] = \
        Field(Model.models_cunet)

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
                    "-g", self.gpu if not self.cpu else -1,
                    "-j", self._lpc,
                    "-x"*self.tta,
                    # "-m", self.model.value, # Fixme: Doko?
                    preexec_fn=(self._single_core if single_core else None),
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

    model: Annotated[Model, Option("--model", "-m",
        help="(🔵 Special ) Model to use for RealESRGAN")] = \
        Field(Model.realesr_animevideov3)

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
                    preexec_fn=(self._single_core if single_core else None),
                    cwd=self.download().parent,
                    echo=echo,
                )
                return Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #

class Upscayl(UpscalerNCNN_Base):
    """Configure and use Upscayl    [dim](by https://github.com/upscayl/upscayl)[/]"""
    type: Annotated[Literal["upscayl"], BrokenTyper.exclude()] = "upscayl"

    class Model(str, BrokenEnum):
        realesrgan_x4plus       = "realesrgan-x4plus"
        realesrgan_x4fast       = "realesrgan-x4fast"
        realesrgan_x4plus_anime = "realesrgan-x4plus-anime"
        ultramix_balanced       = "ultramix_balanced"
        ultrasharp              = "ultrasharp"
        remacri                 = "remacri"

    model: Annotated[Model, Option("--model", "-m",
        help="(🔵 Special ) Model to use for Upscayl")] = \
        Field(Model.realesrgan_x4plus_anime)

    @staticmethod
    def _download_url() -> str:
        release, tag = ("https://github.com/upscayl/upscayl/releases/download", "2.11.5")
        platform = BrokenPlatform.System.replace("windows", "win").replace("macos", "mac")
        return f"{release}/v{tag}/upscayl-{tag}-{platform}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "upscayl-bin"

    def download(self) -> Path:
        if BrokenPlatform.OnLinux:
            BrokenPath.add_to_path("/opt/Upscayl/resources/bin") # Ubuntu package
            BrokenPath.add_to_path("/opt/upscayl/bin") # Arch Linux
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
        with self.path_image() as output:
            with self.path_image(input) as input:
                binary = self.download()
                shell(
                    binary,
                    "-i", input,
                    "-o", output,
                    "-m", "../models",
                    every("-z", self.scale),
                    every("-s", self.scale),
                    every("-t", self.tile_size),
                    "-g", (self.gpu if not self.cpu else -1),
                    "-j", self._lpc,
                    "-x"*self.tta,
                    "-n", denum(self.model),
                    preexec_fn=(self._single_core if single_core else None),
                    stderr=DEVNULL,
                    echo=echo,
                )
                return Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #
