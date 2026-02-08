import contextlib
import os
import site
import sys
from importlib.metadata import Distribution
from pathlib import Path
from typing import Optional


def abs_path(x: Path) -> Path:
    return Path(x).expanduser().resolve().absolute()

class Environment:
    """Utilities for managing environment variables"""

    def __new__(cls) -> None:
        raise TypeError(f"{cls.__name__} class cannot be instantiated")

    def get(key: str, default: str=None) -> Optional[str]:
        return os.getenv(key, default)

    def set(key: str, value: Optional[str]) -> None:
        if (value is not None):
            os.environ[key] = str(value)
            return None
        Environment.pop(key)

    def setdefault(key: str, value: str) -> None:
        os.environ.setdefault(key, str(value))

    def pop(key: str) -> Optional[str]:
        return os.environ.pop(key, None)

    def update(**values: Optional[str]) -> None:
        for key, value in values.items():
            Environment.set(key, value)

    def exists(key: str) -> bool:
        return (key in os.environ)

    def absent(key: str) -> bool:
        return (key not in os.environ)

    def int(key: str, default: int=0) -> int:
        return int(os.getenv(key, default))

    def float(key: str, default: float=1.0) -> float:
        return float(os.getenv(key, default))

    def bool(key: str, default: bool=False) -> bool:
        value = str(os.getenv(key, default)).lower()

        if value in ("1", "true", "t", "yes", "y", "on"):
            return True
        elif value in ("0", "false", "f", "no", "n", "off"):
            return False

        raise ValueError(f"Invalid boolean for environment variable '{key}': {value}")

    def flag(key: str, default: bool=False) -> bool:
        return Environment.bool(key, default)

    def path(key: str, default: str="") -> Path:
        return abs_path(Path(os.getenv(key, default)))

    @contextlib.contextmanager
    def temporary(**variables: str):
        original = os.environ.copy()
        Environment.update(**variables)
        try:
            yield None
        finally:
            os.environ.clear()
            os.environ.update(original)

    def arguments() -> bool:
        return (len(sys.argv) > 1)

    # # System PATH

    def PATH() -> list[Path]:
        return list(Path(x) for x in os.getenv("PATH", "").split(os.pathsep) if x)

    def in_path(path: Path) -> bool:
        return (abs_path(path) in Environment.PATH())

    def add_to_path(path: Path, prepend: bool=True) -> None:
        path = abs_path(path)
        Environment.set("PATH", ''.join((
            f"{path}{os.pathsep}" * (prepend),
            Environment.get("PATH", ""),
            f"{os.pathsep}{path}" * (not prepend),
        )))

# ---------------------------------------------------------------------------- #

class Runtime:
    """Information about the current runtime environment"""

    # # Runtime environments

    Pyaket: bool = Environment.exists("PYAKET")
    """True if running as a Pyaket release (https://github.com/BrokenSource/Pyaket)"""

    uvx: bool = any(f"archive-v{x}" in __file__ for x in range(4))
    """True if running from uvx (https://docs.astral.sh/uv/concepts/tools/)"""

    PyPI: bool = (Distribution.from_name("broken-source").read_text("direct_url.json") is None)
    """True if running as a installed package from PyPI"""

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

if Runtime.uvx:
    # Find venv from "~/.cache/uv/archive-v0/(hash)/lib/python3.12/site-packages"
    _VIRTUAL_ENV = Path(site.getsitepackages()[0]).parent.parent.parent
    os.environ.setdefault("VIRTUAL_ENV", _VIRTUAL_ENV)
