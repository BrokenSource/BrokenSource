import shutil
from abc import abstractmethod
from pathlib import Path
from subprocess import DEVNULL
from typing import Literal

import PIL
import PIL.Image
from PIL.Image import Image
from pydantic import Field, field_validator

from Broken import BrokenPath, BrokenPlatform, shell
from Broken.Externals.Upscaler import BrokenUpscaler


class UpscalerNCNN_Base(BrokenUpscaler):
    denoise:   int  = Field(default=0, gt= 0, alias="n")
    tile_size: int  = Field(default=0, gt=-1, alias="t")
    gpu:       int  = Field(default=0, gt=-1, alias="g")
    tta:       bool = Field(default=False, alias="x")
    cpu:       bool = Field(default=False, alias="c")

    # Special
    load_threads: int = Field(default=1, gt=0, alias="l")
    proc_threads: int = Field(default=2, gt=0, alias="p")
    save_threads: int = Field(default=2, gt=0, alias="s")

    @property
    def _lpc(self) -> str:
        return f"{self.load_threads}:{self.proc_threads}:{self.save_threads}"

    # Make the process only use one random core
    def preexec_fn(self):
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
        if (binary := shutil.which(self._binary_name())):
            return BrokenPath(binary)
        DOWNLOAD = self._base_download().format(BrokenPlatform.Name.replace("linux", "ubuntu"))
        EXECUTABLE = self._binary_name() + (".exe"*BrokenPlatform.OnWindows)
        return BrokenPath.make_executable(next(BrokenPath.get_external(DOWNLOAD).rglob(EXECUTABLE)))

# -------------------------------------------------------------------------------------------------|

class Waifu2x(UpscalerNCNN_Base):
    model: Literal[
        "models-cunet",
        "models-upconv_7_anime_style_art_rgb",
        "models-upconv_7_photo",
    ] = Field(default="models-cunet", alias="m")

    @staticmethod
    def _base_download() -> str:
        return "https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20220728/waifu2x-ncnn-vulkan-20220728-{}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "waifu2x-ncnn-vulkan"

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in {1, 2, 4, 8, 16, 32}:
            raise ValueError("Scale must be 1, 2, 4, 8, 16, or 32 for Waifu2x")
        return value

    @field_validator("denoise", mode="plain")
    def _validate_denoise(cls, value):
        if value not in {-1, 0, 1, 2, 3}:
            raise ValueError("Denoise must be -1, 0, 1, 2, or 3 for Waifu2x")
        return value

    def _upscale(self, input: Image, *, echo: bool=True) -> Image:
        with self.path_image() as output:
            with self.path_image(input) as input:
                shell(
                    self.download(),
                    "-i", input,
                    "-o", output,
                    "-n", self.denoise,
                    "-s", self.scale,
                    "-t", self.tile_size,
                    "-g", self.gpu if not self.cpu else -1,
                    "-j", self._lpc,
                    "-x"*self.tta,
                    # "-m", self.model.value, # Fixme: Doko?
                    stderr=DEVNULL,
                    preexec_fn=self.preexec_fn,
                    cwd=self.download().parent,
                    echo=echo,
                )
                return PIL.Image.open(output)

# -------------------------------------------------------------------------------------------------|

class RealEsrgan(UpscalerNCNN_Base):
    model: Literal[
        "realesr-animevideov3",
        "realesrgan-x4plus",
        "realesrgan-x4plus-anime",
        "realesrnet-x4plus",
    ] = Field(default="realesr-animevideov3")

    @staticmethod
    def _base_download() -> str:
        return "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-{}.zip"

    @staticmethod
    def _binary_name() -> str:
        return "realesrgan-ncnn-vulkan"

    @field_validator("scale", mode="plain")
    def _validate_scale(cls, value):
        if value not in {1, 2, 3, 4}:
            raise ValueError("Scale must be 2, 3, or 4 for RealESRGAN")
        return value

    def _upscale(self, input: Image, *, echo: bool=True) -> Image:
        with self.path_image() as output:
            with self.path_image(input) as input:
                shell(
                    self.download(),
                    "-i", input,
                    "-o", output,
                    "-s", self.scale,
                    "-t", self.tile_size,
                    "-g", self.gpu if not self.cpu else -1,
                    "-j", self._lpc,
                    "-x"*self.tta,
                    stderr=DEVNULL,
                    cwd=self.download().parent,
                    echo=echo,
                )
                return PIL.Image.open(output)

# -------------------------------------------------------------------------------------------------|
