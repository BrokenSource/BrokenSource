# -------------------------------------------------------------------------------------------------|
# Tracebacks

import os
from pathlib import Path

if (os.getenv("RICH_TRACEBACK", "1") == "1"):
    import rich.traceback
    rich.traceback.install(width=None)

# -------------------------------------------------------------------------------------------------|
# General fixes and safety

import os
import sys
import typing

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
os.environ["OMP_NUM_THREADS"] = "1"

# NVIDIA: High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind vblank
# https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
os.environ["__GL_YIELD"] = "USLEEP"

# Keep repository clean of __pycache__ and .pyc files by writing them to .venv
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Resolve relative paths and existing files on argv
for _index, _item in enumerate(sys.argv):
    if any((
        any((_item.startswith(x) for x in ("./", "../", ".\\", "..\\"))),
        bool(Path(_item).suffix) and Path(_item).exists(),
    )):
        sys.argv[_index] = str(Path(_item).expanduser().resolve())

# Replace argv[0]=="-c" with PyApp's managed python
if bool(os.getenv("PYAPP", None)):
    sys.argv[0] = sys.executable

# Python < 3.11 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# -------------------------------------------------------------------------------------------------|
# Actual package

import importlib.metadata
import importlib.resources

# Information about the release and version
VERSION:     str  = importlib.metadata.version("broken-source")
PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
NUITKA:      bool = ("__compiled__" in globals())
PYAPP:       bool = bool(os.getenv("PYAPP", False))
PYPI:        bool = ("site-packages" in __file__.lower())
DOCKER:      bool = bool(os.getenv("DOCKER_RUNTIME", False))
WSL:         bool = bool(Path("/usr/lib/wsl/lib").exists())
RELEASE:     bool = (PYINSTALLER or NUITKA or PYAPP or PYPI)
DEVELOPMENT: bool = (not RELEASE)
GITHUB_CI:   bool = bool(os.getenv("GITHUB_ACTIONS", False))

import Broken.Resources as BrokenResources
from Broken.Core import (
    Stack,
    apply,
    clamp,
    denum,
    dunder,
    flatten,
    hyphen_range,
    image_hash,
    last_locals,
    limited_integer_ratio,
    nearest,
    pydantic_cli,
    shell,
    temp_env,
    valid,
)
from Broken.Core.BrokenEnum import BrokenEnum
from Broken.Core.BrokenLogging import BrokenLogging, log
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
    LazyImport,
    OnceTracker,
    Patch,
    PlainTracker,
    SameTracker,
)

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources
)
"""The main library's BrokenProject instance. Useful for common downloads and resources"""

PROJECT = BROKEN
"""The first BrokenProject initialized after, but including, BROKEN itself"""

# -------------------------------------------------------------------------------------------------|

import time

time.zero = time.perf_counter()
"""Precise time at which the program started since booting the computer"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time this Python process has been running, started at time.zero"""

# -------------------------------------------------------------------------------------------------|
