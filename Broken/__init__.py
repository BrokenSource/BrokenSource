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
BROKEN_VERSION:     str  = importlib.metadata.version("broken-source")

# isort: off
from .BrokenImports import *
from .BrokenEnum    import *
from .BrokenLogging import *
from .BrokenBase    import *
# from .BrokenDotmap  import *
from .Optional.BrokenDotmap import *
from .BrokenProject import *

# Create Broken monorepo project
import Broken.Resources as BrokenResources

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

from .BrokenProfiler import *

# -------------------------------------------------------------------------------------------------|
# Cursed Python ahead, here be dragons!

# Add a .get(index, default=None) method on lists, why is this not a thing?
forbiddenfruit.curse(
    list, "get",
    lambda self, index, default=None: self[index] if (index < len(self)) else default
)

# Append and return value on a list, it's walrus-like!
forbiddenfruit.curse(
    list, "appendget",
    lambda self, value: self.append(value) or value
)

# Workarounds for System ARGV

# Expand sys.argv's ./ or .\ to full path. This is required as the working directory of projects
# changes, so we must expand them on the main script relative to where Broken is used as CLI
for i, arg in enumerate(sys.argv):
    if any([arg.startswith(x) for x in ("./", "../", ".\\", "..\\")]):
        sys.argv[i] = str(BrokenPath.true_path(arg))
