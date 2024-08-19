import io
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

import PIL
import validators
from attr import define
from PIL.Image import Image

import Broken
from Broken import log
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
                )
        except ImportError:
            return None

        return LoaderImage._cache

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[Image]:
        if value is None:
            return None

        if isinstance(value, Image):
            log.debug("Loading already an Instance of Image")
            return value

        if value is Image:
            log.debug("Loading already an Class of Image")
            return value

        if isinstance(value, bytes):
            log.debug("Loading Image from Bytes")
            return PIL.Image.open(io.BytesIO(value), **kwargs)

        if ("numpy" in str(type(value))):
            log.debug("Loading Image from Numpy Array")
            return PIL.Image.fromarray(value, **kwargs)

        if (path := Path(value).expanduser().resolve()).exists():
            log.debug(f"Loading Image from Path ({path})")
            return PIL.Image.open(path, **kwargs)

        if validators.url(value):
            log.debug(f"Loading Image from URL ({value})")
            import requests
            get = getattr(LoaderImage.cache(), "get", requests.get)
            return PIL.Image.open(io.BytesIO(get(value).content), **kwargs)

        return None

LoadableImage: TypeAlias = Union[Image, Path, URL, "numpy.ndarray", bytes, None]
