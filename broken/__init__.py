# -------------------------------- General fixes, quality of life -------------------------------- #

import os
import sys
import time
from pathlib import Path

time.zero = time.perf_counter()
"""Precise time at which the program started since last boot"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time since the program started running"""

class Environment:
    """Utilities for managing environment variables"""

    def __new__(cls) -> None:
        raise TypeError(f"{cls.__name__} class shouldn't be instantiated")

    def get(key: str, default: str=None) -> str:
        return os.getenv(key, default)

    def set(key: str, value: str | None) -> None:
        if (value is not None):
            os.environ[key] = str(value)
            return None
        Environment.pop(key)

    def setdefault(key: str, value: str | None) -> None:
        if (value is not None):
            os.environ.setdefault(key, str(value))

    def pop(key: str) -> str:
        return os.environ.pop(key, None)

    def update(**values: str | None) -> None:
        for key, value in values.items():
            Environment.set(key, value)

    def exists(key: str) -> bool:
        return (key in os.environ)

    def int(key: str, default: int=0) -> int:
        return int(os.getenv(key, default))

    def float(key: str, default: float=1.0) -> float:
        return float(os.getenv(key, default))

    def bool(key: str, default: bool=False) -> bool:
        value = str(os.getenv(key, default)).lower()

        if value in ("1", "true", "yes", "on"):
            return True
        elif value in ("0", "false", "no", "off"):
            return False

        raise ValueError(f"Invalid boolean value for environment variable '{key}': {value}")

    def flag(key: str, default: bool=False) -> bool:
        return Environment.bool(key, default)

    def iflag(key: str, default: bool=False) -> bool:
        return (not Environment.flag(key, default))

    # # Arguments

    def arguments() -> bool:
        return bool(sys.argv[1:])

    # # System PATH

    def _abs_path(x: Path) -> Path:
        return Path(x).expanduser().resolve().absolute()

    def path() -> list[Path]:
        return list(Path(x) for x in os.getenv("PATH", "").split(os.pathsep) if x)

    def in_path(path: Path) -> bool:
        return (Environment._abs_path(path) in Environment.path())

    def add_to_path(path: Path, prepend: bool=True) -> None:
        path = Environment._abs_path(path)
        Environment.set("PATH", ''.join((
            f"{path}{os.pathsep}" * (prepend),
            Environment.get("PATH", ""),
            f"{os.pathsep}{path}" * (not prepend),
        )))

# Keep the repository clean of bytecode cache files
if (_venv := Path(__file__).parent.parent/".venv").exists():
    sys.pycache_prefix = str(_venv/"pycache")

# Python <= 3.10 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self, TypeAlias
    typing.TypeAlias = TypeAlias
    typing.Self = Self

# Fix weird Pydantic use_attribute_docstrings error in older Python
Path.endswith = (lambda self, suffix: str(self).endswith(suffix))

# Huge CPU usage for little to no speed up on matrix multiplication of NumPy's BLAS
# - https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
# Warn: If using PyTorch CPU, set `torch.set_num_threads(multiprocessing.cpu_count())`
Environment.setdefault("OMP_NUM_THREADS", 1)

# NVIDIA: High CPU usage on glfw.swap_buffers when vsync is off and the GPU is wayy behind vsync
# - https://forums.developer.nvidia.com/t/glxswapbuffers-gobbling-up-a-full-cpu-core-when-vsync-is-off/156635
# - https://forums.developer.nvidia.com/t/gl-yield-and-performance-issues/27736
Environment.setdefault("__GL_YIELD", "USLEEP")

# macOS: Enable CPU fallback for PyTorch unsupported operations in native MPS
# - https://pytorch.org/docs/stable/mps_environment_variables.html
Environment.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", 1)

# Make telemetries opt-in instead of opt-out
Environment.setdefault("HF_HUB_DISABLE_TELEMETRY", 1)

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
from importlib.metadata import Distribution
from pathlib import Path

from broken.version import __version__


class Runtime:
    """Information about the current runtime environment"""

    Version: str = __version__
    """The version of the Broken library, and subsequently all projects"""

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

    Interactive: bool = sys.stdout.isatty()
    """True if running in an interactive terminal session (user can input)"""

# ------------------------------------------------------------------------------------------------ #

if Runtime.uvx:
    # Find venv from "~/.cache/uv/archive-v0/7x8klaYDn8Kd0GRTY-nYr/lib/python3.12/site-packages"
    _VIRTUAL_ENV = Path(site.getsitepackages()[0]).parent.parent.parent
    Environment.setdefault("VIRTUAL_ENV", _VIRTUAL_ENV)

# ---------------------------------------- Package exports --------------------------------------- #

from broken.core import (
    BrokenAttribute,
    BrokenAttrs,
    BrokenCache,
    BrokenLogging,
    BrokenModel,
    BrokenRelay,
    BrokenSingleton,
    DictUtils,
    FrozenHash,
    Nothing,
    StaticClass,
    apply,
    block_modules,
    clamp,
    combinations,
    denum,
    every,
    flatten,
    hyphen_range,
    install,
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
from broken.core.enumx import BrokenEnum, MultiEnum
from broken.core.path import BrokenPath
from broken.core.project import BrokenProject
from broken.core.system import ArchEnum, BrokenPlatform, PlatformEnum, SystemEnum

# ------------------------------------------------------------------------------------------------ #

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken")
"""The main library's BrokenProject instance"""

PROJECT: BrokenProject = BROKEN
"""The first BrokenProject initialized after (but including) BROKEN itself"""
