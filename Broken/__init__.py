import importlib.metadata
import sys

# Information about the release and version
BROKEN_PYINSTALLER: bool = getattr(sys, "frozen", False)
BROKEN_NUITKA:      bool = ("__compiled__" in globals())
BROKEN_RELEASE:     bool = (BROKEN_NUITKA or BROKEN_PYINSTALLER)
BROKEN_VERSION:     str = "v" + (importlib.metadata.version("Broken") or "Unknown")

# isort: off
from .BrokenImports import *
from .BrokenLogging import *
from .BrokenDotmap import *
from .BrokenDirectories import *
from .BrokenUtils import *
# isort: on

# Symlink path to projects data to the root of the monorepo for convenience
BrokenPath.symlink(where=BROKEN_DIRECTORIES.ROOT, to=BROKEN_MONOREPO_DIR/"Workspace")

# Create main Broken configuration file
BROKEN_CONFIG = BrokenDotmap(path=BROKEN_DIRECTORIES.CONFIG/"Broken.toml")

# Create logger based on configuration
__loglevel__ = BROKEN_CONFIG.logging.default("level", "info").upper()
BrokenLogging().stdout(__loglevel__).file(BROKEN_DIRECTORIES.LOGS/"Broken.log", __loglevel__)

# -------------------------------------------------------------------------------------------------|

# isort: off
from .BrokenDownloads import *
from .BrokenExternals import *
from .BrokenDynamics import *
from .BrokenMIDI import *
from .BrokenAudio import *
from .BrokenTimeline import *
from .BrokenFFmpeg import *
# isort: on


class BrokenBase:
    def typer_app(description: str = None, **kwargs) -> typer.Typer:
        return typer.Typer(
            help=description or "No help provided",
            add_help_option=False,
            pretty_exceptions_enable=False,
            no_args_is_help=kwargs.get("no_args_is_help", True),
            add_completion=False,
            rich_markup_mode="rich",
            chain=False,
            epilog=(
                f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]{BROKEN_VERSION}[/yellow]\n\n"
                "→ [italic grey53]Consider [blue][link=https://github.com/sponsors/Tremeschin]Sponsoring[/link][/blue] my Open Source Work[/italic grey53]"
            ),
        )
