import os
import time
from typing import Self

import rich
from loguru import logger as log

# Don't log contiguous long paths
console = rich.get_console()
console.soft_wrap = True

class BrokenLogging:
    LOG_START = time.perf_counter()

    def __new__(cls) -> Self:
        if not hasattr(cls, "_singleton"):
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        self.make()

    @staticmethod
    def project() -> str:
        return os.getenv("BROKEN_APP_NAME", "Broken")

    @staticmethod
    def set_project(name: str, *, force: bool=False) -> None:
        if (BrokenLogging.project() == "Broken") or force:
            os.environ["BROKEN_APP_NAME"] = name

    def broken_format(self, data) -> str:
        when = (time.perf_counter() - BrokenLogging.LOG_START)
        data["when"] = f"{int(when//60)}'{when%60:06.3f}"
        return (
            f"\r│[dodger_blue3]{self.project()}[/dodger_blue3]├"
            "┤[green]{when}[/green]├"
            "┤[{level.icon}]{level:7}[/{level.icon}]"
            "│ ▸ {message}"
        ).format(**data)

    @property
    def log_level(self) -> str:
        return os.getenv("LOGLEVEL", "INFO").upper()

    @log_level.setter
    def log_level(self, level: str) -> None:
        os.environ["LOGLEVEL"] = level.upper()
        self.make()

    def make(self) -> None:
        log.remove()
        log.add(
            sink=rich.print,
            format=self.broken_format,
            level=os.getenv("LOGLEVEL", "INFO").upper(),
            colorize=False,
            backtrace=True,
            diagnose=True,
            catch=True,
        )
        self.level("TRACE", None, "dark_turquoise")
        self.level("DEBUG", None, "turquoise4")
        self.level("INFO", None, "bright_white")
        self.level("NOTE", 25, "bright_blue")
        self.level("TIP", 25, "dark_cyan")
        self.level("SUCCESS", None, "green")
        self.level("MINOR", 25, "grey42")
        self.level("SKIP", 25, "grey42")
        self.level("FIXME", 25, "cyan")
        self.level("TODO", 25, "dark_blue")
        self.level("WARNING", None, "yellow")
        self.level("ERROR", None, "red")
        self.level("CRITICAL", None, "red")

    def level(self, level: str, loglevel: int=0, color: str=None) -> None:
        """Create or update a loglevel `.{name.lower()}` on the logger, optional 'echo' argument"""
        def wraps_log(*args, echo=True) -> str:
            message = " ".join(map(str, args))
            if not echo:
                return message
            for line in message.splitlines():
                log.log(level, line)
            return message

        # Assign log function to logger. Workaround to set icon=color
        log.level(level, loglevel, icon=color)
        setattr(log, level.lower(), wraps_log)

BrokenLogging()
