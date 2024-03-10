# -------------------------------------------------------------------------------------------------|
# Faster than halo spinners

from yaspin import yaspin
from yaspin.spinners import Spinners

_spinner = yaspin(text="Initializing Library: Broken")
_spinner.start()

# -------------------------------------------------------------------------------------------------|
# Keep repository clean of __pycache__ and .pyc files

import os
import tempfile

# Write annoying __pycache__ and .pyc on temporary directory, keeps development directories clean.
# On Linux, it's under /tmp - System RAM, brutally fast, also shouldn't take that much memory
os.environ["PYTHONPYCACHEPREFIX"] = str(f"{tempfile.gettempdir()}/__pycache__")

# -------------------------------------------------------------------------------------------------|
# Pretty... Errors !

import pretty_errors

pretty_errors.configure(
    filename_display  = pretty_errors.FILENAME_EXTENDED,
    line_color        = pretty_errors.RED + "> \033[1;37m",
    code_color        = '  \033[1;37m',
    line_number_first = True,
    lines_before      = 10,
    lines_after       = 10,
)

# -------------------------------------------------------------------------------------------------|
# Broken Library

import importlib.metadata
import importlib.resources
import sys

# Information about the release and version
BROKEN_PYINSTALLER: bool = bool(getattr(sys, "frozen", False))
BROKEN_PYAPP:       bool = bool(getattr(os.environ, "PYAPP", False))
BROKEN_NUITKA:      bool = ("__compiled__" in globals())
BROKEN_RELEASE:     bool = (BROKEN_NUITKA or BROKEN_PYINSTALLER or BROKEN_PYAPP)
BROKEN_DEVELOPMENT: bool = (not BROKEN_RELEASE)
BROKEN_VERSION:     str  = importlib.metadata.version("broken-source")

# isort: off
from .Imports import *
from .Enum    import *
from .Logging import *
from .Base    import *
from .Optional.Dotmap import *
from .Project import *

import Broken.Resources as BrokenResources

BROKEN = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="Broken",
    APP_AUTHOR="BrokenSource",
    RESOURCES=BrokenResources,
)

# The Broken.PROJECT variable points to the last initialized project, which more often than not
# is the current project. Just `import Broken` and set/access it for own BrokenProject class
PROJECT = BROKEN

from .Loaders   import *
from .Externals import *

# -------------------------------------------------------------------------------------------------|
# Cursed Python ahead, here be dragons!

if (sys.version_info>=(3, 12)) and (log.project=="Broken") and not (BrokenPlatform.OnLinux):
    log.warning(f"You are on Python 3.12+, some project packages might require compilation")

# Ignore mostly NumPy warnings
warnings.filterwarnings('ignore')

# Add a list.get(index, default=None)
forbiddenfruit.curse(
    list, "get",
    lambda self, index, default=None: self[index] if (index < len(self)) else default
)

# Walrus-like operator for list.append
forbiddenfruit.curse(
    list, "appendget",
    lambda self, value: self.append(value) or value
)

def transcends(method, base, generator: bool=False):
    """
    Are you tired of managing and calling super().<name>(*args, **kwargs) in your methods?
    > We have just the right solution for you!

    Introducing transcends, the decorator that crosses your class's MRO and calls the method
    with the same name as the one you are decorating. It's an automatic super() !
    """
    name = method.__name__

    def decorator(func: Callable) -> Callable:
        def get_targets(self):
            for cls in type(self).mro()[:-1]:
                if cls in (base, object):
                    continue
                if (target := cls.__dict__.get(name)):
                    yield target

        # Note: We can't have a `if generator` else the func becomes a Generator
        def yields(self, *args, **kwargs):
            for target in get_targets(self):
                yield from target(self, *args, **kwargs)
        def plain(self, *args, **kwargs):
            for target in get_targets(self):
                target(self, *args, **kwargs)

        return (yields if generator else plain)
    return decorator

# As a safety measure, make all relative and strings with suffix ok paths absolute. We might run
# binaries from other cwd, so make sure to always use non-ambiguous absolute paths if found
# • File name collisions are unlikely with any Monorepo path (?)
for i, arg in enumerate(sys.argv):
    if any((
        any((arg.startswith(x) for x in ("./", "../", ".\\", "..\\"))),
        bool(Path(arg).suffix) and Path(arg).exists(),
    )):
        sys.argv[i] = str(BrokenPath(arg))

# Safer measures: Store the first cwd that Broken is run, always start from there
os.chdir(os.environ.setdefault("BROKEN_PREVIOUS_WORKING_DIRECTORY", os.getcwd()))

# -------------------------------------------------------------------------------------------------|

_spinner.stop()
