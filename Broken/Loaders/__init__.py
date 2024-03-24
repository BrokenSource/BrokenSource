from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Optional
from typing import Type

from attr import define


@define
class BrokenLoader(ABC):

    def __new__(cls, *args, **kwargs) -> Optional[Type]:
        return cls.load(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def load(value: Any=None, **kwargs) -> Optional[Type]:
        ...
