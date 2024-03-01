from . import *


class DotmapLoaderImage(DotmapLoader):

    @staticmethod
    def acronyms() -> Set[str]:
        return {"image", "png", "jpg", "jpeg", "bmp"}

    def load(self) -> T:
        log.debug(f"• LoaderImage.load() for value ({self.value})")

        if not self.value:
            return None

        elif isinstance(self.value, Image):
            log.debug(f"  :: Using PIL.Image")
            return self.value

        elif isinstance(self.value, str) and Path(self.value).exists():
            log.debug(f"  :: Using path")
            return PIL.Image.open(self.value)

        elif isinstance(self.value, Path):
            log.debug(f"  :: Using path")
            return PIL.Image.open(self.value)

        elif BrokenUtils.have_import("requests") and validators.url(self.value):
            log.debug(f"  :: Using requests")
            return PIL.Image.open(io.BytesIO(requests.get(self.value).content))

        elif BrokenUtils.have_import("numpy") and isinstance(self.value, numpy.ndarray):
            log.debug(f"  :: Using numpy")
            return PIL.Image.fromarray(self.value)

        elif isinstance(self.value, bytes):
            log.debug(f"  :: Using bytes")
            return PIL.Image.open(io.BytesIO(self.value))

        return None

    def dump(self, path: Path) -> None:
        log.debug(f":: LoaderImage.dump() @ ({path}) - {self.value}")
        self.value.save(path)

DotmapLoader.register(DotmapLoaderImage)
