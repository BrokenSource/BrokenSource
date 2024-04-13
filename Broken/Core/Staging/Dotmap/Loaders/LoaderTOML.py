from . import *


class LoaderTOML(DotmapLoader):

    @staticmethod
    def acronyms() -> Set[str]:
        return {"toml"}

    def load(self) -> T:
        log.debug(f":: LoaderTOML.load() for value ({self.value})")

        if not self.value:
            return None

        elif isinstance(self.value, str):
            log.debug(f"  :: Using string")
            return BrokenDotmap(toml.loads(self.value))

        elif isinstance(self.value, dict):
            log.debug(f"  :: Using dictionary")
            return BrokenDotmap(self.value)

        elif isinstance(self.value, bytes):
            log.debug(f"  :: Using bytes")
            return BrokenDotmap(toml.loads(self.value.decode("utf-8")))

        elif BrokenPath.empty_file(self.value):
            log.debug(f"  :: Using empty file")
            return BrokenDotmap()

        elif BrokenPath.non_empty_file(self.value):
            log.debug(f"  :: Using non-empty file")
            return BrokenDotmap(toml.load(self.value))

        else:
            raise RuntimeError(f"Cannot load TOML from value {self.value}")

    def dump(self, path: Path):
        log.trace(f":: LoaderTOML.dump() to ({path})")
        path.write_text(toml.dumps(self.value))

DotmapLoader.register(LoaderTOML)
