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

# -------------------------------------------------------------------------------------------------|

# Symlink path to projects data to the root of the monorepo for convenience
try:
    BrokenPath.symlink(virtual=BROKEN_DIRECTORIES.PACKAGE/"Workspace", real=BROKEN_DIRECTORIES.WORKSPACE.parent)
except Exception:
    pass

# Create main Broken configuration file
BROKEN_CONFIG = BrokenDotmap(path=BROKEN_DIRECTORIES.CONFIG/"Broken.toml")

# Create logger based on configuration
__loglevel__ = BROKEN_CONFIG.logging.default("level", "trace").upper()
try:
    # Fixme: Windows and two Broken instances sharing a log file
    BrokenLogging().stdout(__loglevel__)
    BrokeLogging().file(BROKEN_DIRECTORIES.LOGS/"Broken.log", __loglevel__)
except Exception:
    pass

# -------------------------------------------------------------------------------------------------|

from .Modules import *
