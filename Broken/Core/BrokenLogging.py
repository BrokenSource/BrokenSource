import os
import textwrap
import time
from collections.abc import Callable

import rich
from loguru import logger as log

from Broken import Runtime
from Broken.Core import BrokenSingleton

# Don't log contiguous long paths
console = rich.get_console()
console.soft_wrap = True

class BrokenLogging(BrokenSingleton):
    def __init__(self):
        self.reset()

    @staticmethod
    def project() -> str:
        return os.getenv("BROKEN_APP_NAME", "Broken")

    @staticmethod
    def set_project(name: str, *, force: bool=False) -> None:
        if (BrokenLogging.project() == "Broken") or force:
            os.setenv("BROKEN_APP_NAME", name)

    def format(self, data: dict) -> str:
        when = time.absolute()
        data["time"] = f"{int(when//60)}'{(when%60):06.3f}"
        data["project"] = self.project()

        # Simpler logging for non utf8 or workflows
        if Runtime.GitHub or (os.getenv("SIMPLE_LOGGING", "0") == "1"):
            return ("[{project}][{time}][{level:7}] {message}").format(**data)

        elif (os.getenv("PLAIN_LOGGING", "0") == "1"):
            return ("[{level:7}] {message}").format(**data)

        return (
            f"│[dodger_blue3]{self.project()}[/dodger_blue3]├"
            "┤[green]{time}[/green]├"
            "┤[{level.icon}]{level:7}[/{level.icon}]│ "
            "▸ {message}"
        ).format(**data)

    @property
    def level(self) -> str:
        return os.getenv("LOGLEVEL", "INFO").upper()

    @level.setter
    def level(self, level: str) -> None:
        os.setenv("LOGLEVEL", level.upper())
        self.reset()

    @property
    def sink(self) -> Callable:
        if Runtime.GitHub:
            return print
        return rich.print

    def reset(self) -> None:
        log.remove()
        log.add(
            sink=self.sink,
            format=self.format,
            level=os.getenv("LOGLEVEL", "INFO").upper(),
            colorize=False,
            backtrace=True,
            diagnose=True,
            catch=True,
        )
        self._make_level("TRACE", None, "dark_turquoise")
        self._make_level("DEBUG", None, "turquoise4")
        self._make_level("INFO", None, "bright_white")
        self._make_level("NOTE", 25, "bright_blue")
        self._make_level("SPECIAL", 25, "bright_blue")
        self._make_level("TIP", 25, "dark_cyan")
        self._make_level("SUCCESS", None, "green")
        self._make_level("MINOR", 25, "grey42")
        self._make_level("SKIP", 25, "grey42")
        self._make_level("FIXME", 25, "cyan")
        self._make_level("TODO", 25, "dark_blue")
        self._make_level("WARNING", None, "yellow")
        self._make_level("ERROR", None, "red")
        self._make_level("CRITICAL", None, "red")

    def _make_level(self, level: str, loglevel: int=0, color: str=None) -> None:
        """Create or update a loglevel `.{name.lower()}` on the logger, optional 'echo' argument"""
        def wrapper(*args,
            dedent: bool=False,
            echo: bool=True,
        ) -> str:
            message = " ".join(map(str, args))
            if dedent:
                message = textwrap.dedent(message)
            if not echo:
                return message
            for line in message.splitlines():
                log.log(level, line)
            return message

        # Assign log function to logger. Workaround to set icon=color
        log.level(level, loglevel, icon=color)
        setattr(log, level.lower(), wrapper)

BrokenLogging()
