# -------------------------- General fixes, quality of life, and safety -------------------------- #

import time

time.zero = time.perf_counter()
"""Precise time at which the program started since booting the computer"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time this Python process has been running, started at time.zero"""

import os
import sys
from pathlib import Path

# Keep repository clean of __pycache__ and .pyc files by writing them to .venv
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
os.environ["OMP_NUM_THREADS"] = "1"

# NVIDIA: High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind vsync
# https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
os.environ["__GL_YIELD"] = "USLEEP"

# Force UTF-8 encoding for the environment
os.environ["PYTHONIOENCODING"] = "utf-8"

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

# --------------------------- Information about the release and version -------------------------- #

import struct

from Broken.Version import __version__


class Runtime:
    """Information about the current runtime environment"""

    Version: str = __version__
    """The version of the Broken library, and subsequently all projects"""

    # # Bitness

    Bitness: int = (struct.calcsize("P") * 8)
    """The word size of the Python interpreter (32, 64 bits)"""

    Python32: bool = (Bitness == 32)
    """True if running on a 32-bit Python interpreter"""

    Python64: bool = (Bitness == 64)
    """True if running on a 64-bit Python interpreter"""

    # # Runtime environments

    PyInstaller: bool = bool(getattr(sys, "frozen", False))
    """True if running from a PyInstaller binary build (https://github.com/pyinstaller/pyinstaller)"""

    Nuitka: bool = ("__compiled__" in globals())
    """True if running from a Nuitka binary build (https://github.com/Nuitka/Nuitka)"""

    PyApp: bool = bool(os.getenv("PYAPP", False))
    """True if running as a PyApp release (https://github.com/ofek/pyapp)"""

    PyPI: bool = any((part in __file__.lower() for part in ("site-packages", "dist-packages")))
    """True if running as a installed package from PyPI (https://brokensrc.dev/get/pypi/)"""

    Executable: bool = (PyInstaller or Nuitka or PyApp)
    """True if running from any executable build (PyInstaller, Nuitka, PyApp)"""

    Release: bool = (Executable or PyPI)
    """True if running from any static final release build (PyInstaller, Nuitka, PyApp, PyPI)"""

    Source: bool = (not Release)
    """True if running directly from the source code (https://brokensrc.dev/get/source/)"""

    Method: str = (Source and "Source") or (Executable and "Executable") or (PyPI and "PyPI")
    """The runtime environment of the current project release (Source, Release, PyPI)"""

    # # Special and Containers

    Docker: bool = bool(os.getenv("DOCKER_RUNTIME", False))
    """True if running from a Docker container""" # Fixme: Detect without manual flag

    Github: bool = bool(os.getenv("GITHUB_ACTIONS", False))
    """True if running in a GitHub Actions CI environment (https://docs.github.com/en/actions/writing-workflows/quickstart)"""

    WSL: bool = Path("/usr/lib/wsl/lib").exists()
    """True if running in Windows Subsystem for Linux (https://learn.microsoft.com/en-us/windows/wsl/about)"""

    Interactive: bool = sys.stdout.isatty()
    """True if running in an interactive terminal session (user can input)"""

# ---------------------------------------- Module imports ---------------------------------------- #

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
    SerdeBaseModel,
    Stack,
    apply,
    arguments,
    clamp,
    denum,
    dunder,
    every,
    filter_dict,
    flatten,
    hyphen_range,
    image_hash,
    install,
    iter_dict,
    limited_ratio,
    nearest,
    overrides,
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
"""The first BrokenProject initialized after (but including) BROKEN itself"""

# ------------------------------------------------------------------------------------------------ #
