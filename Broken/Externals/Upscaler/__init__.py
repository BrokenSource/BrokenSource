import contextlib
import shutil
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Literal, Optional, TypeAlias, Union

from PIL import Image
from PIL.Image import Image as ImageType
from pydantic import ConfigDict, Field
from typer import Option

from Broken import BrokenEnum, BrokenResolution, BrokenTyper, denum
from Broken.Externals import ExternalModelsBase
from Broken.Loaders import LoadableImage, LoadImage


class UpscalerBase(ExternalModelsBase, ABC):
    model_config = ConfigDict(validate_assignment=True)

    width: Annotated[int, Option("--width", "-w", min=0,
        help="[bold red](🔴 Basic   )[/] Upscaled image width, automatic on height aspect ratio if 0, forced if both are set")] = \
        Field(0, gt=-1)

    height: Annotated[int, Option("--height", "-h", min=0,
        help="[bold red](🔴 Basic   )[/] Upscaled image height, automatic on width aspect ratio if 0, forced if both are set")] = \
        Field(0, gt=-1)

    scale: Annotated[int, Option("--scale", "-s", min=1,
        help="[bold red](🔴 Basic   )[/] Single pass upscale factor. For precision, over-scale and force width and/or height")] = \
        Field(2, gt=0)

    passes: Annotated[int, Option("--passes", "-p", min=1,
        help="[bold red](🔴 Basic   )[/] Number of sequential upscale passes. Gets exponentially slower and bigger images")] = \
        Field(1, gt=0)

    class Format(str, BrokenEnum):
        PNG = "png"
        JPG = "jpg"

    format: Annotated[Format, Option("--format", "-f",
        help="[bold red](🔴 Basic   )[/] Temporary image processing format. (PNG: Lossless, slow) (JPG: Good enough, faster)")] = \
        Field(Format.JPG)

    quality: Annotated[int, Option("--quality", "-q", min=0, max=100,
        help="[bold red](🔴 Basic   )[/] Temporary image processing 'PIL.Image.save' quality used on --format")] = \
        Field(95, ge=0, le=100)

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
                suffix=f".{denum(self.format)}").name,
                delete=(image is None),
            )
            if image is ImageType:
                pass
            elif isinstance(image, ImageType):
                image.save(file, quality=self.quality)
            elif isinstance(image, Path) and Path(image).exists():
                shutil.copy(image, file)
            yield file
        finally:
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
            The upscaled image as a PIL Image object if `output` is `Image`, else the output Path
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

# ------------------------------------------------------------------------------------------------ #

class PillowUpscaler(UpscalerBase):
    type: Annotated[Literal["pillow"], BrokenTyper.exclude()] = "pillow"

    def _load_model(self):
        pass

    def _upscale(self, image: ImageType) -> ImageType:
        return image.resize(self.output_size(*image.size), Image.LANCZOS)

class NoUpscaler(UpscalerBase):
    type: Annotated[Literal["none"], BrokenTyper.exclude()] = "none"

    def _load_model(self):
        pass

    def upscale(self, *args, **kwargs) -> ImageType:
        return args[0]

    def _upscale(self, image: ImageType) -> ImageType:
        return image

# ------------------------------------------------------------------------------------------------ #

from Broken.Externals.Upscaler.ncnn import Realesr, Upscayl, Waifu2x

BrokenUpscaler: TypeAlias = Union[
    NoUpscaler,
    PillowUpscaler,
    Realesr,
    Upscayl,
    Waifu2x,
]

# ------------------------------------------------------------------------------------------------ #
