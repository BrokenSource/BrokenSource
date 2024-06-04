import os
import sys
import typing
from pathlib import Path

import pretty_errors

pretty_errors.configure(
    filename_display  = pretty_errors.FILENAME_EXTENDED,
    line_color        = pretty_errors.RED + "> \033[1;37m",
    code_color        = '  \033[1;37m',
    line_number_first = True,
    lines_before      = 10,
    lines_after       = 10,
)

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
os.environ["OMP_NUM_THREADS"] = "1"

# High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind own vblank
# https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
os.environ["__GL_YIELD"] = "USLEEP"

# Keep repository clean of __pycache__ and .pyc files by writing to .venv
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Expand "../paths" and existing ("-o", "file.ext") to abolute paths: Unanbiguously naming paths
for _index, _item in enumerate(sys.argv):
    if any((
        any((_item.startswith(x) for x in ("./", "../", ".\\", "..\\"))),
        bool(Path(_item).suffix) and Path(_item).exists(),
    )):
        sys.argv[_index] = str(Path(_item).expanduser().resolve())

# Replace argv[0] of "-c" with PyApp's managed python
if bool(os.environ.get("PYAPP", None)):
    sys.argv[0] = sys.executable

# Python <= 3.10 typing fixes
if sys.version_info <= (3, 10):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# -------------------------------------------------------------------------------------------------|

import importlib.metadata
import importlib.resources

# Information about the release and version
PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
PYAPP:       bool = bool(os.environ.get("PYAPP", False))
NUITKA:      bool = ("__compiled__" in globals())
PYPI:        bool = ("site-packages" in __file__.lower())
RELEASE:     bool = (NUITKA or PYINSTALLER or PYAPP or PYPI)
DEVELOPMENT: bool = (not RELEASE)
VERSION:     str  = importlib.metadata.version("broken-source")

import Broken.Resources as BrokenResources
from Broken.Core import (
    BIG_BANG,
    apply,
    clamp,
    denum,
    dunder,
    extend,
    flatten,
    have_import,
    hyphen_range,
    image_hash,
    last_locals,
    limited_integer_ratio,
    nearest,
    shell,
    temp_env,
)
from Broken.Core.BrokenEnum import BrokenEnum
from Broken.Core.BrokenLogging import BrokenLogging
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import BrokenPlatform
from Broken.Core.BrokenProfiler import BrokenProfiler, BrokenProfilerEnum
from Broken.Core.BrokenProject import BrokenApp, BrokenProject
from Broken.Core.BrokenResolution import BrokenResolution
from Broken.Core.BrokenScheduler import BrokenScheduler, BrokenTask
from Broken.Core.BrokenSpinner import BrokenSpinner
from Broken.Core.BrokenThread import BrokenThread, BrokenThreadPool
from Broken.Core.BrokenTorch import BrokenTorch, TorchFlavor
from Broken.Core.BrokenTyper import BrokenTyper
from Broken.Core.BrokenUtils import (
    BrokenAttrs,
    BrokenFluentBuilder,
    BrokenRelay,
    BrokenSingleton,
    BrokenWatchdog,
    Ignore,
    OnceTracker,
    SameTracker,
)

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
    PROJECT.pyapp_new_binary_restore_hook()
