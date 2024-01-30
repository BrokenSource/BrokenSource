import pretty_errors

pretty_errors.configure(
    filename_display  = pretty_errors.FILENAME_EXTENDED,
    line_color        = pretty_errors.RED + "> \033[1;37m",
    code_color        = '  \033[1;37m',
    line_number_first = True,
    lines_before      = 10,
    lines_after       = 10,
)

# -------------------------------------------------------------------------------------------------|

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

import Broken.Resources as BrokenResources

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

from .BrokenExternals import *

# -------------------------------------------------------------------------------------------------|
# Cursed Python ahead, here be dragons!

# Add a list.get(index, default=None)
forbiddenfruit.curse(
    list, "get",
    lambda self, index, default=None: self[index] if (index < len(self)) else default
)

# Walrus-like operator for list.append
forbiddenfruit.curse(
    list, "appendget",
    lambda self, value: self.append(value) or value
)

# Expand sys.argv's ./ or .\ to the full path. This is required as the working directory of projects
# changes, so we must expand them on the main script relative to where Broken is used as CLI
for i, arg in enumerate(sys.argv):
    if any([arg.startswith(x) for x in ("./", "../", ".\\", "..\\")]):
        sys.argv[i] = str(BrokenPath.true_path(arg))
