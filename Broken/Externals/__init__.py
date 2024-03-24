from abc import ABC
from abc import abstractmethod
from typing import Type


class BrokenExternal(ABC):

    @property
    @abstractmethod
    def binary(self) -> str:
        ...

class BrokenExternalManager:
    def get(self, external: Type[BrokenExternal]) -> BrokenExternal:
        ...
