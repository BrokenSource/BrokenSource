from pathlib import Path
from typing import Any, Optional, TypeAlias, Union

from attr import define

from Broken import BrokenPath

from . import BrokenLoader


@define
class LoaderBytes(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[bytes]:
        if not value:
            return b""

        if isinstance(value, bytes):
            return value

        if isinstance(value, str):
            return value.encode()

        if (path := BrokenPath.get(value)).exists():
            return path.read_bytes()

        return None

LoadableBytes: TypeAlias = Union[bytes, str, Path, None]
