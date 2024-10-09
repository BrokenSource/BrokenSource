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

from broken.version import __version__


class runtime:

    version: str = __version__
    """The version of the Broken library, and subsequently all projects"""

    # # Bitness

    bitness: int = (struct.calcsize("P") * 8)
    """The word size of the Python interpreter (32, 64 bits)"""

    python32: bool = (bitness == 32)
    """True if running on a 32-bit Python interpreter"""

    python64: bool = (bitness == 64)
    """True if running on a 64-bit Python interpreter"""

    # # Runtime environments

    pyinstaller: bool = bool(getattr(sys, "frozen", False))
    """True if running from a PyInstaller binary build (https://github.com/pyinstaller/pyinstaller)"""

    nuitka: bool = ("__compiled__" in globals())
    """True if running from a Nuitka binary build (https://github.com/Nuitka/Nuitka)"""

    pyapp: bool = bool(os.getenv("PYAPP", False))
    """True if running as a PyApp release (https://github.com/ofek/pyapp)"""

    pypi: bool = any((part in __file__.lower() for part in ("site-packages", "dist-packages")))
    """True if running as a installed package from PyPI (https://brokensrc.dev/get/pypi/)"""

    executable: bool = (pyinstaller or nuitka or pyapp)
    """True if running from any executable build (PyInstaller, Nuitka, PyApp)"""

    release: bool = (executable or pypi)
    """True if running from any static final release build (PyInstaller, Nuitka, PyApp, PyPI)"""

    source_code: bool = (not release)
    """True if running directly from the source code (https://brokensrc.dev/get/source/)"""

    method: str = (source_code and "Source") or (executable and "Release") or (pypi and "PyPI")
    """The runtime environment of the current project release (Source, Release, PyPI)"""

    # # Special and Containers

    docker: bool = bool(os.getenv("DOCKER_RUNTIME", False))
    """True if running from a Docker container""" # Fixme: Detect without manual flag

    github: bool = bool(os.getenv("GITHUB_ACTIONS", False))
    """True if running in a GitHub Actions CI environment (https://docs.github.com/en/actions/writing-workflows/quickstart)"""

    wsl: bool = Path("/usr/lib/wsl/lib").exists()
    """True if running in Windows Subsystem for Linux (https://learn.microsoft.com/en-us/windows/wsl/about)"""

    interactive: bool = sys.stdout.isatty()
    """True if running in an interactive terminal session (user can input)"""

# ---------------------------------------- Module imports ---------------------------------------- #

import broken.resources as resources
from broken.core import (
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
    actions,
    apply,
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
from broken.core.enumeration import BrokenEnum
from broken.core.logging import BrokenLogging, log
from broken.core.path import BrokenPath
from broken.core.profiler import BrokenProfiler, BrokenProfilerEnum
from broken.core.project import BrokenApp, BrokenProject
from broken.core.pytorch import BrokenTorch, TorchFlavor
from broken.core.resolution import BrokenResolution
from broken.core.scheduler import BrokenScheduler, BrokenTask
from broken.core.system import BrokenSystem
from broken.core.terminal import BrokenTerminal
from broken.core.thread import BrokenThread, BrokenThreadPool

BROKEN = BrokenProject(
    package=__file__,
    name="Broken",
    author="BrokenSource",
    resources=resources)
"""The main library's BrokenProject instance. Useful for common downloads and resources"""

project = BROKEN
"""The first BrokenProject initialized after (but including) BROKEN itself"""

# ------------------------------------------------------------------------------------------------ #
