# Plain functions definitions
from . import *

BROKEN_REQUESTS_CACHE = requests_cache.CachedSession(BROKEN_DIRECTORIES.CACHE/'RequestsCache')

def shell(*args, output=False, Popen=False, echo=True, confirm=False, do=True, **kwargs):
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works

    # Usage:
    - shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)

    # Parameters:
    - args:    The command to run, can be a list of arguments or a list of lists of arguments, don't care
    - output:  Whether to return the output of the command or not
    - Popen:   Whether to run and return the Popen object or not
    - echo:    Whether to print the command or not
    - confirm: Whether to ask for confirmation before running the command or not
    - do:      Whether to run the command or not, good for conditional commands
    """
    if output and Popen:
        raise ValueError("Cannot use output=True and Popen=True at the same time")

    # Flatten a list, remove falsy values, convert to strings
    command = [item for item in map(str, BrokenUtils.flatten(args)) if item]

    # Maybe print custom working directory
    if (cwd := kwargs.get("cwd", "")):
        cwd = f" @ ({cwd})"

    (log.info if do else log.minor)(("Running" if do else "Skipping") + f" command {command}{cwd}", echo=echo)

    if not do: return

    # Confirm running command or not
    if confirm and not rich.prompt.Confirm.ask(f"• Confirm running the command above"):
        return

    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

def BetterThread(callable, *args, start: bool=True, loop: bool=False, daemon: bool=False, **kwargs) -> Thread:
    """Create a thread on a callable, yeet whatever you think it works"""

    # Wrap callable on a loop
    if loop:
        original = copy.copy(callable)

        @functools.wraps(callable)
        def infinite_callable(*args, **kwargs):
            while True:
                original(*args, **kwargs)
        callable = infinite_callable

    thread = Thread(target=callable, daemon=daemon, args=args, kwargs=kwargs)
    if start: thread.start()
    return thread

def BrokenAppend(list: List[Any], item: Any, returns: Option["item", "list"]="item") -> List[Any]:
    """Appends an item to a list, returns the item"""
    list.append(item)
    return item if (returns == "item") else list

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

    def fuzzy_string_search(string: str, choices: List[str], many: int=1, minimum_score: int=0) -> list[tuple[str, int]]:
        """Fuzzy search a string in a list of strings, returns a list of matches"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            import thefuzz.process
            result = thefuzz.process.extract(string, choices, limit=many)
            if many == 1:
                return result[0]
            return result

    def get_free_tcp_port() -> int:
        """Get a unused TCP port"""
        temp_socket = socket.socket()
        temp_socket.bind(('', 0))
        return [temp_socket.getsockname()[1], temp_socket.close()][0]

    def get_environ_var(name: str, default: Any=None, cast: Any=None) -> Any:
        """Get an environment variable, cast it to a type, or return a default value"""
        value = os.environ.get(name, default)
        if cast:
            return cast(value)
        return value

    def add_method_to_self(method):
        """Add a method to the current scope's self"""

        # Find previous scope's self
        self = inspect.currentframe().f_back.f_locals.get("self", None)

        # Assert self is not None
        if self is None:
            log.error("Could not add method to self, are you in a class?")
            return

        # Add method to self
        setattr(self, method.__name__, method)

    def root_mean_square(x):
        return numpy.sqrt(numpy.mean(numpy.square(x)))

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

