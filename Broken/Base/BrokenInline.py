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

    # Maybe print custom working directory
    if (cwd := kwargs.get("cwd", "")):
        cwd = f" @ ({cwd})"

    info(f"Running command {command}{cwd}", echo=echo)

    # Confirm running command or not
    if confirm and not rich.prompt.Confirm.ask(f"• Confirm running the command above"):
        return

    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

def BetterThread(callable, *args, start=True, **kwargs):
    """Create a thread on a callable, yeet whatever you think it works"""
    return Thread(target=callable, args=args, kwargs=kwargs)

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

class Dummy:
    """Well, an empty callable both initialization and __call__, eats up args and kwargs as well, does nothing"""
    def __init__(self,*a,**b): ...
    def __call__(self,*a,**b): ...

def BrokenNeedImport(*packages: Union[str, List[str]]):
    """Check if a package is imported (required for project), else exit with error"""
    for name in packages:
        module = sys.modules.get(name, None)
        if (module is None) or isinstance(module, BrokenImportError):
            error(f"• Dependency {name} is required, maybe it's not installed on this virtual environment, not listed in BrokenImports or not imported")
            exit(1)

@contextmanager
def BrokenExitOnKeyboardInterrupt():
    """A context that exits the program on KeyboardInterrupt"""
    try:
        yield
    except KeyboardInterrupt:
        exit(0)

@contextmanager
def BrokenNullContext():
    """A context that does nothing"""
    yield Dummy()

@attrs.define
class BrokenVsync:
    """
    Client configuration for BrokenVsyncManager

    # Function:
    - callback:   Function callable to call every syncronization
    - args:       Arguments to pass to callback
    - kwargs:     Keyword arguments to pass to callback
    - context:    Context to use when calling callback (with statement)

    # Timing:
    - frequency:  Frequency of callback calls
    - enabled:    Whether to enable this client or not
    - next_call:  Next time to call callback (initializes $now+next_call, value in now() seconds)
    """
    callback:   callable = None
    args:       List[Any] = []
    kwargs:     Dict[str, Any] = {}
    frequency:  float    = 60
    context:    Any      = None
    enabled:    bool     = False
    next_call:  float    = 0

@attrs.define
class BrokenVsyncManager:
    clients: List[BrokenVsync] = []

    def add(self, client: BrokenVsync) -> BrokenVsync:
        client.next_call += now()
        self.clients.append(client)
        return client

    def next(self, block=True) -> Option[None, Any]:
        client = sorted(self.clients, key=lambda item: item.next_call*(item.enabled))[0]

        # Time to wait for next call if block
        # - Next call at 110 seconds, now=100, wait=10
        # - Positive means to wait, negative we are behind
        wait = client.next_call - now()

        # Wait for next call time if blocking
        if block:
            time.sleep(max(0, wait))

        # Non blocking mode, if we are not behind do nothing
        elif not (wait < 0):
            return None

        # Keep adding periods until next call is on the future
        while client.next_call < now():
            client.next_call += 1/client.frequency

        # Enter or not the given context, call callback with args and kwargs
        with (client.context or BrokenNullContext()):
            return client.callback(*client.args, **client.kwargs)
