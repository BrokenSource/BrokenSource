from typing import Any

from attrs import define


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
