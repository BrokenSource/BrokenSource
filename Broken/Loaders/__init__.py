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

from Broken.Loaders.LoaderBytes import LoadableBytes, LoaderBytes
from Broken.Loaders.LoaderImage import LoadableImage, LoaderImage
from Broken.Loaders.LoaderString import LoadableString, LoaderString
