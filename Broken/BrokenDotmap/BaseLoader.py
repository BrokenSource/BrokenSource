from . import *

T = TypeVar("T")

@attrs.define
class DotmapLoader(ABC):

    # ------------------------------------------|
    # # Registration and initialization

    loaders        = set()
    __acronyms__   = {}
    __extensions__ = {}

    def register(cls: Type[Self]) -> None:
        """Register a new loader"""
        DotmapLoader.loaders.add(cls)

        # Add loader acronyms
        for acronym in cls.acronyms():
            if acronym in DotmapLoader.__acronyms__:
                log.warning(f"Overriding loader acronym {acronym} with {cls}")
            DotmapLoader.__acronyms__[acronym] = cls

        # Add loader extensions
        for extension in cls.extensions():
            if extension in DotmapLoader.__extensions__:
                log.warning(f"Overriding loader extension {extension} with {cls}")
            DotmapLoader.__extensions__[extension] = cls

    # # Initialization methods

    def from_acronym(acronym: str) -> Optional[Self]:
        """Try finding a loader from its acronym"""
        return DotmapLoader.__acronyms__.get(acronym, None)

    def from_extension(extension: str) -> Optional[Self]:
        return DotmapLoader.__extensions__.get(extension, None)

    def smart_find(key: str, value: Any=None, acronym: str=None) -> Optional[Self]:
        """Find a loader that can load the given key"""
        if (loader := DotmapLoader.from_acronym(acronym)):
            return loader
        if (loader := DotmapLoader.from_extension(key)):
            return loader
        for loader in DotmapLoader.loaders:
            if loader.can_load(key=key, value=value):
                return loader
        return None

    # ------------------------------------------|
    # # Must implement own methods

    # Self values
    value: T = attrs.field(default=None)

    @staticmethod
    @abstractmethod
    def acronyms(self) -> Set[str]:
        ...

    @staticmethod
    @abstractmethod
    def extensions(self) -> Set[str]:
        ...

    @abstractmethod
    def load(self) -> T:
        ...

    @abstractmethod
    def dump(self, path: Path) -> None:
        ...

    @abstractmethod
    def can_load(key: str, value: Any=None) -> bool:
        ...

    # ------------------------------------------|

    # # Default implementations

    def __call__(self, value: Any) -> Self:
        """Handle calling the instance as a function"""
        self.value = value
        return self

