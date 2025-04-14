# -------------------------------- General fixes, quality of life -------------------------------- #

import time

time.zero = time.perf_counter()
"""Precise time at which the program started since last boot"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time since the program started running"""

import os # noqa

class Environment:
    """Utilities for managing environment variables"""

    def __new__(cls) -> None:
        raise TypeError(f"{cls.__name__} class cannot be instantiated")

    @staticmethod
    def set(key: str, value: str | None, /) -> None:
        if (value is not None):
            os.environ[key] = str(value)

    @staticmethod
    def append(key: str, value: str | None, /, pad: str=" ") -> None:
        if (key not in os.environ):
            Environment.set(key, value)
        elif (value is not None):
            os.environ[key] += pad + str(value)

    @staticmethod
    def setdefault(key: str, value: str | None, /) -> None:
        if (value is not None):
            os.environ.setdefault(key, str(value))

    @staticmethod
    def update(**values: str | None) -> None:
        for key, value in values.items():
            Environment.set(key, value)

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
    def iflag(key: str, default: bool=False, /) -> bool:
        return (not Environment.flag(key, default))

    @staticmethod
    def unset(key: str, /) -> None:
        os.unsetenv(key)

import sys
from pathlib import Path

# Keep the repository clean of cache files by writing them to .venv
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Warn if running unsupported Python versions
if sys.version_info < (3, 10):
    _current: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    sys.stderr.write(f"Warning: Python {_current} isn't officially supported and projects may break\n")
    sys.stderr.write("→ Fix: Upgrade to at least Python 3.10 for guaranteed compatibility\n")
    sys.stderr.write("→ See status of your version: (https://endoflife.date/python)\n")

# Python <= 3.10 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# Fix weird Pydantic use_attribute_docstrings error in older Python
Path.endswith = (lambda self, suffix: str(self).endswith(suffix))

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
Environment.setdefault("OMP_NUM_THREADS", 1)

# NVIDIA: High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind vsync
# https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
Environment.setdefault("__GL_YIELD", "USLEEP")

# macOS: Enable CPU fallback for PyTorch unsupported operations in native MPS
# https://pytorch.org/docs/stable/mps_environment_variables.html
Environment.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", 1)

# Make telemetries opt-in instead of opt-out
Environment.setdefault("HF_HUB_DISABLE_TELEMETRY", 1)
Environment.setdefault("DO_NOT_TRACK", 1)

# Pretty tracebacks, smart lazy installing
if Environment.flag("RICH_TRACEBACK", 1):
    def _lazy_hook(type, value, traceback):
        import rich.traceback
        rich.traceback.install(
            extra_lines=1,
            width=None,
        )(type, value, traceback)
    sys.excepthook = _lazy_hook

# --------------------------- Information about the release and version -------------------------- #

import site
import struct
from importlib.metadata import Distribution
from pathlib import Path

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

    Pyaket: bool = Environment.exists("PYAKET")
    """True if running as a Pyaket release (https://github.com/BrokenSource/Pyaket)"""

    uvx: bool = any(f"archive-v{x}" in __file__ for x in range(4))
    """True if running from uvx (https://docs.astral.sh/uv/concepts/tools/)"""

    PyPI: bool = (Distribution.from_name("broken-source").read_text("direct_url.json") is None)
    """True if running as a installed package from PyPI (https://brokensrc.dev/get/pypi/)"""

    Installer: bool = (Pyaket)
    """True if running from any executable build"""

    Release: bool = (Installer or PyPI)
    """True if running from any immutable final release build (Installer, PyPI)"""

    Source: bool = (not Release)
    """True if running directly from the source code (https://brokensrc.dev/get/source/)"""

    Method: str = (uvx and "uvx") or (Source and "Source") or (Installer and "Installer") or (PyPI and "PyPI")
    """The runtime environment of the current project release (Source, Release, PyPI)"""

    # # Special and Containers

    Docker: bool = Path("/.dockerenv").exists()
    """True if running from a Docker container"""

    GitHub: bool = Environment.exists("GITHUB_ACTIONS")
    """True if running in a GitHub Actions CI environment (https://github.com/features/actions)"""

    WSL: bool = Path("/usr/lib/wsl/lib").exists()
    """True if running in Windows Subsystem for Linux (https://learn.microsoft.com/en-us/windows/wsl/about)"""

    ZeroGPU: bool = Environment.bool("SPACES_ZERO_GPU")
    """True if running inside a HuggingFace's ZeroGPU space (https://huggingface.co/docs/hub/spaces-zerogpu)"""

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

# ------------------------------------------------------------------------------------------------ #

if Runtime.uvx:
    # Find venv from "~/.cache/uv/archive-v0/7x8klaYDn8Kd0GRTY-nYr/lib/python3.12/site-packages"
    VIRTUAL_ENV = Path(site.getsitepackages()[0]).parent.parent.parent
    Environment.setdefault("VIRTUAL_ENV", VIRTUAL_ENV)

# ---------------------------------------- Package exports --------------------------------------- #

from Broken.Core import (
    BrokenAttribute,
    BrokenAttrs,
    BrokenCache,
    BrokenFluent,
    BrokenLogging,
    BrokenModel,
    BrokenRelay,
    BrokenSingleton,
    BrokenWatchdog,
    DictUtils,
    FrozenHash,
    LazyImport,
    Nothing,
    Patch,
    StaticClass,
    ThreadedStdin,
    apply,
    arguments,
    block_modules,
    clamp,
    combinations,
    denum,
    easyloop,
    every,
    flatten,
    hyphen_range,
    install,
    limited_ratio,
    list_get,
    log,
    multi_context,
    nearest,
    override_module,
    overrides,
    pop_fill,
    shell,
    smartproxy,
    tempvars,
)
from Broken.Core.BrokenEnum import BrokenEnum, FlagEnum, MultiEnum
from Broken.Core.BrokenLauncher import BrokenLauncher
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import (
    ArchEnum,
    BrokenPlatform,
    PlatformEnum,
    SystemEnum,
)
from Broken.Core.BrokenProfiler import BrokenProfiler
from Broken.Core.BrokenProject import BrokenProject
from Broken.Core.BrokenResolution import BrokenResolution
from Broken.Core.BrokenScheduler import BrokenScheduler, SchedulerTask
from Broken.Core.BrokenTorch import BrokenTorch, SimpleTorch, TorchRelease
from Broken.Core.BrokenTrackers import (
    FileTracker,
    OnceTracker,
    PlainTracker,
    SameTracker,
)
from Broken.Core.BrokenTyper import BrokenTyper
from Broken.Core.BrokenWorker import BrokenWorker

# ------------------------------------------------------------------------------------------------ #

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource")
"""The main library's BrokenProject instance"""

PROJECT: BrokenProject = BROKEN
"""The first BrokenProject initialized after (but including) BROKEN itself"""

# ------------------------------------------------------------------------------------------------ #

# Centralize models for easier uninstalling
if Runtime.Installer:
    Environment.setdefault("HF_HOME",    BROKEN.DIRECTORIES.EXTERNAL_MODELS/"HuggingFace")
    Environment.setdefault("TORCH_HOME", BROKEN.DIRECTORIES.EXTERNAL_MODELS/"PyTorchHub")
