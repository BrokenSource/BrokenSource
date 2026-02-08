from dearlog import logger  # isort: split

from importlib.metadata import metadata

__meta__:   dict = metadata("broken-source")
__about__:   str = __meta__["Summary"]
__author__:  str = __meta__["Author"]
__version__: str = __meta__["Version"]

import os
import sys

# Python <= 3.10 typing fixes
if sys.version_info < (3, 11):
    import typing # noqa
    from typing_extensions import Self
    typing.Self = Self

# Pretty tracebacks, smart lazy installing
if os.getenv("RICH_TRACEBACK") == "1":
    def _lazy_hook(type, value, traceback):
        import rich.traceback
        rich.traceback.install(
            extra_lines=1,
            width=None,
        )(type, value, traceback)
    sys.excepthook = _lazy_hook
