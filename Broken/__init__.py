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
BrokenPath.symlink(where=BROKEN_DIRECTORIES.WORKSPACE.parent, to=BROKEN_DIRECTORIES.PACKAGE/"Workspace")

# Create main Broken configuration file
BROKEN_CONFIG = BrokenDotmap(path=BROKEN_DIRECTORIES.CONFIG/"Broken.toml")

# Create logger based on configuration
__loglevel__ = BROKEN_CONFIG.logging.default("level", "trace").upper()
BrokenLogging().stdout(__loglevel__).file(BROKEN_DIRECTORIES.LOGS/"Broken.log", __loglevel__)

# -------------------------------------------------------------------------------------------------|

# isort: off
# from .BrokenDownloads import *
# from .BrokenExternals import *
# from .BrokenDynamics import *
# from .BrokenMIDI import *
# from .BrokenAudio import *
# from .BrokenTimeline import *
from .BrokenFFmpeg import *
# isort: on

