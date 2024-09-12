# -------------------------------------------------------------------------------------------------|
# General fixes, improvements and safety

import os
import sys
import typing
from pathlib import Path

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

# Replace argv[0]=="-c" with PyApp's managed python
if bool(os.getenv("PYAPP", None)):
    sys.argv[0] = sys.executable

# Python < 3.11 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# Pretty tracebacks
if (os.getenv("RICH_TRACEBACK", "1") == "1"):
    import rich.traceback
    rich.traceback.install(width=None)

# -------------------------------------------------------------------------------------------------|
# Information about the release and version

import importlib.metadata
import importlib.resources
import struct

BITNESS: int = (struct.calcsize("P") * 8)
"""The word size of the Python interpreter (32, 64 bits)"""

VERSION: str = importlib.metadata.version("broken-source")
"""The version of the Broken library, and subsequently all projects"""

PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
"""True if running from a PyInstaller binary build (https://github.com/pyinstaller/pyinstaller)"""

NUITKA: bool = ("__compiled__" in globals())
"""True if running from a Nuitka binary build (https://github.com/Nuitka/Nuitka)"""

PYAPP: bool = bool(os.getenv("PYAPP", False))
"""True if running as a PyApp release (https://github.com/ofek/pyapp)"""

PYPI: bool = ("site-packages" in __file__.lower())
"""True if running as a installed package from PyPI (https://brokensrc.dev/get/pypi/)"""

DOCKER: bool = bool(os.getenv("DOCKER_RUNTIME", False))
"""True if running from a Docker container""" # Fixme: Detect without manual flag

GITHUB_CI: bool = bool(os.getenv("GITHUB_ACTIONS", False))
"""True if running from a GitHub Actions CI environment (https://docs.github.com/en/actions/writing-workflows/quickstart)"""

WSL: bool = bool(Path("/usr/lib/wsl/lib").exists())
"""True if running from a Windows Subsystem for Linux (https://learn.microsoft.com/en-us/windows/wsl/about)"""

RELEASE: bool = (PYINSTALLER or NUITKA or PYAPP or PYPI)
"""True if running from any static final release build (PyInstaller, Nuitka, PyApp, PyPI)"""

FROM_SOURCE: bool = (not RELEASE)
"""True if running directly from the source code (https://brokensrc.dev/get/source/)"""

import Broken.Resources as BrokenResources
from Broken.Core import (
    BrokenAttrs,
    BrokenFluent,
    BrokenRelay,
    BrokenSingleton,
    BrokenWatchdog,
    LazyImport,
    Nothing,
    OnceTracker,
    Patch,
    PlainTracker,
    SameTracker,
    Stack,
    apply,
    clamp,
    denum,
    dunder,
    every,
    filter_dict,
    flatten,
    hyphen_range,
    image_hash,
    limited_ratio,
    nearest,
    override,
    pydantic2typer,
    selfless,
    shell,
    temp_env,
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

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources)
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
