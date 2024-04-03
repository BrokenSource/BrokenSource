# -------------------------------------------------------------------------------------------------|

import os
import sys
import typing
from pathlib import Path

# Keep repository clean of __pycache__ and .pyc files by writing to .venv
sys.pycache_prefix = str(Path(__file__).parent.parent/".venv"/"pycache")

# Fix: typing.Self was implemented on Python >= 3.11
if sys.version_info < (3, 11):
    typing.Self = typing.Any

# PyAPP isn't passing the argument on Linux
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
from Broken.Project import BrokenProject

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

PROJECT = BROKEN
"""
The Broken.PROJECT variable points to the first project set on Broken.set_project, else BROKEN.
It is useful to use current project pathing and resources on common parts of the code
"""

def set_project(project: BrokenProject):
    global PROJECT
    if not isinstance(project, BrokenProject):
        raise TypeError(f"Project must be an instance of BrokenProject, not {type(project)}")
    if PROJECT is not BROKEN:
        return
    PROJECT = project

# -------------------------------------------------------------------------------------------------|

# As a safety measure, make all relative and strings with suffix ok paths absolute. We might run
# binaries from other cwd, so make sure to always use non-ambiguous absolute paths if found
# • File name collisions are unlikely with any Monorepo path (?)
for i, arg in enumerate(sys.argv):
    if any((
        any((arg.startswith(x) for x in ("./", "../", ".\\", "..\\"))),
        bool(Path(arg).suffix) and Path(arg).exists(),
    )):
        sys.argv[i] = str(Path(arg).expanduser().resolve())

# Safer measures: Store the first cwd that Broken is run, always start from there
os.chdir(os.environ.setdefault("BROKEN_PREVIOUS_WORKING_DIRECTORY", os.getcwd()))

# -------------------------------------------------------------------------------------------------|
# Small fixes

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
