from pathlib import Path
from typing import Any, Optional, TypeAlias, Union

from attr import define

from Broken.Loaders import BrokenLoader


@define
class LoaderString(BrokenLoader):

    @staticmethod
    def load(value: Any=None) -> Optional[str]:
        if (not value):
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, bytes):
            return value.decode(encoding="utf-8")

        if (path := Path(value)).exists():
            return path.read_text(encoding="utf-8")

        return None

LoadableString: TypeAlias = Union[str, bytes, Path]
