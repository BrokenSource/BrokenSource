import contextlib
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated, Generator, Optional, Tuple, Type, Union

import PIL
import PIL.Image
import typer
from PIL.Image import Image
from pydantic import ConfigDict, Field

from Broken import BrokenEnum, BrokenResolution, denum
from Broken.Externals import ExternalModelsBase
from Broken.Loaders import LoadableImage, LoaderImage


class BrokenUpscaler(ExternalModelsBase, ABC):
    model_config = ConfigDict(validate_assignment=True)

    width: Annotated[int, typer.Option("--width", "-w", min=0,
        help="[bold red](🔴 Basic   )[reset] Upscaled image width, automatic on height aspect ratio if 0, forced if both are set")] = \
        Field(default=0, gt=-1)

    height: Annotated[int, typer.Option("--height", "-h", min=0,
        help="[bold red](🔴 Basic   )[reset] Upscaled image height, automatic on width aspect ratio if 0, forced if both are set")] = \
        Field(default=0, gt=-1)

    scale: Annotated[int, typer.Option("--scale", "-s", min=1,
        help="[bold red](🔴 Basic   )[reset] Single pass upscale factor. For precision, over-scale and force width and/or height")] = \
        Field(default=2, gt=0)

    passes: Annotated[int, typer.Option("--passes", "-p", min=1,
        help="[bold red](🔴 Basic   )[reset] Number of sequential upscale passes. Gets exponentially slower and bigger images")] = \
        Field(default=1, gt=0)

    class Format(BrokenEnum):
        PNG = "png"
        JPG = "jpg"

    format: Annotated[Format, typer.Option("--format", "-f",
        help="[bold red](🔴 Basic   )[reset] Temporary image processing format. (PNG: Lossless, slow) (JPG: Good enough, faster)")] = \
        Field(default="jpg")

    quality: Annotated[int, typer.Option("--quality", "-q", min=0, max=100,
        help="[bold red](🔴 Basic   )[reset] Temporary image processing 'PIL.Image.save' quality used on --format")] = \
        Field(default=95, gt=0)

    def output_size(self, width: int, height: int) -> Tuple[int, int]:
        """Calculate the final output size after upscaling some input size"""
        return BrokenResolution.fit(
            old=(width, height),
            new=(self.width or None, self.height or None),
            scale=self.scale**self.passes,
            ar=(width/height)
        )

    @contextlib.contextmanager
    def path_image(self, image: Optional[LoadableImage]=None) -> Generator[Path, None, None]:
        image = LoaderImage(image)
        try:
            # Note: No context because NTFS only allows one fd per path
            file = Path(tempfile.NamedTemporaryFile(
                suffix=f".{denum(self.format)}").name,
                delete=(image is None),
            )
            if image is Image:
                pass
            elif isinstance(image, Image):
                image.save(file, quality=self.quality)
            elif isinstance(image, Path) and Path(image).exists():
                shutil.copy(image, file)
            yield file
        finally:
            file.unlink()

    def upscale(self,
        image: LoadableImage,
        output: Union[Path, Type[Image]]=Image,
        **config
    ) -> Union[Path, Type[Image]]:
        """
        Upscale some input image given by its path or Image object.

        Args:
            input:  The input image to upscale
            output: The output path to save or `Image` class for a Image object

        Returns:
            The upscaled image as a PIL Image object if `output` is `Image`, else the output Path
        """

        # Convenience: Direct configs
        for key, val in config.items():
            if hasattr(self, key):
                setattr(self, key, val)

        # Only valid output for str is Path
        if isinstance(output, str):
            output = Path(output)

        # Input image must be a valid image
        if not (image := LoaderImage(image)):
            raise ValueError("Invalid input Image for upscaling")

        # Calculate expected output size
        target = self.output_size(*image.size)

        # Optimization: Return if output matches target
        if isinstance(output, Path) and output.exists():
            if (PIL.Image.open(output).size == target):
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
            image = image.resize(target, PIL.Image.LANCZOS)

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
    def _upscale(self, image: Image, **config) -> Image:
        """The upscaler's proper implementation"""
        ...

# ------------------------------------------------------------------------------------------------ #

class PillowUpscaler(BrokenUpscaler):
    def _load_model(self):
        pass

    def _upscale(self, image: Image) -> Image:
        return image.resize(self.output_size(*image.size), PIL.Image.LANCZOS)

class NoUpscaler(BrokenUpscaler):
    def _load_model(self):
        pass

    def upscale(self, *args, **kwargs) -> Image:
        return args[0]

    def _upscale(self, image: Image) -> Image:
        return image

# ------------------------------------------------------------------------------------------------ #

from Broken.Externals.Upscaler.ncnn import Realesr, Waifu2x

# ------------------------------------------------------------------------------------------------ #
