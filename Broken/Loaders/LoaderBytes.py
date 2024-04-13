from pathlib import Path
from typing import Any, Optional, Union

from attr import define
from loguru import logger as log

from Broken import BrokenPath

from . import BrokenLoader


@define
class LoaderBytes(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[bytes]:
        if not value:
            return b""

        elif isinstance(value, bytes):
            log.debug("Loading Bytes from Bytes")
            return value

        elif isinstance(value, str):
            log.debug("Loading Bytes from String")
            return value.encode()

        elif (path := BrokenPath(value).valid()):
            log.debug(f"Loading Bytes from Path ({path})")
            return path.read_bytes()

        return None

LoadableBytes = Union[bytes, str, Path, None]
