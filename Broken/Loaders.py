import contextlib
from abc import ABC, abstractmethod
from base64 import b64decode
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

import validators
from attr import define
from PIL import Image
from PIL.Image import Image as ImageType

import Broken
from Broken import BrokenCache

if TYPE_CHECKING:
    import numpy as np

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenLoader(ABC):

    def __new__(cls, *args, **kwargs) -> Optional[type]:
        return cls.load(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def load(value: Any=None, **kwargs) -> Optional[type]:
        ...

# ------------------------------------------------------------------------------------------------ #

@define
class LoadString(BrokenLoader):

    @staticmethod
    def load(value: Any=None) -> Optional[str]:
        if (not value):
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, bytes):
            return value.decode()

        if (path := Path(value)).exists():
            return path.read_text(encoding="utf-8")

        return None

LoadableString: TypeAlias = Union[str, bytes, Path]

# ------------------------------------------------------------------------------------------------ #

@define
class LoadBytes(BrokenLoader):

    @staticmethod
    def load(value: Any=None) -> Optional[bytes]:
        if (value is None):
            return None

        if isinstance(value, bytes):
            return value

        if isinstance(value, str):
            return value.encode()

        if (path := Path(value)).exists():
            return path.read_bytes()

        return None

LoadableBytes: TypeAlias = Union[bytes, str, Path, None]

# ------------------------------------------------------------------------------------------------ #

@define
class LoadImage(BrokenLoader):
    _cache = None

    @staticmethod
    def cache() -> Any:
        with contextlib.suppress(ImportError):
            LoadImage._cache = (LoadImage._cache or BrokenCache.requests(
                cache_name=Broken.BROKEN.DIRECTORIES.CACHE/"LoadImage.sqlite",
                expire_after=1800))
        return LoadImage._cache

    @staticmethod
    def load(value: Any=None) -> Optional[ImageType]:

        # No value to load
        if (value is None):
            return None

        # Passthrough image class
        if (value is ImageType):
            return value

        # Already an instance of Image
        if isinstance(value, ImageType):
            return value

        # Attempt to load from path
        if isinstance(value, Path):
            if (value.exists()):
                return Image.open(value)
            return None

        if isinstance(value, str):

            # Load from base64 generic type
            if (value.startswith(prefix := "base64:")):
                return Image.open(BytesIO(b64decode(value[len(prefix):])))

            # Attempt to load from URL
            if validators.url(value):
                import requests
                get = getattr(LoadImage.cache(), "get", requests.get)
                return Image.open(BytesIO(get(value).content))

            # Load from path, ignore too
            try:
                if (path := Path(value)).exists():
                    return Image.open(path)
            except OSError as error:
                if (error.errno != 36):
                    raise error

            return None

        # Load from bytes
        if isinstance(value, bytes):
            return Image.open(BytesIO(value))

        # Load from numpy array
        if ("numpy" in str(type(value))):
            return Image.fromarray(value)

        return None

LoadableImage: TypeAlias = Union[
    ImageType,
    Path,
    "np.ndarray",
    bytes,
    str
]

# ------------------------------------------------------------------------------------------------ #
