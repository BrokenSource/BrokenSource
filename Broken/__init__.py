# -------------------------------------------------------------------------------------------------|
# Keep repository clean of __pycache__ and .pyc files

import os
import tempfile

# Write annoying __pycache__ and .pyc on temporary directory, keeps development directories clean.
# On Linux, it's under /tmp - System RAM, brutally fast, also shouldn't take that much memory
os.environ["PYTHONPYCACHEPREFIX"] = str(f"{tempfile.gettempdir()}/__pycache__")

# -------------------------------------------------------------------------------------------------|
# Idk why but PyAPP isn't passing the argument on Linux
import sys

if bool(os.environ.get("PYAPP", False)) and (os.name != "nt"):
    sys.argv.insert(0, sys.executable)

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
from pathlib import Path

# Information about the release and version
PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
PYAPP:       bool = bool(os.environ.get("PYAPP", False))
NUITKA:      bool = ("__compiled__" in globals())
RELEASE:     bool = (NUITKA or PYINSTALLER or PYAPP)
DEVELOPMENT: bool = (not RELEASE)
VERSION:     str  = importlib.metadata.version("broken-source")

import Broken.Resources as BrokenResources
from Broken.Base import BrokenPath
from Broken.Base import BrokenPlatform
from Broken.Logging import log
from Broken.Project import BrokenProject

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

# The Broken.PROJECT variable points to the last initialized project, which more often than not
# is the current project. Just `import Broken` and set/access it for own BrokenProject class
PROJECT = BROKEN

# -------------------------------------------------------------------------------------------------|
# Small fixes
# Numpy's blas broken multiprocessing on matmul
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
os.environ["OMP_NUM_THREADS"] = "1"

# Patch torch.jit requiring inspect.getsource
# https://github.com/pytorch/vision/issues/1899#issuecomment-598200938
if PYINSTALLER:
    try:
        import torch.jit
        def patch(object, **kwargs):
            return object
        torch.jit.script_method = patch
        torch.jit.script = patch
    except (ModuleNotFoundError, ImportError):
        pass

    import pyi_splash  # type: ignore
    pyi_splash.close()


if (sys.version_info>=(3, 12)) and (log.project=="Broken") and not (BrokenPlatform.OnLinux):
    log.warning("You are on Python 3.12+, some project packages might require compilation")

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
