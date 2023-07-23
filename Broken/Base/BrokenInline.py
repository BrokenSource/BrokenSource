# Plain functions definitions
from . import *

BROKEN_REQUESTS_CACHE = requests_cache.CachedSession(BROKEN_DIRECTORIES.CACHE/'RequestsCache')

def shell(*args, output=False, Popen=False, echo=True, confirm=False, **kwargs):
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works

    # Usage:
    - shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
    """
    if output and Popen:
        raise ValueError("Cannot use output=True and Popen=True at the same time")

    # Flatten a list, remove falsy values, convert to strings
    command = [item for item in map(str, BrokenUtils.flatten(args)) if item]

    info(f"Running command {command}", echo=echo)

    # Confirm running command or not
    if confirm and not rich.prompt.Confirm.ask(f"• Confirm running the command above"):
        return

    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

class BrokenUtils:
    def force_list(item: Union[Any, List[Any]]) -> List[Any]:
        """Force an item to be a list, if it's not already"""
        return item if (type(item) is list) else [item]

    def truthy(items: List[Any]) -> List[Any]:
        """Transforms a list into a truthy-only values list, removing all falsy values"""
        return [item for item in BrokenUtils.force_list(items) if item]

    def flatten(*stuff: Union[Any, List[Any]]) -> List[Any]:
        """
        Flatten nested lists and tuples to a single list
        [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
        """
        flatten = lambda stuff: [
            item for subitem in stuff for item in
            (flatten(subitem) if isinstance(subitem, (list, tuple)) else [subitem])
        ]
        return flatten(stuff)

def get_environ_var(name: str, default: Any=None, cast: Any=None) -> Any:
    """Get an environment variable, cast it to a type, or return a default value"""
    value = os.environ.get(name, default)
    if cast:
        return cast(value)
    return value

# # Weird classes

class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__singleton__"):
            cls.__singleton__ = super().__new__(cls)
        return cls.__singleton__

class EmptyCallable:
    """Well, an empty callable both initialization and __call__, eats up args and kwargs as well"""
    def __init__(self,*a,**b): ...
    def __call__(self,*a,**b): ...

def BrokenNeedImport(*packages: Union[str, List[str]]):
    """Check if a package is imported (required for project), else exit with error"""
    for name in packages:
        module = sys.modules.get(name, None)
        if (module is None) or isinstance(module, BrokenImportError):
            error(f"• Dependency {name} is required, maybe it's not installed on this virtual environment, not listed in BrokenImports or not imported")
            exit(1)
