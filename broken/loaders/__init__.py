from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from attr import define


@define
class BrokenLoader(ABC):

    def __new__(cls, *args, **kwargs) -> Optional[Type]:
        return cls.load(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def load(value: Any=None, **kwargs) -> Optional[Type]:
        ...

from broken.loaders.bytes import LoadableBytes, LoaderBytes
from broken.loaders.image import LoadableImage, LoaderImage
from broken.loaders.string import LoadableString, LoaderString
