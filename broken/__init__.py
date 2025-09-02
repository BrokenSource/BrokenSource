import time

time.zero = time.perf_counter()
"""Precise time at which the program started since last boot"""

time.absolute = (lambda: time.perf_counter() - time.zero)
"""Precise time since the program started running"""

# ---------------------------------------------------------------------------- #

import sys
from pathlib import Path

from broken.envy import Environment

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

# Don't import asyncio in loguru, seems fine
if Environment.flag("LOGURU_NO_ASYNCIO", 1):
    class _fake: get_running_loop = (lambda: None)
    original = sys.modules.pop("asyncio", None)
    sys.modules["asyncio"] = _fake
    import loguru
    sys.modules["asyncio"] = original
    if (original is None):
        sys.modules.pop("asyncio")

# ---------------------------------------------------------------------------- #

import importlib.metadata

__version__ = importlib.metadata.version("broken-source")
