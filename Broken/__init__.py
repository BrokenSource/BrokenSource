import importlib.metadata
import importlib.resources
import os
import sys

# Information about the release and version
BROKEN_PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
BROKEN_PYAPP:       bool = bool(os.environ.get("PYAPP", False))
BROKEN_NUITKA:      bool = ("__compiled__" in globals())
BROKEN_RELEASE:     bool = (BROKEN_NUITKA or BROKEN_PYINSTALLER or BROKEN_PYAPP)
BROKEN_DEVELOPMENT: bool = not BROKEN_RELEASE
BROKEN_VERSION:     str  = importlib.metadata.version("Broken") or "Unknown"

# isort: off
from .BrokenImports import *
from .BrokenLogging import *
from .BrokenDotmap import *
from .BrokenUtils import *
from .BrokenProject import *

import Broken.Resources as BrokenResources

# Create Broken monorepo project
BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

from .Modules import *

# Workarounds for System ARGV

# Expand sys.argv's ./ or .\ to full path. This is required as the working directory of projects
# changes, so we must expand them on the main script relative to where Broken is used as CLI
for i, arg in enumerate(sys.argv):
    if any([arg.startswith(x) for x in ("./", "../", ".\\", "..\\")]):
        sys.argv[i] = str(BrokenPath.true_path(arg))
