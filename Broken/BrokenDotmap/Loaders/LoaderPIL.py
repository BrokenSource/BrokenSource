from . import *


class DotmapLoaderImage(DotmapLoader):

    @staticmethod
    def acronyms() -> Set[str]:
        return {"image"}

    @staticmethod
    def extensions() -> Set[str]:
        return {".png", ".jpg", ".jpeg", ".bmp"}

    def load(self):
        print(f"• LoaderImage.load() for value ({self.value})")

        if isinstance(type(self), PIL.Image.Image):
            print(f"  :: Using PIL.Image")
            return self.value

        elif isinstance(self.value, Path):
            print(f"  :: Using path")
            return PIL.Image.open(self.value)

        elif BrokenUtils.have_import("requests") and validate.url(self.value):
            print(f"  :: Using requests")
            return PIL.Image.open(io.BytesIO(requests.get(self.value).content))

        elif BrokenUtils.have_import("numpy") and isinstance(self.value, numpy.ndarray):
            print(f"  :: Using numpy")
            return PIL.Image.fromarray(self.value)

        elif isinstance(self.value, bytes):
            print(f"  :: Using bytes")
            return PIL.Image.open(io.BytesIO(self.value))

        else:
            raise RuntimeError(f"Cannot load image from value {self.value}")

    def dump(self, path: Path) -> None:
        print(f":: LoaderImage.dump() @ ({path}) - {self.value}")
        self.value.save(path)

    def can_load(key: str, value: str=None) -> bool:

        # Already an PIL image
        if isinstance(value, PIL.Image.Image):
            return True

        # Known image sufix
        if Path(key).suffix.lower() in DotmapLoaderImage.extensions():
            return True

        # We can load url with png extensions
        if isinstance(value, str):
            if validate.url(value):
                return DotmapLoaderImage.can_load(key=value)

DotmapLoader.register(DotmapLoaderImage)
