# Plain functions definitions
from . import *

BROKEN_REQUESTS_CACHE = requests_cache.CachedSession(BROKEN_DIRECTORIES.CACHE/'RequestsCache')

# Flatten nested lists and tuples to a single list
# [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
flatten_list = lambda stuff: [
    item for sub in stuff for item in
    (flatten_list(sub) if type(sub) in (list, tuple) else [sub])
]

# shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True)
def shell(*args, output=False, Popen=False, echo=True, **kwargs):
    if output and Popen:
        raise ValueError("Cannot use output=True and Popen=True at the same time")

    # Flatten a list, remove falsy values, convert to strings
    command = [item for item in map(str, flatten_list(args)) if item]
    info(f"Running command {command}", echo=echo)

    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

def enforce_list(item: Union[Any, List[Any]]) -> List[Any]:
    return item if (type(item) is list) else [item]

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