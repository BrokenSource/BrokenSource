from pathlib import Path
from typing import Any, Optional, Union

from attr import define

from Broken import BrokenPath, log
from Broken.Loaders import BrokenLoader


@define
class LoaderString(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[str]:
        if not value:
            return ""

        elif isinstance(value, str):
            log.debug(f"Loading String from String {value}")
            return value

        elif isinstance(value, bytes):
            log.debug("Loading String from Bytes")
            return value.decode(encoding="utf-8")

        elif (path := BrokenPath(value).valid()):
            log.debug(f"Loading String from Path ({path})")
            return path.read_text(encoding="utf-8")

        return None

LoadableString = Union[str, bytes, Path, None]
