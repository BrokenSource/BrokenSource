# -------------------------------- General fixes, quality of life -------------------------------- #

import os
import time

time.zero = time.perf_counter()
"""Precise time the program started since last boot"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time the program has been running for"""

class Environment:
    """Utilities for managing environment variables"""

    def __new__(cls) -> None:
        raise TypeError(f"{cls.__name__} class cannot be instantiated")

    @staticmethod
    def set(key: str, value: str, /) -> None:
        os.environ[key] = str(value)

    @staticmethod
    def setdefault(key: str, value: str, /) -> None:
        os.environ.setdefault(key, str(value))

    @staticmethod
    def get(key: str, default: str=None, /) -> str:
        return os.getenv(key, default)

    @staticmethod
    def exists(key: str, /) -> bool:
        return (key in os.environ)

    @staticmethod
    def int(key: str, default: int=0, /) -> int:
        return int(os.getenv(key, default))

    @staticmethod
    def float(key: str, default: float=1.0, /) -> float:
        return float(os.getenv(key, default))

    @staticmethod
    def bool(key: str, default: bool=False, /) -> bool:
        value = str(os.getenv(key, default)).lower()

        if value in ("1", "true", "yes", "on"):
            return True
        elif value in ("0", "false", "no", "off"):
            return False

        raise ValueError(f"Invalid boolean value for environment variable '{key}': {value}")

    @staticmethod
    def flag(key: str, default: bool=False, /) -> bool:
        return Environment.bool(key, default)

    @staticmethod
    def unset(key: str, /) -> None:
        os.unsetenv(key)

import sys
from pathlib import Path

# Keep the repository clean of cache files by writing them to .venv
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Warn if running unsupported Python versions
if sys.version_info <= (3, 9):
    _current: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    sys.stderr.write(f"Warning: Python {_current} isn't officially supported and projects may break\n")
    sys.stderr.write("→ Fix: Upgrade to at least Python 3.10 for guaranteed compatibility\n")
    sys.stderr.write("→ See status of your version: https://devguide.python.org/versions/\n")

# Python < 3.11 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
Environment.setdefault("OMP_NUM_THREADS", 1)

# NVIDIA: High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind vsync
# https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
Environment.setdefault("__GL_YIELD", "USLEEP")

# Replace argv[0] being "-c" to PyApp's managed python
if Environment.exists("PYAPP"):
    sys.argv[0] = sys.executable

# Pretty tracebacks
if Environment.flag("RICH_TRACEBACK", 1):
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

    PyApp: bool = Environment.exists("PYAPP")
    """True if running as a PyApp release (https://github.com/ofek/pyapp)"""

    PyPI: bool = any((part in __file__.lower() for part in ("site-packages", "dist-packages")))
    """True if running as a installed package from PyPI (https://brokensrc.dev/get/pypi/)"""

    Binary: bool = (PyInstaller or Nuitka or PyApp)
    """True if running from any executable build (PyInstaller, Nuitka, PyApp)"""

    Release: bool = (Binary or PyPI)
    """True if running from any static final release build (PyInstaller, Nuitka, PyApp, PyPI)"""

    Source: bool = (not Release)
    """True if running directly from the source code (https://brokensrc.dev/get/source/)"""

    Method: str = (Source and "Source") or (Binary and "Binary") or (PyPI and "PyPI")
    """The runtime environment of the current project release (Source, Release, PyPI)"""

    # # Special and Containers

    Docker: bool = Path("/.dockerenv").exists()
    """True if running from a Docker container"""

    GitHub: bool = Environment.exists("GITHUB_ACTIONS")
    """True if running in a GitHub Actions CI environment (https://github.com/features/actions)"""

    WSL: bool = Path("/usr/lib/wsl/lib").exists()
    """True if running in Windows Subsystem for Linux (https://learn.microsoft.com/en-us/windows/wsl/about)"""

    Interactive: bool = sys.stdout.isatty()
    """True if running in an interactive terminal session (user can input)"""

class Tools:
    """Shortcuts to common tools and utilities"""

    python: Path = Path(sys.executable)
    """The current Python interpreter executable"""

    uv: list[str, Path] = [python, "-m", "uv"]
    """Entry point for the uv package manager (https://github.com/astral-sh/uv)"""

    pip: list[str, Path] = [python, "-m", "uv", "pip"]
    """Entry point for pip"""

# ---------------------------------------- Package exports --------------------------------------- #

import Broken.Resources as BrokenResources
from Broken.Core import (
    BrokenAttribute,
    BrokenAttrs,
    BrokenCache,
    BrokenFluent,
    BrokenModel,
    BrokenRelay,
    BrokenSingleton,
    BrokenWatchdog,
    DictUtils,
    FrozenHash,
    LazyImport,
    Nothing,
    Patch,
    apply,
    arguments,
    block_modules,
    clamp,
    combinations,
    denum,
    every,
    flatten,
    hyphen_range,
    install,
    limited_ratio,
    list_get,
    multi_context,
    nearest,
    overrides,
    pop_fill,
    shell,
    smartproxy,
    tempvars,
)
from Broken.Core.BrokenEnum import BrokenEnum, FlagEnum, MultiEnum
from Broken.Core.BrokenLogging import BrokenLogging, log
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import (
    ArchEnum,
    BrokenPlatform,
    PlatformEnum,
    SystemEnum,
)
from Broken.Core.BrokenProfiler import BrokenProfiler, BrokenProfilerEnum
from Broken.Core.BrokenProject import BrokenApp, BrokenProject
from Broken.Core.BrokenResolution import BrokenResolution
from Broken.Core.BrokenScheduler import BrokenScheduler, BrokenTask
from Broken.Core.BrokenThread import BrokenThread, ParallelQueue, WorkerPool
from Broken.Core.BrokenTorch import BrokenTorch, TorchFlavor
from Broken.Core.BrokenTrackers import (
    FileTracker,
    OnceTracker,
    PlainTracker,
    SameTracker,
)
from Broken.Core.BrokenTyper import BrokenTyper

# ------------------------------------------------------------------------------------------------ #

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources
)
"""The main library's BrokenProject instance"""

PROJECT: BrokenProject = BROKEN
"""The first BrokenProject initialized after (but including) BROKEN itself"""

# ------------------------------------------------------------------------------------------------ #
