import importlib.metadata
import importlib.resources
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
from .BrokenProject import *

# Create Broken monorepo project
BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
)

from .BrokenUtils import *
from .Modules import *
