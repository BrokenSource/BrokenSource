import tempfile
from pathlib import Path
from typing import Any, Self

from attrs import define

from Broken import BrokenEnum, Environment, log, shell


class BrokenProfilerEnum(BrokenEnum):
    """List of profilers"""
    cprofile      = "cprofile"
    # imports       = "imports"
    # pyinstrument  = "pyinstrument"


@define
class BrokenProfiler:
    name: str = "NONE"
    profiler: BrokenProfilerEnum = BrokenProfilerEnum.cprofile

    @property
    def label(self) -> str:
        return self.name.upper()

    def __attrs_post_init__(self):
        profiler = Environment.get(f"{self.label}_PROFILER", self.profiler)
        self.profiler = BrokenProfilerEnum.get(profiler)

    @property
    def enabled(self) -> bool:
        return Environment.flag(f"{self.label}_PROFILE", 0)

    @property
    def output(self) -> Path:
        return Path(tempfile.gettempdir())/f"{self.label}.prof"

    __profiler__: Any = None

    def __enter__(self) -> Self:
        if (not self.enabled):
            pass
        elif (self.profiler == BrokenProfilerEnum.cprofile):
            log.trace("Profiling with cProfile")
            import cProfile
            self.__profiler__ = cProfile.Profile()
            self.__profiler__.enable()
        return self

    def __exit__(self, *args) -> None:
        if (not self.enabled):
            return None

        if (self.profiler == BrokenProfilerEnum.cprofile):
            log.trace("Finishing cProfile")
            output = self.output.with_suffix(".prof")
            self.__profiler__.disable()
            self.__profiler__.dump_stats(output)
            try:
                shell("snakeviz", output)
            except KeyboardInterrupt:
                pass
            output.unlink()
