import os
import time
from typing import Self

import rich
from attr import define
from loguru import logger as log

# Don't log contiguous long paths
console = rich.get_console()
console.soft_wrap = True

@define
class BrokenLogging:
    LOG_START = time.perf_counter()

    def __new__(cls) -> Self:
        if not hasattr(cls, "_singleton"):
            cls._singleton = super().__new__(cls)
            cls._singleton._init()
        return cls._singleton

    @staticmethod
    def project() -> str:
        return os.environ.get("BROKEN_APP_NAME", "Broken")

    @staticmethod
    def set_project(name: str, *, force: bool=False) -> None:
        if (BrokenLogging.project() == "Broken") or force:
            os.environ["BROKEN_APP_NAME"] = name

    def broken_format(self, data) -> str:
        data["ms"] = int((time.perf_counter() - BrokenLogging.LOG_START)*1000)
        return (
            f"\r│[dodger_blue3]{self.project().ljust(10)}[/dodger_blue3]├"
            "┤[green]{ms:>4}ms[/green]├"
            "┤[{level.icon}]{level:7}[/{level.icon}]"
            "│ ▸ {message}"
        ).format(**data)

    def _init(self) -> None:
        log.remove()
        log.add(
            rich.print,
            format=self.broken_format,
            level=os.environ.get("LOGLEVEL", "INFO").upper(),
            colorize=False,
            backtrace=True,
            diagnose=True,
            catch=True,
        )

        # Override default levels with capitalized version for rich color
        # and add optional (echo: bool) argument
        self.level("TRACE", None, "dark_turquoise")
        self.level("DEBUG", None, "turquoise4")
        self.level("INFO", None, "bright_white")
        self.level("SUCCESS", None, "green")
        self.level("MINOR", 25, "grey42")
        self.level("SKIP", 25, "grey42")
        self.level("FIXME", 25, "cyan")
        self.level("TODO", 25, "dark_blue")
        self.level("WARNING", None, "yellow")
        self.level("ERROR", None, "red")
        self.level("CRITICAL", None, "red")

    def level(self, level: str, loglevel: int=0, color: str=None) -> Self:
        """Create a new loglevel `.{name.lower()}` on the logger"""
        def wraps_log(*args, echo=True, **kwargs) -> str:
            message = " ".join(map(str, args))
            if not echo:
                return message
            for line in message.splitlines():
                log.log(level, line, **kwargs)
            return message

        # Assign log function to logger. Workaround to set icon=color
        log.level(level, loglevel, icon=color)
        setattr(log, level.lower(), wraps_log)
        return self

BrokenLogging()
