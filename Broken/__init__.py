# -------------------------------------------------------------------------------------------------|
# Faster than halo spinners

from yaspin import yaspin
from yaspin.spinners import Spinners

_spinner = yaspin(text="Loading Library: Broken")
_spinner.start()

# -------------------------------------------------------------------------------------------------|
# Keep repository clean of __pycache__ and .pyc files

import os
import tempfile

# Write annoying __pycache__ and .pyc on temporary directory, keeps development directories clean.
# On Linux, it's under /tmp - System RAM, brutally fast, also shouldn't take that much memory
os.environ["PYTHONPYCACHEPREFIX"] = str(f"{tempfile.gettempdir()}/__pycache__")

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
import sys

# Information about the release and version
BROKEN_PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
BROKEN_PYAPP:       bool = bool(getattr(os.environ, "PYAPP", False))
BROKEN_NUITKA:      bool = ("__compiled__" in globals())
BROKEN_RELEASE:     bool = (BROKEN_NUITKA or BROKEN_PYINSTALLER or BROKEN_PYAPP)
BROKEN_DEVELOPMENT: bool = (not BROKEN_RELEASE)
BROKEN_VERSION:     str  = importlib.metadata.version("broken-source")

# isort: off
from .Imports import *
from .Enum    import *
from .Logging import *
from .Base    import *
from .Optional.Dotmap import *
from .Project import *

import Broken.Resources as BrokenResources

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

# The Broken.PROJECT variable points to the last initialized project, which more often than not
# is the current project. Just `import Broken` and set/access it for own BrokenProject class
PROJECT = BROKEN

from .Loaders   import *
from .Externals import *

if (sys.version_info>=(3, 12)) and (log.project=="Broken") and not (BrokenPlatform.OnLinux):
    log.warning(f"You are on Python 3.12+, some project packages might require compilation")

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

# -------------------------------------------------------------------------------------------------|

_spinner.stop()
