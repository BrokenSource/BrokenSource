from . import *


@define
class LoaderImage(BrokenLoader):
    _cache = None

    @staticmethod
    def cache() -> Any:
        try:
            import requests_cache
            if not LoaderImage._cache:
                LoaderImage._cache = requests_cache.CachedSession(
                    BROKEN.DIRECTORIES.CACHE/f"LoaderImage.sqlite",
                )
        except ImportError:
            return None

        return LoaderImage._cache

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[Image]:
        if not value:
            return None

        elif isinstance(value, Image):
            return value

        elif (path := BrokenPath(value, valid=True)):
            return PIL.Image.open(path, **kwargs)

        elif validators.url(value) and LoaderImage.cache():
            return PIL.Image.open(io.BytesIO(LoaderImage.cache().get(value).content), **kwargs)

        elif validators.url(value):
            return PIL.Image.open(io.BytesIO(requests.get(value).content), **kwargs)

        elif isinstance(value, numpy.ndarray):
            return PIL.Image.fromarray(value, **kwargs)

        elif isinstance(value, bytes):
            return PIL.Image.open(io.BytesIO(value), **kwargs)

        return None
