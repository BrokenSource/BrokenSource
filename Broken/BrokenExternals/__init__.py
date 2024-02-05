from .. import *


class BrokenExternal(ABC):

    @property
    @abstractmethod
    def binary(self) -> str:
        ...

class BrokenExternalManager:
    def get(self, external: Type[BrokenExternal]) -> BrokenExternal:
        ...

from .BrokenFFmpeg import *
from .BrokenUpscaler import *
