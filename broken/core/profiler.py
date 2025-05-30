import contextlib
import tempfile
from pathlib import Path
from typing import Any, Self

from attr import define, field

from broken import Environment
from broken.core import shell


@define
class profiler:
    name: str = field(converter=str.upper)

    @property
    def _name(self) -> str:
        return self.name.upper()

    @property
    def enabled(self) -> bool:
        return Environment.flag(f"{self._name}_PROFILE", 0)

    @property
    def profiler(self) -> str:
        return Environment.get(f"{self._name}_PROFILER", "cprofile").lower()

    @property
    def output(self) -> Path:
        return Path(tempfile.gettempdir())/f"{self._name}.prof"

    _profiler: Any = None

    def __call__(self, method) -> Any:
        def wrapper(*a, **k):
            with self:
                return method(*a, **k)
        return wrapper

    def __enter__(self) -> Self:
        if (not self.enabled):
            pass
        elif (self.profiler == "cprofile"):
            import cProfile
            self._profiler = cProfile.Profile()
            self._profiler.enable()
        else:
            raise ValueError(f"Unknown profiler: {self.profiler}")
        return self

    def __exit__(self, *args) -> None:
        if (not self.enabled):
            return None
        if (self.profiler == "cprofile"):
            self._profiler.disable()
            self._profiler.dump_stats(self.output)
            with contextlib.suppress(KeyboardInterrupt):
                shell("snakeviz", self.output)
            with contextlib.suppress(Exception):
                self.output.unlink()
