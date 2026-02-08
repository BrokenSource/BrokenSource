from dearlog import logger # isort: split

import importlib.metadata
import sys
from pathlib import Path

from broken.envy import Environment

__version__ = importlib.metadata.version("broken-source")

# Python <= 3.10 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self
    typing.Self = Self

# Pretty tracebacks, smart lazy installing
if Environment.flag("RICH_TRACEBACK", 1):
    def _lazy_hook(type, value, traceback):
        import rich.traceback
        rich.traceback.install(
            extra_lines=1,
            width=None,
        )(type, value, traceback)
    sys.excepthook = _lazy_hook
