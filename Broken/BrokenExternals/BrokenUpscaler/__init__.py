from .. import *


@define
class BrokenUpscaler(BrokenExternal, ABC):
    scale:  int = field(default=2, converter=int)
    width:  int = field(default=0, converter=int)
    height: int = field(default=0, converter=int)
    passes: int = field(default=1, converter=int)

    @property
    def s(self) -> int:
        return self.scale
    @s.setter
    def s(self, value: int):
        self.scale = value

    @property
    def w(self) -> int:
        return self.width
    @w.setter
    def w(self, value: int):
        self.width = value

    @property
    def h(self) -> int:
        return self.height
    @h.setter
    def h(self, value: int):
        self.height = value

    def output_size(self, width: int, height: int):
        """Get the output size after upscaling some input size"""
        if (self.width and self.height):
            return (self.width, self.height)

        # We upscale current times ratio at each pass
        upscale_ratio = self.scale**self.passes

        return (width*upscale_ratio, height*upscale_ratio)

    # # Implementations

    @abstractmethod
    def __upscale__(self, input: Path, output: Path, *, echo: bool=True):
        """Proper upscale method"""
        ...

    def upscale(self,
        input:  Union[Path, URL, Image],
        output: Union[Path, URL, None]=Image,
        *,
        echo: bool=True
    ) -> Option[Path, Image]:
        """
        Upscale some input image given by its path or Image object.

        Args:
            `input`:  The input image to upscale
            `output`: The output path to save or `Image` class for a Image object
            `echo`:   Log the upscale process or commands

        Returns:
            The upscaled image as a PIL Image object if `output` is `Image`, else the output Path
        """
        self.__validate__()

        # Load a Image out of the input or output, else Empty image
        Empty  = PIL.Image.new("RGB", (1, 1))
        iimage = BrokenUtils.load_image(input ) or Empty
        oimage = BrokenUtils.load_image(output) or Empty

        # Get the upscaled size of the input image
        target = self.output_size(iimage.width, iimage.height)

        # No need to upscaled if already on target size
        if (oimage.size == target):
            log.success(f"Already upscaled to target size ({self.width}, {self.height}): {input}")
            if output is Image:
                return oimage
            return output
        if (iimage.size == target):
            log.success(f"Already upscaled to target size ({self.width}, {self.height}): {input}")
            if output is Image:
                return iimage
            return output

        # Upscale the image
        with self.temp_image(input) as temp_input:
            with self.temp_image(output) as temp_output:

                # Upscale once then on top of itself for each pass
                for _ in range(self.passes):
                    self.__upscale__(input=temp_input, output=temp_output, echo=echo)
                    input = temp_output

                # Return the Path of the Image
                if isinstance(output, Path):
                    oimage = PIL.Image.open(temp_output)
                    oimage = oimage.resize(target, PIL.Image.LANCZOS)
                    oimage.save(output, quality=95)
                    return output

                # Return an Image object
                output = PIL.Image.open(temp_output)
                output = output.resize(target, PIL.Image.LANCZOS)
                return output

    @abstractmethod
    def __validate__(self):
        """
        Validate parameters for the current upscaler
        """

    @contextlib.contextmanager
    def temp_image(self,
        image: Union[Path, URL, Image],
        format="jpg"
    ) -> Generator[Path, None, None]:
        """
        Get a temporary Path to a Image
        • Saves an Image object or copies a Path to a temporary file
        • Yields the Path to the temporary file

        Args:
            `image`:  The image to save or copy
            `format`: The format of the temporary file

        Returns:
            The Path to the temporary file, deleted on context exit
        """
        image = BrokenUtils.load_image(image) or image

        with tempfile.NamedTemporaryFile(suffix=f".{format}") as file:
            file = BrokenPath(file.name)

            if isinstance(image, Image):
                image.save(file, quality=95)
            elif image is Image:
                pass
            elif Path(image).exists():
                shutil.copyfile(image, file)

            yield file


from .BrokenNCNN import *
