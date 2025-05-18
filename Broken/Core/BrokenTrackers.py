from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from attr import Factory, define, field
from dotmap import DotMap

if TYPE_CHECKING:
    import arrow

@define
class SameTracker:
    """Doumo same desu. If a value is the same, returns True, else updates it and returns False
    • Useful on ignoring expensive calls where parameters doesn't changes"""
    value: Any = None

    def __call__(self, value: Any=True) -> bool:
        if self.value != value:
            self.value = value
            return False
        return True

@define
class OnceTracker:
    """Returns False the first time it's called, never nest style: `if once/already(): return`"""
    _first: bool = False

    def __call__(self) -> bool:
        if (not self._first):
            self._first = True
            return False
        return True

@define
class PlainTracker:
    value: Any = None

    def __call__(self, set: bool=None) -> bool:
        """Returns value if None else sets it"""
        if (set is not None):
            self.value = set
        return self.value

@define
class FileTracker:
    file: Path = field(converter=Path)
    retention: DotMap = Factory(lambda: DotMap(days=1, hours=0))

    def __attrs_post_init__(self):
        self.file.touch()

        # Initialize new or empty trackers
        if (not self.file.read_text("utf-8")):
            self._first = True
            self.update()

    _first: bool = False

    @property
    def first(self) -> bool:
        """True if initializing the tracker for the first time"""
        return self._first

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        return None

    @property
    def last(self) -> "arrow.Arrow":
        """How long it's been since the last run"""
        import arrow
        return arrow.get(self.file.read_text("utf-8"))

    @property
    def sleeping(self, granularity: tuple[str]=("day")) -> str:
        """How long it's been since the last run, for printing purposes"""
        return self.last.humanize(only_distance=True, granularity=granularity)

    def trigger(self, update: bool=False) -> bool:
        """True if it's been more than 'self.retention' since the last run"""
        import arrow
        trigger = (self.last.shift(**self.retention) < arrow.utcnow())
        if (trigger and update):
            self.update()
        return trigger

    def update(self, **shift: dict) -> None:
        import arrow
        time = arrow.utcnow().shift(**(shift or {}))
        self.file.write_text(str(time), "utf-8")
