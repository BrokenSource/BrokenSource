import contextlib
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Generator,
    Optional,
    Tuple,
    Type,
    Union,
)

import PIL
import PIL.Image
from PIL.Image import Image
from pydantic import BaseModel, ConfigDict, Field

from Broken.Loaders import LoadableImage, LoaderImage


class BrokenUpscaler(BaseModel, ABC):
    model_config = ConfigDict(validate_assignment=True)
    width:  int = Field(default=0, gt=-1)
    height: int = Field(default=0, gt=-1)
    scale:  int = Field(default=2, gt=0)
    passes: int = Field(default=1, gt=0)

    # Temporary images processing
    format: str = Field(default="jpg")
    quality: int = Field(default=95)

    def output_size(self, width: int, height: int) -> Tuple[int, int]:
        """Calculate the final output size after upscaling some input size"""

        # Forces final resolution
        if (self.width and self.height):
            return (self.width, self.height)

        # Upscales input
        ratio = self.scale**self.passes
        return (int(width*ratio), int(height*ratio))

    @contextlib.contextmanager
    def path_image(self, image: Optional[LoadableImage]=None) -> Generator[Path, None, None]:
        image = LoaderImage(image)
        try:
            file = Path(tempfile.NamedTemporaryFile(
                delete=image is None,
                suffix=f".{self.format}").name
            )
            if isinstance(image, Image):
                image.save(file, quality=self.quality)
            elif image is Image:
                pass
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
            image.info.get("transparency", None)
        ))):
            _, _, _, alpha = image.split()
            alpha = alpha.resize(target)

        # Convert to RGB for working
        image = image.convert("RGB")

        # Upscale core logic
        with self.path_image(image) as temp_input:
            for _ in range(self.passes):
                image.save(temp_input, quality=self.quality)
                image = self._upscale(image)

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
    def _upscale(self, image: Image) -> Image:
        """The upscaler's proper implementation"""
        ...

# -------------------------------------------------------------------------------------------------|

class PillowUpscaler(BrokenUpscaler):
    def _upscale(self, image: Image) -> Image:
        return image.resize(self.output_size(*image.size), PIL.Image.LANCZOS)

# -------------------------------------------------------------------------------------------------|

from Broken.Externals.Upscaler.ncnn import RealEsrgan, Waifu2x

# -------------------------------------------------------------------------------------------------|
