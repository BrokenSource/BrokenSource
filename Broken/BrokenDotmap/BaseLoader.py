from . import *

T = TypeVar("T")

@define
class DotmapLoader(ABC):

    # ------------------------------------------|
    # # Registration and initialization

    loaders        = set()
    __acronyms__   = {}

    def register(cls: Type[Self]) -> None:
        """Register a new loader"""
        DotmapLoader.loaders.add(cls)

        # Add loader acronyms
        for acronym in cls.acronyms():
            if acronym in DotmapLoader.__acronyms__:
                log.warning(f"Overriding loader acronym {acronym} with {cls}")
            DotmapLoader.__acronyms__[acronym] = cls

    # # Initialization methods

    def from_acronym(acronym: str) -> Optional[Self]:
        """Try finding a loader from its acronym"""
        return DotmapLoader.__acronyms__.get(acronym, None)

    def smart_find(key: str=None, value: Any=None) -> Optional[Self]:
        """Find a loader that can load the given key"""
        suffix = Path(key).suffix.replace(".", "").lower()

        if (loader := DotmapLoader.from_acronym(suffix)):
            return loader
        # for loader in DotmapLoader.loaders:
        #     if loader.load(value=value):
        #         return loader
        return None

    # ------------------------------------------|
    # # Proper methods

    value: Any = field(default=None)

    @staticmethod
    @abstractmethod
    def acronyms(self) -> Set[str]:
        ...

    @abstractmethod
    def load() -> T:
        ...

    @abstractmethod
    def dump(path: Path) -> None:
        ...

    # ------------------------------------------|

    # # Default implementations

    def __call__(self, value: Any) -> T:
        """Handle calling the instance as a function"""
        return type(self).load(value)

