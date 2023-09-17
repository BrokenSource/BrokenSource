# Lifelong utilities
from . import *

BROKEN_REQUESTS_CACHE = requests_cache.CachedSession(BROKEN_DIRECTORIES.CACHE/'RequestsCache')

# -------------------------------------------------------------------------------------------------|

def shell(
    *args: list[Any],
    output: bool=False,
    Popen: bool=False,
    echo: bool=True,
    confirm: bool=False,
    do:bool =True,
    **kwargs
):
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works

    Example:
    ```python
    shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
    ```

    Args:
        args (list[]):    The command to run, can be a list of arguments or a list of lists of arguments, don't care
        output:  Whether to return the output of the command or not
        Popen:   Whether to run and return the Popen object or not
        echo:    Whether to print the command or not
        confirm: Whether to ask for confirmation before running the command or not
        do:      Whether to run the command or not, good for conditional commands
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

# -------------------------------------------------------------------------------------------------|

class BrokenPlatform:
    # Name of the current platform
    Name      = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    OnLinux   = Name == "linux"
    OnWindows = Name == "windows"
    OnMacOS   = Name == "macos"
    OnBSD     = Name == "bsd"

    # Family of platforms
    OnUnix    = OnLinux or OnMacOS or OnBSD

    # Distros IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro = distro.id()

# -------------------------------------------------------------------------------------------------|

class Dummy:
    """
    A class that does nothing
    """
    def __init__(self,*a,**b): ...
    def __call__(self,*a,**b): ...
    def __getattr__(self,*a,**b): return self
    def __setattr__(self,*a,**b): return self
    def __delattr__(self,*a,**b): return self
    def __getitem__(self,*a,**b): return self
    def __setitem__(self,*a,**b): return self
    def __delitem__(self,*a,**b): return self
    def __iter__(self,*a,**b): return self
    def __next__(self,*a,**b): return self
    def __enter__(self,*a,**b): return self
    def __exit__(self,*a,**b): return self


# -------------------------------------------------------------------------------------------------|

# A class inside a class, huh
class BrokenStopwatch():
    """
    Context Manager or callable that counts the time it took to run

    ```python
    with BrokenUtils.BrokenStopwatch() as counter:
        took_so_far = counter.took
        ...

    # Stays at (finish - start) time after exiting
    print(counter.took)

    # Or use it as a callable
    counter = BrokenUtils.BrokenStopwatch()
    ...
    counter.took
    counter()
    ```
    """
    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def stop(self):
        self.end = time.time()

    def __call__(self):
        return self.time

    @property
    def time(self):
        return getattr(self, "end", time.time()) - self.start

# -------------------------------------------------------------------------------------------------|

class BrokenUtils:
    class Singleton:
        def __new__(cls, *args, **kwargs):
            if not hasattr(cls, "__singleton__"):
                cls.__singleton__ = super().__new__(cls)
            return cls.__singleton__

    def force_list(item: Union[Any, List[Any]]) -> List[Any]:
        """Force an item to be a list, if it's not already"""
        return item if (type(item) is list) else [item]

    def truthy(items: List[Any]) -> List[Any]:
        """Transforms a list into a truthy-only values list, removing all falsy values"""
        return [item for item in BrokenUtils.force_list(items) if item]

    def flatten(*stuff: Union[Any, List[Any]], truthy: bool=True) -> List[Any]:
        """
        Flatten nested lists and tuples to a single list
        [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
        """
        flatten = lambda stuff: [
            item for subitem in stuff for item in
            (flatten(subitem) if isinstance(subitem, (list, tuple)) else [subitem])
        ]
        return BrokenUtils.truthy(flatten(stuff)) if truthy else flatten(stuff)

    def denum(stuff: list[Any]) -> list[Any]:
        """Converts items of an list that are Enums to their values"""
        return [item.value if issubclass(item.__class__, Enum) else item for item in stuff]

    def fuzzy_string_search(string: str, choices: List[str], many: int=1, minimum_score: int=0) -> list[tuple[str, int]]:
        """Fuzzy search a string in a list of strings, returns a list of matches"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            import thefuzz.process
            result = thefuzz.process.extract(string, choices, limit=many)
            if many == 1:
                return result[0]
            return result

    def better_thread(callable, *args, start: bool=True, loop: bool=False, daemon: bool=False, **kwargs) -> Thread:
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
        """Calculate the root mean square of some array"""
        return numpy.sqrt(numpy.mean(numpy.square(x)))

    def polar_to_complex(r, theta):
        """Convert polar coordinates to a complex number"""
        return r * numpy.exp(1j * theta)

    @contextmanager
    def exit_on_keyboard_interrupt():
        """A context that exits the program on KeyboardInterrupt"""
        try:
            yield
        except KeyboardInterrupt:
            exit(0)

    def need_import(*packages: Union[str, List[str]]):
        """Check if a package is imported (required for project), else exit with error"""
        for name in packages:
            module = sys.modules.get(name, None)
            if (module is None) or isinstance(module, BrokenImportError):
                log.error(f"• Dependency {name} is required, maybe it's not installed on this virtual environment, not listed in BrokenImports or not imported")
                exit(1)

    def have_import(*packages: Union[str, List[str]]) -> bool:
        """Check if a package is imported (required for project), else exit with error"""
        for name in packages:
            module = sys.modules.get(name, None)
            if (module is None) or isinstance(module, BrokenImportError):
                return False
        return True

    def append_return(list: List[Any], item: Any, returns: Option["item", "list"]="item") -> List[Any]:
        """Appends an item to a list, returns the item"""
        list.append(item)
        return item if (returns == "item") else list

    def recurse(function: callable, **variables) -> Any:
        """
        Calls some function with the previous scope locals() updated by variables

        Use case are functions that are called recursively and need to be called with the same arguments

        ```python
        def function(with, many, arguments, and, only=3, one=True, modification="Nice"):
            ...
            if recurse_condition:
                BrokenUtils.recurse(function, many=True)
        ```
        """

        # Get the previous scope locals() and update it with the variables
        previous_locals = inspect.currentframe().f_back.f_locals
        previous_locals.update(variables)

        # Filter out variables that are not in the function arguments
        previous_locals = {
            k: v for k, v in previous_locals.items()
            if k in inspect.getfullargspec(function).args
            if k != "self"
        }

        # Call and return the same function
        return function(**previous_locals)

    def benchmark(
        function: callable,
        benchmark_name: str=None,
        benchmark_method: Option["duration", "executions"]="duration",

        # Duration arguments
        benchmark_duration: float=2,
        benchmark_executions: int=100,

        # Callable arguments
        *args, **kwargs
    ):
        frametimes = []

        with tqdm(
            total=benchmark_duration if (benchmark_method == "duration") else benchmark_executions,
            unit="s" if (benchmark_method == "duration") else "it",
            unit_scale=True,
            leave=False,
        ) as progress_bar:

            with BrokenUtils.BrokenStopwatch() as counter:
                while True:

                    # Call Function to benchmark
                    with BrokenUtils.BrokenStopwatch() as call_time:
                        function(*args, **kwargs)
                        frametimes.append(call_time.time)

                    # Update progress bar and check finish conditions
                    if benchmark_method == "duration":
                        progress_bar.n = min(counter.time, benchmark_duration)
                        if counter.time > benchmark_duration:
                            break

                    elif benchmark_method == "executions":
                        progress_bar.update(1)
                        if len(frametimes) > benchmark_executions:
                            break

                    # Update progress bar description
                    progress_bar.set_description(f"Benchmarking: {benchmark_name or function.__name__} ({len(frametimes)/sum(frametimes):.3f} it/s)")

        # # Get a few status
        frametimes = numpy.array(frametimes)

        f = lambda x: f"{x:.3f} it/s"
        log.info(f"• Benchmark Results for [{str(benchmark_name or function.__name__).ljust(20)}]: [Average {f(1.0/frametimes.mean())}] [Max {f(1.0/frametimes.min())}] [Min {f(1.0/frametimes.max())}] [Std {f((1/frametimes).std())}]")

    def sublist_in_list(sublist: List[Any], list: List[Any]) -> bool:
        """Check if a sublist is in a list"""
        return all(item in list for item in sublist)

    def extend(base: type, name: str=None, as_property: bool=False) -> type:
        """
        Extend a class with another classe's methods or a method directly.

        # Usage:
        Decorator of the class or method, class to extend as argument

        @BrokenUtils.extend(BaseClass)
        class ExtendedClass:
            def method(self):
                ...

        @BrokenUtils.extend(BaseClass)
        def method(self):
            ...

        @BrokenUtils.extend(BaseClass, as_property=True)
        def method(self):
            ...
        """
        def extender(add: type):

            # Extend as property
            if as_property:
                return BrokenUtils.extend(base, name=name, as_property=False)(property(add))

            # If add is a method
            if isinstance(add, types.FunctionType):
                setattr(base, name or add.__name__, add)
                return base

            # If it's a property
            if isinstance(add, property):
                setattr(base, name or add.fget.__name__, add)
                return base

            # If add is a class, add its methods to base
            for key, value in add.__dict__.items():
                if key.startswith("__"):
                    continue
                setattr(base, key, value)
                return base

        return extender

# -------------------------------------------------------------------------------------------------|

class BrokenPath:

    @contextmanager
    def PATH(
        directories: List[PathLike],
        recursive: bool=True,
        prepend: bool=True,
        clean: bool=False,
        restore: bool=True,
    ):
        """
        Temporarily limits the PATH to given directories
        - directories: List of directories to add to PATH
        - recursive: Whether to add subdirectories of given directories to PATH
        - prepend: Prioritize binaries found in input directories
        - restricted: Do not include current PATH in the new PATH
        """

        # Make Path objects
        directories = [Path(x) for x in BrokenUtils.force_list(directories)]

        # Get current PATH
        old = os.environ["PATH"]

        # List of all directories in PATH
        PATH = [] if clean else os.environ["PATH"].split(os.pathsep)

        # Add directories to PATH
        for directory in directories:
            PATH.append(directory)

            # Do not recurse if so
            if not recursive:
                continue

            # WARN: This could be slow on too many directories (wrong input?)
            # Find all subdirectories of a path
            for path in directory.rglob("*"):
                if path.is_dir():
                    if prepend:
                        PATH.insert(0, path)
                    else:
                        PATH.append(path)

        # Set new PATH
        os.environ["PATH"] = os.pathsep.join(map(str, PATH))

        yield os.environ["PATH"]

        # Restore PATH
        os.environ["PATH"] = old

    @staticmethod
    def get_binary(name: str, file_not_tagged_executable_workaround=True, echo=True) -> Option[Path, None]:
        """Get a binary from PATH"""

        # Get binary if on path and executable
        binary = shutil.which(name)

        # Workaround for files that are not set as executable: shutil will not find them
        # • Attempt finding directory/name for every directory in PATH
        if (binary is None) and file_not_tagged_executable_workaround :
            for directory in os.environ["PATH"].split(os.pathsep):
                if (maybe_the_binary := Path(directory)/name).is_file():
                    binary = maybe_the_binary
                    break

        # Print information about the binary
        if echo: (log.warning if (binary is None) else log.success)(f"• Binary [{str(name).ljust(20)}]: [{binary}]", echo=echo)

        return binary

    @staticmethod
    def binary_exists(name: str, echo=True) -> bool:
        """Check if a binary exists on PATH"""
        return BrokenPath.get_binary(name, echo=echo) is not None

    # # Specific / "Utils"

    @contextmanager
    def pushd(path: PathLike):
        """Change directory, then change back when done"""
        cwd = os.getcwd()
        os.chdir(path)
        yield path
        os.chdir(cwd)

    @staticmethod
    def true_path(path: PathLike) -> Path:
        return Path(path).expanduser().resolve().absolute()

    @staticmethod
    def make_executable(path: PathLike, echo=False) -> None:
        """Make a file executable"""
        path = Path(path)
        if BrokenPlatform.OnUnix:
            shell("chmod", "+x", path, echo=echo)

    # # File or directory creation

    @staticmethod
    def mkdir(path: PathLike, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        path = Path(path)
        if path.exists():
            log.success(f"Directory [{path}] already exists", echo=echo)
            return path
        log.info(f"Creating directory {path}", echo=echo)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def resetdir(path: PathLike, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        BrokenPath.remove(path, echo=echo)
        return BrokenPath.mkdir(path, echo=echo)

    @staticmethod
    def touch(path: PathLike, echo=True):
        """Creates a file, fail safe™"""
        path = Path(path)
        if path.exists():
            log.success(f"File [{path}] already exists", echo=echo)
            return
        log.info(f"Creating file {path}", echo=echo)
        path.touch()

    # # Data moving

    @staticmethod
    def copy(source: PathLike, destination: PathLike, echo=True) -> "destination":
        source, destination = Path(source), Path(destination)
        log.info(f"Copying [{source}] -> [{destination}]", echo=echo)
        shutil.copy2(source, destination)
        return destination

    @staticmethod
    def move(source: PathLike, destination: PathLike, echo=True) -> "destination":
        source, destination = Path(source), Path(destination)
        log.info(f"Moving [{source}] -> [{destination}]", echo=echo)
        shutil.move(source, destination)
        return destination

    @staticmethod
    def remove(path: PathLike, confirm=False, echo=True) -> bool:
        path = Path(path)
        log.info(f"• Removing Path ({confirm=}) [{path}]", echo=echo)

        if not path.exists():
            log.success(f"└─ Does not exist", echo=echo)
            return False

        # Symlinks are safe to remove
        if path.is_symlink():
            path.unlink()
            log.success(f"└─ Removed Symlink", echo=echo)
            return True

        # Confirm removal: directory contains data
        if confirm and (not rich.prompt.Confirm.ask(f"• Confirm removing path ({path})")):
            return False

        # Remove the path
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            log.success(f"└─ Removed Directory", echo=echo)
        else:
            path.unlink()
            log.success(f"└─ Removed File", echo=echo)

        return True

    @staticmethod
    def open_in_file_explorer(path: PathLike):
        """Opens a path in the file explorer"""
        path = Path(path)
        if BrokenPlatform.OnWindows:
            os.startfile(str(path))
        elif BrokenPlatform.OnLinux:
            shell("xdg-open", path)
        elif BrokenPlatform.OnMacOS:
            shell("open", path)

    @staticmethod
    def symlink(where: Path, to: Path, echo=True):
        """Symlink [where] -> [to], `where` being the symlink and `to` the target

        Args:
            where (Path): Symlink path
            to (Path): Target path

        Returns:
            None
        """
        log.info(f"Symlinking [{to}] -> [{where}]", echo=echo)

        # Make parent directory
        BrokenPath.mkdir(to.parent, echo=False)

        # Remove old symlink
        if to.is_symlink():
            to.unlink()

        # Error: `where` is a existing file or directory
        if to.exists():
            log.error(f"Path [{to}] exists and isn't a symlink")
            return

        to.symlink_to(where)

class ShellCraft:

    # Current shell name (binary path)
    SHELL_BINARY = os.environ.get("SHELL", "unknown")

    # Booleans if the current shell is the following
    BASH       = "bash" in SHELL_BINARY
    ZSH        = "zsh"  in SHELL_BINARY
    FISH       = "fish" in SHELL_BINARY
    Unknown    = (not (BASH or ZSH or FISH)) or (SHELL_BINARY == "unknown")

    def add_path_to_system_PATH(path: PathLike, echo=True) -> bool:
        """Add a path to the system PATH _ideally_ for all platforms. Sincerely, f-pointer-comment-at this function"""
        path = Path(path)

        # If the path is already in the system path, no work to do
        if str(path) in os.environ.get("PATH", "").split(os.pathsep):
            log.success(f"Path [{path}] already in PATH", echo=echo)
            return True

        # Unix is complicated, ideally one would put on /etc/profile but it's only reloaded on logins
        # The user shell varies a lot, but most are in BASH, ZSH or FISH apparently, but need sourcing or restarting
        if BrokenPlatform.OnUnix:

            # The export line adding to PATH the wanted path
            export = f"export PATH={path}:$PATH"

            # Add the export line based on the current shell
            for current_shell, shellrc in [
                (ShellCraft.BASH,    HOME_DIR/".bashrc"                 ),
                (ShellCraft.ZSH,     HOME_DIR/".zshrc"                  ),
                # (ShellCraft.FISH,    HOME_DIR/".config/fish/config.fish"),
                (ShellCraft.Unknown, HOME_DIR/".profile")
            ]:
                # Skip if not on this chell
                if not current_shell: continue

                # Info on what's going on
                if ShellCraft.Unknown:
                    log.error(f"Your shell is unknown and PATH will be re-exported in [{shellrc}], you need to log out and log in for changes to take effect, go touch some grass..   (PRs are welcome!)", echo=echo)

                log.info(f"Your current shell is [{ShellCraft.SHELL_BINARY}], adding the directory [{path}] to PATH in the shell rc file [{shellrc}] as [{export}]", echo=echo)

                # Add the export line to the shell rc file
                with open(shellrc, "a") as file:
                    file.write(f"{export}\n")

            # Need to restart the shell or source it
            log.warning(f"Please restart your shell for the changes to take effect or run [source {shellrc}] or [. {shellrc}] on current one, this must be done since a children process (Python) can't change the parent process (your shell) environment variables plus the [source] or [.] not binaries but shell builtins")

        # No clue if this works.
        elif BrokenPlatform.OnWindows:
            log.fixme("I don't know if the following reg command works for adding a PATH to PATH on Windows")
            shell("reg", "add", r"HKCU\Environment", "/v", "PATH", "/t", "REG_SZ", "/d", f"{path};%PATH%", "/f")
            shell("refreshenv")

        else:
            log.error(f"Unknown Platform [{BrokenPlatform.Name}]")
            return False

        return True

# -------------------------------------------------------------------------------------------------|

@attrs.define
class BrokenRelay:
    """
    A class to bind, passthrough some callback to many callables.

    Useful for ModernGL window function, eg pseudocode:

    ```python
    window = moderngl_window(...)

    # Create BrokenRelay instance
    scroll_callbacks = BrokenRelay()

    # Map window scroll func callback to this class
    window.mouse_scroll_event_func = scroll_callbacks

    # Define many callbacks that should be called on window resize
    def log_scroll(x, y):
        ...

    camera2d = Camera2D(...)

    # Add callbacks
    scroll_callbacks.bind(log_scroll, camera2d.resize)

    # Or with @ syntax
    scroll_callbacks @ (log_scroll, camera2d.resize)

    # It also returns self when binding
    self.window_mouse_scroll_event_func = scroll_callbacks @ (log_scroll, camera2d.resize)
    ```
    """
    callbacks: list[callable] = attrs.Factory(list)

    def __bind__(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        self.callbacks += BrokenUtils.flatten(callbacks)
        return self

    def bind(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        return self.__bind__(*callbacks)

    def __matmul__(self, *callbacks: callable) -> Self:
        """Convenience syntax for binding"""
        return self.__bind__(*callbacks)

    def __call__(self, *args, **kwargs):
        """Pass through all callbacks to who called "us" (self)"""
        for callback in self.callbacks:
            callback(*args, **kwargs)

# -------------------------------------------------------------------------------------------------|

@contextmanager
def BrokenNullContext():
    """A context that does nothing"""
    yield Dummy()

class BrokenSmart:
    def load_image(image: Union[PilImage, PathLike, URL], pixel="RGB", cache=True, echo=True) -> Option[PilImage, None]:
        """Smartly load 'SomeImage', a path, url or PIL Image"""

        # Nothing to do if already a PIL Image
        if isinstance(image, PilImage):
            return image

        try:
            # Load image if a path or url is supplied
            if any([isinstance(image, T) for T in (PathLike, str)]):
                if (path := BrokenPath.true_path(image)).exists():
                    log.info(f"Loading image from Path [{path}]", echo=echo)
                    return PIL.Image.open(path).convert(pixel)
                else:
                    log.info(f"Loading image from (maybe) URL [{image}]", echo=echo)
                    try:
                        requests = BROKEN_REQUESTS_CACHE if cache else requests
                        return PIL.Image.open(BytesIO(requests.get(image).content)).convert(pixel)
                    except Exception as e:
                        log.error(f"Failed to load image from URL or Path [{image}]: {e}", echo=echo)
                        return None
            else:
                log.error(f"Unknown image parameter [{image}], must be a PIL Image, Path or URL", echo=echo)
                return None

        # Can't open file
        except Exception as e:
            log.error(f"Failed to load image [{image}]: {e}", echo=echo)
            return None

# -------------------------------------------------------------------------------------------------|

@attrs.define
class BrokenVsyncClient:
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
    - dt:         Whether to pass dt (time since last call) to callback
    - time:       Whether to pass time (time since first call) to callback
    """
    callback:   callable = None
    name:       str      = None
    args:       List[Any] = []
    kwargs:     Dict[str, Any] = {}
    frequency:  float    = 60
    context:    Any      = None
    enabled:    bool     = False
    next_call:  float    = 0
    dt:         bool     = False
    time:       float    = 0
    started:    float    = None
    last_call:  float = None

@attrs.define
class BrokenVsync:
    clients: List[BrokenVsyncClient] = []
    __thread__: Option[Thread, None] = None
    __stop__:   bool = False

    def add_client(self, client: BrokenVsyncClient) -> BrokenVsyncClient:
        """Adds a client to the manager with immediate next call"""
        client.next_call += time.time()
        client.started = time.time()
        self.clients.append(client)
        return client

    def get_client(self, name: str) -> Option[BrokenVsyncClient, None]:
        """Gets a client by name"""
        return next((client for client in self.clients if client.name == name), None)

    def new(self, *args, **kwargs) -> BrokenVsyncClient:
        """Wraps around BrokenVsync for convenience"""
        return self.add_client(BrokenVsyncClient(*args, **kwargs))

    def next(self, block=True) -> Option[None, Any]:
        """Calls the next call client in the list"""
        client = sorted(self.clients, key=lambda item: item.next_call*(item.enabled))[0]

        # Time to wait for next call if block
        # - Next call at 110 seconds, now=100, wait=10
        # - Positive means to wait, negative we are behind
        wait = client.next_call - time.time()

        # Wait for next call time if blocking
        if block:
            time.sleep(max(0, wait))

        # Non blocking mode, if we are not behind do nothing
        elif not (wait < 0):
            return None

        # The assumed instant the code below will run instantly
        now = time.time()

        # Delta time between last call and next call
        if client.dt:
            client.kwargs["dt"] = now - (client.last_call or now)
            client.last_call = now

        # Time since client started
        if client.time:
            client.kwargs["time"] = now - client.started

        # Add periods until next call is in the future
        while client.next_call <= now:
            client.next_call += 1/client.frequency

        # Enter or not the given context, call callback with args and kwargs
        with (client.context or BrokenNullContext()):
            return client.callback(*client.args, **client.kwargs)

    # # Thread-wise wording

    def start_thread(self) -> None:
        self.__stop__   = False
        self.__thread__ = BrokenUtils.better_thread(self.loop)

    def stop_thread(self):
        self.__stop__   = True
        self.__thread__._stop()

    # # "Natural" wording?

    def loop(self) -> None:
        while not self.__stop__:
            self.next()

    def stop(self):
        self.__stop__ = True

    def start(self):
        self.__stop__ = False
        self.loop()

# -------------------------------------------------------------------------------------------------|

class BrokenEnum(Enum):

    @classmethod
    def smart(cls, value: Union[str, Enum]):
        """Get enum member from string name, value or enum"""

        # Value already a member of the enum
        if isinstance(value, cls):
            return value

        try:
            # Try finding the member by name
            for member in cls:
                if isinstance(member.value, (list, tuple)):
                    if value in member.value:
                        return member
                elif member.value == value:
                    return member

            return cls[value]
        except KeyError:
            log.error(f"No such value [{value}] on Enum class [{cls.__name__}]")
            raise ValueError

    @classmethod
    @property
    def options(cls) -> List[Enum]:
        """Get all members of the enum"""
        return list(cls)

    @classmethod
    @property
    def values(cls) -> List[Any]:
        """Get all values of the enum"""
        return [member.value for member in cls]