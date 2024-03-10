from .. import *


@define
class BrokenLoader(ABC):

    def __new__(cls, *args, **kwargs) -> Optional[Type]:
        return cls.load(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def load(value: Any=None, **kwargs) -> Optional[Type]:
        ...

from .LoaderBytes import *
from .LoaderPIL import *
from .LoaderString import *
