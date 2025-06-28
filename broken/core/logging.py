import sys
import time
from typing import Callable

import rich

from broken import Environment, Runtime

# ------------------------------------------------------------------------------------------------ #
# Optimization: Don't import asyncio, could break stuff

if Environment.flag("LOGURU_NO_ASYNCIO", 1):
    class _FakeAsyncio:
        get_running_loop = lambda: None
    asyncio = sys.modules.pop("asyncio", None)
    sys.modules["asyncio"] = _FakeAsyncio

    from loguru import logger as log

    if (asyncio is not None):
        sys.modules["asyncio"] = asyncio
    else:
        sys.modules.pop("asyncio")

from loguru import logger as log

# ------------------------------------------------------------------------------------------------ #

# Don't log contiguous long paths
console = rich.get_console()
console.soft_wrap = True

class BrokenLogging:
    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"{cls.__name__} class shouldn't be instantiated")

    @staticmethod
    def project() -> str:
        return Environment.get("BROKEN_APP_NAME", "Broken")

    @staticmethod
    def set_project(name: str) -> None:
        Environment.setdefault("BROKEN_APP_NAME", name)

    @classmethod
    def format(cls, data: dict) -> str:
        when = time.absolute()
        data["time"] = f"{int(when//60)}'{(when%60):06.3f}"
        data["project"] = cls.project()

        # Simpler logging for non UTF or workflows
        if Runtime.GitHub or Environment.flag("SIMPLE_LOGGING", 0):
            return ("[{project}][{time}][{level:5}] {message}").format(**data)

        elif Environment.flag("PLAIN_LOGGING", 0):
            return ("[{level:5}] {message}").format(**data)

        return (
            f"│[dodger_blue3]{cls.project()}[/]├"
            "┤[green]{time}[/]├"
            "┤[{level.icon}]{level:5}[/{level.icon}]│ "
            "▸ {message}"
        ).format(**data)

    @staticmethod
    def sink() -> Callable:
        if Runtime.GitHub:
            return print
        return rich.print

    @classmethod
    def reset(cls) -> None:
        log.remove()
        log.add(
            sink=cls.sink(),
            format=cls.format,
            level=Environment.get("LOGLEVEL", "INFO").upper(),
            colorize=False,
            backtrace=True,
            diagnose=True,
            catch=True,
        )
        cls._make_level("TRACE", None, "dark_turquoise")
        cls._make_level("DEBUG", None, "turquoise4")
        cls._make_level("INFO",  None, "bright_white")
        cls._make_level("NOTE",  25,   "bright_blue")
        cls._make_level("TIP",   25,   "dark_cyan")
        cls._make_level("OK",    25,   "green")
        cls._make_level("MINOR", 25,   "grey42")
        cls._make_level("SKIP",  25,   "grey42")
        cls._make_level("FIXME", 25,   "cyan")
        cls._make_level("TODO",  25,   "dark_blue")
        cls._make_level("WARN",  25,   "yellow")
        cls._make_level("ERROR", None, "red")
        cls._make_level("CRIT",  25,   "red")

    @classmethod
    def _make_level(cls, level: str, loglevel: int=0, color: str=None) -> None:
        """Create or update a loglevel `.{name.lower()}` on the logger"""
        def wrapper(
            *args: str,
            echo: bool=True,
        ) -> str:
            message = " ".join(map(str, args))
            if not echo:
                return message
            for line in message.splitlines():
                log.log(level, line)
            return message

        # Assign log function to logger. Workaround to set icon=color
        log.level(level, loglevel, icon=color)
        setattr(log, level.lower(), wrapper)

BrokenLogging.reset()
