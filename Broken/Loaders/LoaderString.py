from pathlib import Path
from typing import Any, Optional, TypeAlias, Union

from attr import define

from Broken import BrokenPath, log
from Broken.Loaders import BrokenLoader


@define
class LoaderString(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[str]:
        if not value:
            return ""

        if isinstance(value, str):
            log.debug(f"Loading String from String {value}")
            return value

        if isinstance(value, bytes):
            log.debug("Loading String from Bytes")
            return value.decode(encoding="utf-8")

        if (path := BrokenPath.get(value)).exists():
            log.debug(f"Loading String from Path ({path})")
            return path.read_text(encoding="utf-8")

        return None

LoadableString: TypeAlias = Union[str, bytes, Path, None]
