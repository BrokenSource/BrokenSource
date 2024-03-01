from halo import Halo

__HALO__ = Halo(text="Initializing Broken").start()

# -------------------------------------------------------------------------------------------------|
# Pretty... Errors !

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
# Broken Library

import importlib.metadata
import importlib.resources
import os
import sys

# Information about the release and version
BROKEN_PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
BROKEN_PYAPP:       bool = bool(getattr(os.environ, "PYAPP", False))
BROKEN_NUITKA:      bool = ("__compiled__" in globals())
BROKEN_RELEASE:     bool = (BROKEN_NUITKA or BROKEN_PYINSTALLER or BROKEN_PYAPP)
BROKEN_DEVELOPMENT: bool = not BROKEN_RELEASE
BROKEN_VERSION:     str  = importlib.metadata.version("broken-source")

# isort: off
from .Imports import *
from .Enum    import *
from .Logging import *
from .Base    import *
from .Optional.Dotmap import *
from .Project import *

import Broken.Resources as BrokenResources

BROKEN = PROJECT = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

from .Loaders   import *
from .Externals import *

# -------------------------------------------------------------------------------------------------|
# Cursed Python ahead, here be dragons!

# Ignore mostly NumPy warnings
warnings.filterwarnings('ignore')

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

# As a safety measure, make all relative and strings with suffix ok paths absolute. We might run
# binaries from other cwd, so make sure to always use non-ambiguous absolute paths if found
# • File name collisions are unlikely with any Monorepo path (?)
for i, arg in enumerate(sys.argv):
    if any((
        any((arg.startswith(x) for x in ("./", "../", ".\\", "..\\"))),
        bool(Path(arg).suffix) and Path(arg).exists(),
    )):
        sys.argv[i] = str(BrokenPath(arg))

# Safer measures: Store the first cwd that Broken is run, always start from there
os.chdir(os.environ.setdefault("BROKEN_PREVIOUS_WORKING_DIRECTORY", os.getcwd()))

__HALO__.stop()
