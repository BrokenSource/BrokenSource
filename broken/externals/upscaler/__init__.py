from __future__ import annotations

import contextlib
import shutil
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Literal, Optional, TypeAlias, Union

from loguru import logger
from PIL import Image
from PIL.Image import Image as ImageType
from pydantic import ConfigDict, Field
from typer import Option

from broken.enumx import BrokenEnum
from broken.externals import ExternalModelsBase
from broken.loaders import LoadableImage, LoadImage
from broken.model import BrokenModel
from broken.resolution import BrokenResolution
from broken.typerx import BrokenTyper
from broken.utils import denum


class UpscalerBase(ExternalModelsBase, ABC):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    width: Annotated[Optional[int], Option("--width", "-w", min=0)] = Field(None, gt=-1)
    """Upscaled image width, automatic on height's aspect ratio if None"""

    height: Annotated[Optional[int], Option("--height", "-h", min=0)] = Field(None, gt=-1)
    """Upscaled image height, automatic on width aspect ratio if None"""

    scale: Annotated[int, Option("--scale", "-s", min=1)] = Field(2, gt=0)
    """Upscale factor for each pass"""

    passes: Annotated[int, Option("--passes", "-p", min=1)] = Field(1, gt=0)
    """Number of upscaling passes. Exponentially slower and larger images"""

    class Format(str, BrokenEnum):
        PNG = "png"
        JPG = "jpg"

    format: Annotated[Format, Option("--format", "-f")] = Field(Format.JPG)
    """Intermediate image processing format"""

    quality: Annotated[int, Option("--quality", "-q", min=0, max=100)] = Field(95, ge=0, le=100)
    """Intermediate image processing 'PIL.Image.save' quality used on --format"""

    def output_size(self, width: int, height: int) -> tuple[int, int]:
        """Calculate the final output size after upscaling some input size"""
        return BrokenResolution.fit(
            old=(width, height),
            new=(self.width or None, self.height or None),
            scale=(self.scale**self.passes),
            ar=(width/height)
        )

    @contextlib.contextmanager
    def path_image(self, image: Optional[LoadableImage]=None) -> Iterable[Path]:
        image = LoadImage(image)
        try:
            # Note: No context because NTFS only allows one fd per path
            file = Path(tempfile.NamedTemporaryFile(
                suffix=f".{denum(self.format)}",
                delete=(image is None),
            ).name)
            if image is ImageType:
                pass
            elif isinstance(image, ImageType):
                image.save(file, quality=self.quality)
            elif isinstance(image, Path) and Path(image).exists():
                shutil.copy(image, file)
            yield file
        finally:
            with contextlib.suppress(FileNotFoundError):
                file.unlink()

    def upscale(self,
        image: LoadableImage,
        output: Union[Path, ImageType]=ImageType,
        **config
    ) -> Union[Path, ImageType]:
        """
        Upscale some input image given by its path or Image object.

        Args:
            input:  The input image to upscale
            output: The output path to save or `Image` class for a Image object

        Returns:
            The upscaled image as a PIL Image object if `output` is `ImageType`, else the output Path
        """

        # Convenience: Direct configs
        for (key, val) in config.items():
            if hasattr(self, key):
                setattr(self, key, val)

        # Input image must be a valid image
        if not (image := LoadImage(image)):
            raise ValueError("Invalid input Image for upscaling")

        # Only valid output for str is Path
        if isinstance(output, str):
            output = Path(output)

        # Calculate expected output size
        target = self.output_size(*image.size)

        # Optimization: Return if output matches target
        if isinstance(output, Path) and output.exists():
            if (Image.open(output).size == target):
                return output

        # Optimization: Return if input matches target
        if (target == image.size):
            return image

        # If the image has transparency: Split in RGB+A, upscale RGB,
        # resize A to target resolution, merge it back later
        if (transparent := any((
            image.mode == "RGBA",
            image.info.get("transparency", None),
        )) and (not isinstance(self, NoUpscaler))):
            _, _, _, alpha = image.split()
            alpha = alpha.resize(target)

        # Convert to RGB for working
        image = image.convert("RGB")

        # Upscale core logic
        with self.path_image(image) as temp_input:
            for _ in range(self.passes):
                image.save(temp_input, quality=self.quality)
                image = self._upscale(image, **config)

            # Resize to match the expected final size
            image = image.resize(target, Image.LANCZOS)

            # Merge the alpha layer
            if transparent:
                image = image.convert("RGBA")
                image.putalpha(alpha)

            # Save or return the image
            if isinstance(output, Path):
                image.save(output, quality=self.quality)
                return output
            return image

    @abstractmethod
    def _upscale(self, image: ImageType, **config) -> ImageType:
        """The upscaler's proper implementation"""
        ...

    # # Command line interface

    @classmethod
    def cli(cls, typer: BrokenTyper, name: str) -> BrokenTyper:

        # Workaround to order the IO fields first
        class InputsOutputs(BrokenModel):
            input: Annotated[str, Option("--input", "-i")] = Field(None, exclude=True)
            """Path of the image or URL to upscale"""

            output: Annotated[Optional[Path], Option("--output", "-o")] = Field(None, exclude=True)
            """Path to save the upscaled image, defaults to '(input)-upscaled.ext'"""

        # Todo: Common "Single • multi smart IO handler" class
        class CommandLine(cls, InputsOutputs):
            def _post(self):
                input = Path(self.input)
                if (self.output is None):
                    self.output = input.with_stem(f"{input.stem}-upscaled")
                upscaled = self.upscale(image=input, output=self.output)
                logger.info(f"Saved upscaled image to {upscaled}")

        return (typer.command(
            target=CommandLine, name=name,
            description=cls.__doc__,
            post=CommandLine._post,
        ) or typer)

# ---------------------------------------------------------------------------- #

class PillowUpscaler(UpscalerBase):
    type: Annotated[Literal["pillow"], BrokenTyper.exclude()] = "pillow"

    def _load_model(self):
        pass

    def _upscale(self, image: ImageType) -> ImageType:
        return image.resize(self.output_size(*image.size), Image.LANCZOS)

class NoUpscaler(UpscalerBase):
    type: Annotated[Literal["none"], BrokenTyper.exclude()] = "none"

    scale: int = 1

    def _load_model(self):
        pass

    def _upscale(self, image: ImageType) -> ImageType:
        return image

# ---------------------------------------------------------------------------- #

from broken.externals.upscaler.ncnn import Realesr, Upscayl, Waifu2x

BrokenUpscaler: TypeAlias = Union[
    UpscalerBase,
    NoUpscaler,
    PillowUpscaler,
    Realesr,
    Upscayl,
    Waifu2x,
]

# ---------------------------------------------------------------------------- #
