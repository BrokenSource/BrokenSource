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
from .BrokenProject import *

# Create Broken monorepo project
BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
)

from .BrokenUtils import *

# Symlink path to projects data to the root of the monorepo for convenience
try:
    BrokenPath.symlink(
        virtual=BROKEN.DIRECTORIES.REPOSITORY/"Workspace",
        real=BROKEN.DIRECTORIES.WORKSPACE.parent,
        echo=False
    )
except Exception:
    pass

from .Modules import *
