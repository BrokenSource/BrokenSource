import io
from pathlib import Path
from Broken.Logging import log
from typing import Any, Optional, Union

import numpy
import PIL
import validators
from attr import define
from PIL.Image import Image

from Broken import BROKEN
from Broken.Base import BrokenPath
from Broken.Types import URL

from . import BrokenLoader


@define
class LoaderImage(BrokenLoader):
    _cache = None

    @staticmethod
    def cache() -> Any:
        try:
            import requests_cache
            if not LoaderImage._cache:
                LoaderImage._cache = requests_cache.CachedSession(
                    BROKEN.DIRECTORIES.CACHE/"LoaderImage.sqlite",
                )
        except ImportError:
            return None

        return LoaderImage._cache

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[Image]:
        if value is None:
            return None

        elif isinstance(value, Image):
            log.debug(f"Loading Image from Image")
            return value

        elif isinstance(value, numpy.ndarray):
            log.debug(f"Loading Image from Numpy Array")
            return PIL.Image.fromarray(value, **kwargs)

        elif (path := BrokenPath(value, valid=True)):
            log.debug(f"Loading Image from Path ({path})")
            return PIL.Image.open(path, **kwargs)

        elif validators.url(value):
            log.debug(f"Loading Image from URL ({value})")

            if LoaderImage.cache():
                return PIL.Image.open(io.BytesIO(LoaderImage.cache().get(value).content), **kwargs)

            import requests
            return PIL.Image.open(io.BytesIO(requests.get(value).content), **kwargs)

        elif isinstance(value, bytes):
            log.debug(f"Loading Image from Bytes")
            return PIL.Image.open(io.BytesIO(value), **kwargs)

        return None

LoadableImage = Union[Image, Path, URL, numpy.ndarray, bytes, None]
