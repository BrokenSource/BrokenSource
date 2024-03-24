import io
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

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

        elif isinstance(value, numpy.ndarray):
            return PIL.Image.fromarray(value, **kwargs)

        elif isinstance(value, Image):
            return value

        elif (path := BrokenPath(value, valid=True)):
            return PIL.Image.open(path, **kwargs)

        elif validators.url(value):
            if LoaderImage.cache():
                return PIL.Image.open(io.BytesIO(LoaderImage.cache().get(value).content), **kwargs)

            import requests
            return PIL.Image.open(io.BytesIO(requests.get(value).content), **kwargs)

        elif isinstance(value, bytes):
            return PIL.Image.open(io.BytesIO(value), **kwargs)

        return None

LoadableImage = Union[Image, Path, URL, numpy.ndarray, bytes, None]
