import io
import shutil
from abc import abstractmethod
from pathlib import Path
from subprocess import DEVNULL
from typing import Annotated

import PIL
import PIL.Image
import typer
from PIL.Image import Image
from pydantic import Field, field_validator

from Broken import BrokenEnum, BrokenPath, BrokenPlatform, every, shell
from Broken.Externals.Upscaler import BrokenUpscaler


class UpscalerNCNN_Base(BrokenUpscaler):
    denoise: Annotated[int, typer.Option("--denoise", "-n", min=0, max=3,
        help="[bold yellow](🟡 Specific)[reset] Denoiser intensity. Great for digital art, 'fake, uncanny' otherwise")] = \
        Field(default=3, gt=-1)

    tile_size: Annotated[int, typer.Option("--tile-size", "-t", min=0,
        help="[bold yellow](🟡 Specific)[reset] Processing chunk size, increases VRAM and Speed, 0 is auto, must be >= 32")] = \
        Field(default=0, gt=-1)

    tta: Annotated[bool, typer.Option("--tta", "-x",
        help="[bold yellow](🟡 Specific)[reset] Enable test-time augmentation (Similar to SSAA) [red](8x SLOWER)[reset]")] = \
        Field(default=False)

    cpu: Annotated[bool, typer.Option("--cpu", "-c",
        help="[bold yellow](🟡 Specific)[reset] Use CPU for processing instead of the GPU [yellow](SLOW)[reset]")] = \
        Field(default=False)

    gpu: Annotated[int, typer.Option("--gpu", "-g", min=0,
        help="[bold yellow](🟡 Specific)[reset] Use the Nth GPU for processing")] = \
        Field(default=0, gt=-1)

    load_threads: Annotated[int, typer.Option("--load-threads", "-lt", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Load Threads")] \
        = Field(default=1, gt=0)

    proc_threads: Annotated[int, typer.Option("--proc-threads", "-pt", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Process Threads")] \
        = Field(default=2, gt=0)

    save_threads: Annotated[int, typer.Option("--save-threads", "-st", min=1,
        help="[bold green](🟢 Advanced)[bold yellow] Number of Saving Threads")] \
        = Field(default=2, gt=0)

    @property
    def _lpc(self) -> str:
        return f"{self.load_threads}:{self.proc_threads}:{self.save_threads}"

    def preexec_fn(self):
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
    def _base_download() -> str:
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
        DOWNLOAD = self._base_download().format(BrokenPlatform.Name.replace("linux", "ubuntu"))
        EXECUTABLE = self._binary_name() + (".exe"*BrokenPlatform.OnWindows)
        return BrokenPath.make_executable(next(BrokenPath.get_external(DOWNLOAD).rglob(EXECUTABLE)))

    def _load_model(self):
        self.download()

# ------------------------------------------------------------------------------------------------ #

class Waifu2x(UpscalerNCNN_Base):
    """Configure and use Waifu2x    [dim](by https://github.com/nihui/waifu2x-ncnn-vulkan)[reset]"""

    class Model(str, BrokenEnum):
        models_cunet = "models_cunet"
        models_upconv_7_anime_style_art_rgb = "models_upconv_7_anime_style_art_rgb"
        models_upconv_7_photo = "models_upconv_7_photo"

    model: Annotated[Model, typer.Option("--model", "-m", hidden=True,
        help="(🔵 Special ) Model to use for Waifu2x")] = \
        Field(default=Model.models_cunet)

    @staticmethod
    def _base_download() -> str:
        return "https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20220728/waifu2x-ncnn-vulkan-20220728-{}.zip"

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

    def _upscale(self, input: Image, *, echo: bool=True, single_core: bool=False) -> Image:
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
                    stderr=DEVNULL,
                    preexec_fn=(self.preexec_fn if single_core else None),
                    cwd=self.download().parent,
                    echo=echo,
                )
                return PIL.Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #

class Realesr(UpscalerNCNN_Base):
    """Configure and use RealESRGAN [dim](by https://github.com/xinntao/Real-ESRGAN)[reset]"""

    class Model(str, BrokenEnum):
        realesr_animevideov3    = "realesr_animevideov3"
        realesrgan_x4plus       = "realesrgan_x4plus"
        realesrgan_x4plus_anime = "realesrgan_x4plus_anime"
        realesrnet_x4plus       = "realesrnet_x4plus"

    model: Annotated[Model, typer.Option("--model", "-m", hidden=True,
        help="(🔵 Special ) Model to use for RealESRGAN")] = \
        Field(default=Model.realesr_animevideov3)

    @staticmethod
    def _base_download() -> str:
        return "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-{}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "realesrgan-ncnn-vulkan"

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in (allowed := {1, 2, 3, 4}):
            raise ValueError(f"Scale must be one of {allowed} for RealESRGAN")
        return value

    def _upscale(self, input: Image, *, echo: bool=True, single_core: bool=False) -> Image:
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
                    preexec_fn=(self.preexec_fn if single_core else None),
                    cwd=self.download().parent,
                    echo=echo,
                )
                return PIL.Image.open(io.BytesIO(output.read_bytes()))

# ------------------------------------------------------------------------------------------------ #
