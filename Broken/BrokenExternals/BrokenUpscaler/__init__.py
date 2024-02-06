from .. import *


@define
class BrokenUpscaler(BrokenExternal, ABC):
    width:  int = field(default=0, converter=int)
    height: int = field(default=0, converter=int)

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

    # # Implementations

    @abstractmethod
    def __upscale__(self, input: Path, output: Path):
        """Proper upscale method"""
        ...

    def upscale(self,
        input:  Union[Path, URL, Image],
        output: Union[Path, URL, None]=Image,
        *,
        width:  int=None,
        height: int=None,
    ) -> Option[Path, Image]:
        """
        Upscale some input image given by its path or Image object.

        Args:
            `input`:  The input image to upscale
            `output`: The output path to save or `Image` class for a Image object

        Advanced:
            `width`, `height`:
                After the proper upscaling, resize the image to the given size,
                if the input image or the output path is this size, skip the upscaling

        Returns:
            The upscaled image as a PIL Image object if `output` is `Image`, else the output Path
        """
        width  = self.width  or width
        height = self.height or height
        target = (width, height) if (width and height) else None
        self.__validate__()

        # Load a Image out of the input or output, else Empty image
        Empty = PIL.Image.new("RGB", (1, 1))
        iimage = BrokenUtils.load_image(input)  or Empty
        oimage = BrokenUtils.load_image(output) or Empty

        # No need to upscaled if already on target size
        if (oimage.size == target):
            log.success(f"Already upscaled to target size ({width}, {height}): {input}")
            if output is Image:
                return oimage
            return output
        if (iimage.size == target):
            log.success(f"Already upscaled to target size ({width}, {height}): {input}")
            if output is Image:
                return iimage
            return output

        # Upscale the image
        with self.temp_image(input) as temp_input:
            with self.temp_image(output) as temp_output:

                # Upscale once then on top of itself for each pass
                for _ in range(self.passes):
                    self.__upscale__(input=temp_input, output=temp_output)
                    input = temp_output

                # Return the Path of the Image
                if isinstance(output, Path):
                    oimage = PIL.Image.open(temp_output)
                    oimage = oimage if not target else oimage.resize(target, PIL.Image.LANCZOS)
                    oimage.save(output, quality=95)
                    return output

                # Return an Image object
                output = PIL.Image.open(temp_output)
                output = output if not target else output.resize(target, PIL.Image.LANCZOS)
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
    ) -> Path:
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
            file = BrokenPath.true_path(file.name)

            if isinstance(image, Image):
                image.save(file, quality=95)
            elif image is Image:
                pass
            elif Path(image).exists():
                shutil.copyfile(image, file)

            yield file


from .BrokenNCNN import *
