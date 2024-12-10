import io
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

import PIL
import validators
from attr import define
from PIL.Image import Image

import Broken
from Broken.Loaders import BrokenLoader
from Broken.Types import URL

if TYPE_CHECKING:
    import numpy

@define
class LoaderImage(BrokenLoader):
    _cache = None

    @staticmethod
    def cache() -> Any:
        try:
            import requests_cache
            if not LoaderImage._cache:
                LoaderImage._cache = requests_cache.CachedSession(
                    Broken.BROKEN.DIRECTORIES.CACHE/"LoaderImage.sqlite",
                    expire_after=1800
                )
        except ImportError:
            return None

        return LoaderImage._cache

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[Image]:
        if value is None:
            return None

        if isinstance(value, Image):
            return value

        if (value is Image):
            return value

        if isinstance(value, bytes):
            return PIL.Image.open(io.BytesIO(value), **kwargs)

        if ("numpy" in str(type(value))):
            return PIL.Image.fromarray(value, **kwargs)

        if (path := Path(value).expanduser().resolve()).exists():
            return PIL.Image.open(path, **kwargs)

        if validators.url(value):
            import requests
            get = getattr(LoaderImage.cache(), "get", requests.get)
            return PIL.Image.open(io.BytesIO(get(value).content), **kwargs)

        return None

LoadableImage: TypeAlias = Union[Image, Path, URL, "numpy.ndarray", bytes]
