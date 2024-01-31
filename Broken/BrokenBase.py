from __future__ import annotations

from . import *

# -------------------------------------------------------------------------------------------------|

def shell(
    *args:   list[Any],
    output:  bool=False,
    Popen:   bool=False,
    shell:   bool=False,
    echo:    bool=True,
    confirm: bool=False,
    do:      bool=True,
    **kwargs
) -> None | str | subprocess.Popen | subprocess.CompletedProcess:
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works

    Example:
        ```python
        shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
        ```

    Args:
        `args`:    The command to run, can be a list of arguments or a list of lists of arguments, don't care
        `output`:  Whether to return the output of the command or not
        `Popen`:   Whether to run and return the Popen object or not
        `echo`:    Whether to print the command or not
        `confirm`: Whether to ask for confirmation before running the command or not
        `do`:      Whether to run the command or not, good for conditional commands

    Kwargs:
        `cwd`: Current working directory for the command
        `env`: Environment variables for the command
        `*:`   Any other keyword arguments are passed to subprocess.*
    """
    if output and Popen:
        raise ValueError("Cannot use output=True and Popen=True at the same time")

    # Flatten a list, remove falsy values, convert to strings
    command = tuple(map(str, BrokenUtils.flatten(args)))

    if shell:
        log.warning("Running command with shell=True, be careful")
        kwargs["shell"] = shell
        command = ' '.join(command)

    # Assert command won't fail due unknown binary
    if (not shell) and (not shutil.which(command[0])):
        log.error(f"Binary doesn't exist or was not found on PATH ({command[0]})")
        return

    # Get the current working directory
    cwd = f" @ ({kwargs.get('cwd', '') or Path.cwd()})"

    (log.info if do else log.skip)(("Running" if do else "Skipping") + f" command {command}{cwd}", echo=echo)

    if not do: return

    # Confirm running command or not
    if confirm and not click.confirm(f"• Confirm running the command above"):
        return

    # Get current environment variables
    env = os.environ.copy() | kwargs.get("env", {})

    # Run the command and return specified object
    if output: return subprocess.check_output(command, env=env, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, env=env, **kwargs)
    else:      return subprocess.run(command, env=env, **kwargs)

# -------------------------------------------------------------------------------------------------|

class BrokenPlatform:

    # Name of the current platform - (linux, windows, macos, bsd)
    Name:         str  = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    OnLinux:      bool = (Name == "linux")
    OnWindows:    bool = (Name == "windows")
    OnMacOS:      bool = (Name == "macos")
    OnBSD:        bool = (Name == "bsd")

    # Platform release binaries extension and CPU architecture
    Extension:    str  = ".exe" if OnWindows else ".bin"
    Architecture: str  = (platform.machine().lower()
        .replace("x86_64", "amd64")
    )

    # Family of platforms
    OnUnix:       bool = (OnLinux or OnMacOS or OnBSD)

    # Distros IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro:  str  = distro.id()

    # # Booleans if the current platform is the following

    # Ubuntu-like
    OnUbuntu:     bool = (LinuxDistro == "ubuntu")
    OnDebian:     bool = (LinuxDistro == "debian")
    OnMint:       bool = (LinuxDistro == "linuxmint")
    OnRaspberry:  bool = (LinuxDistro == "raspbian")
    OnUbuntuLike: bool = (OnUbuntu or OnDebian or OnMint or OnRaspberry)

    # Arch-like
    OnArch:       bool = (LinuxDistro == "arch")
    OnManjado:    bool = (LinuxDistro == "manjaro")
    OnArchLike:   bool = (OnArch or OnManjado)

    # RedHat-like
    OnFedora:     bool = (LinuxDistro == "fedora")
    OnCentOS:     bool = (LinuxDistro == "centos")
    OnRedHat:     bool = (LinuxDistro == "rhel")
    OnRedHatLike: bool = (OnFedora or OnCentOS or OnRedHat)

    # Others
    OnGentoo:     bool = (LinuxDistro == "gentoo")

    # BSD - I have never used it
    OnOpenBSD:    bool = (LinuxDistro == "openbsd")
    OnNetBSD:     bool = (LinuxDistro == "netbsd")
    OnBSDLike:    bool = (OnOpenBSD or OnNetBSD)

    class Targets(BrokenEnum):
        """List of common platforms targets for releases"""
        LinuxAMD64:   str = "linux-amd64"
        LinuxARM:     str = "linux-arm64"
        WindowsAMD64: str = "windows-amd64"
        WindowsARM:   str = "windows-arm64"
        MacOSAMD64:   str = "macos-amd64"
        MacOSARM:     str = "macos-arm64"

    CurrentTarget:    str = f"{Name}-{Architecture}"

    @staticmethod
    def clear_terminal(**kwargs):
        if BrokenPlatform.OnWindows:
            if kwargs.get("do", True):
                os.system("cls")
        else:
            shell("clear", **kwargs)

    @staticmethod
    def log_system_info():
        log.info(f"• System Info: {platform.system()} {platform.release()}, Python {platform.python_version()} {platform.machine()}")

# -------------------------------------------------------------------------------------------------|

class BrokenPath:

    @contextmanager
    def PATH(*,
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
    def get_binary(name: str, file_not_tagged_executable_workaround=True, *, echo=True) -> Optional[Path]:
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
        if echo: (log.warning if (binary is None) else log.success)(f"• Binary ({name}) found at ({binary})", echo=echo)

        return binary

    # # File or directory creation

    @staticmethod
    def mkdir(path: PathLike, parent: bool=False, *, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        path = BrokenPath.true_path(path)
        path = path.parent if parent else path
        if path.exists():
            log.success(f"Directory ({path}) already exists", echo=echo)
            return path
        log.info(f"Creating directory {path}", echo=echo)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def resetdir(path: PathLike, *, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        BrokenPath.remove(path, echo=echo)
        return BrokenPath.mkdir(path, echo=echo)

    @staticmethod
    def touch(path: PathLike, *, echo=True):
        """Creates a file, fail safe™"""
        path = Path(path)
        if path.exists():
            log.success(f"File ({path}) already exists", echo=echo)
            return
        log.info(f"Creating file {path}", echo=echo)
        path.touch()

    # # Data moving

    @staticmethod
    def copy(source: PathLike, destination: PathLike, *, echo=True) -> "destination":
        source, destination = Path(source), Path(destination)
        log.info(f"Copying ({source}) -> ({destination})", echo=echo)
        BrokenPath.mkdir(destination.parent, echo=echo)
        shutil.copy2(source, destination)
        return destination

    @staticmethod
    def move(source: PathLike, destination: PathLike, *, echo=True) -> "destination":
        source, destination = Path(source), Path(destination)
        log.info(f"Moving ({source}) -> ({destination})", echo=echo)
        shutil.move(source, destination)
        return destination

    @staticmethod
    def remove(path: PathLike, *, confirm=False, echo=True) -> Path:
        path = BrokenPath.true_path(path)
        log.info(f"Removing Path ({path})", echo=echo)

        # Safety: Must not be common
        if path in (Path.cwd(), Path.home()):
            log.error(f"Avoided catastrophic failure by not removing ({path})")
            exit(1)

        # Already removed
        if not path.exists():
            return path

        # Symlinks are safe to remove
        if path.is_symlink():
            path.unlink()
            return path

        # Confirm removal: directory contains data
        if confirm and (not click.confirm(f"• Confirm removing path ({path})")):
            return path

        # Remove the path
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()

        return path

    # # Specific / "Utils"

    @contextmanager
    def pushd(path: PathLike, *, echo: bool=True) -> Path:
        """Change directory, then change back when done"""
        path = BrokenPath.true_path(path)
        cwd = os.getcwd()
        log.info(f"Pushd ({path})", echo=echo)
        os.chdir(path)
        yield path
        log.info(f"Popd  ({path})", echo=echo)
        os.chdir(cwd)

    @staticmethod
    def true_path(path: PathLike) -> Optional[Path]:
        return Path(path).expanduser().resolve() if path else None

    @staticmethod
    def make_executable(path: PathLike, *, echo=False) -> Path:
        """Make a file executable"""
        path = Path(path)
        if BrokenPlatform.OnUnix:
            shell("chmod", "+x", path, echo=echo)
        elif BrokenPlatform.OnWindows:
            shell("attrib", "+x", path, echo=echo)
        return path

    @staticmethod
    def open_in_file_explorer(path: PathLike):
        """Opens a path in the file explorer"""
        path = BrokenPath.true_path(path)
        if BrokenPlatform.OnWindows:
            os.startfile(str(path))
        elif BrokenPlatform.OnLinux:
            shell("xdg-open", path)
        elif BrokenPlatform.OnMacOS:
            shell("open", path)

    @staticmethod
    def symlink(virtual: Path, real: Path, *, echo: bool=True) -> Path:
        """
        Symlink [virtual] -> [real], `virtual` being the symlink file and `real` the target

        Args:
            virtual (Path): Symlink path (file)
            real (Path): Target path (real path)

        Returns:
            None if it fails, else `virtual` Path
        """
        log.info(f"Symlinking ({virtual}) -> ({real})", echo=echo)

        # Return if already symlinked
        if (BrokenPath.true_path(virtual) == BrokenPath.true_path(real)):
            return virtual

        # Make Virtual's parent directory
        BrokenPath.mkdir(virtual.parent, echo=False)

        # Remove old symlink if it points to a non existing directory
        if virtual.is_symlink() and (not virtual.resolve().exists()):
            virtual.unlink()

        # Virtual doesn't exist, ok to create
        elif not virtual.exists():
            pass

        # File exists and is a symlink - safe to remove
        elif virtual.is_symlink():
            virtual.unlink()

        # Virtual is a directory and not empty
        elif virtual.is_dir() and (not os.listdir(virtual)):
            BrokenPath.remove(virtual, echo=False)

        else:
            if click.confirm(f"• Path ({virtual}) exists, but Broken wants to create a symlink to ({real})\nConfirm removing it and continuing? (It might contain data or be a important symlink)"):
                BrokenPath.remove(virtual, echo=False)
            else:
                return

        # Actually symlink
        virtual.symlink_to(real)
        return virtual

    @staticmethod
    def zip(path: Path, output: Path=None, echo: bool=True) -> Path:
        """
        Zip a directory

        Args:
            path (Path): Path to zip
            output (Path): Output path, defaults to path with .zip extension

        Returns:
            Path: The zipped file's path
        """
        path = Path(path)

        # Default output to path with .zip extension
        output = (Path(output) if output else path).with_suffix(".zip")

        # Remove old zip
        BrokenPath.remove(output, echo=echo)

        # Make the new zip
        log.info(f"Zipping ({path}) -> ({output})", echo=echo)
        shutil.make_archive(output.with_suffix(""), "zip", path)

        return output

    @staticmethod
    def on_path(path: PathLike) -> bool:
        """Check if a path is on PATH, works with symlinks"""
        return BrokenPath.true_path(path) in map(BrokenPath.true_path, os.environ.get("PATH", "").split(os.pathsep))

    @staticmethod
    def add_to_path(path: PathLike, *, echo: bool=True) -> Path:
        """Add a path to PATH"""
        path = BrokenPath.true_path(path)

        # Skip already on PATH
        if BrokenPath.on_path(path):
            log.skip(f"Path ({path}) is already on PATH", echo=echo)
            return path

        # Actually add to PATH
        log.warning(f"Path ({path}) was added to PATH. Please, restart the Terminal to take effect", echo=echo)
        __import__("userpath").append(str(path))
        return path

    @staticmethod
    def non_empty_file(path: Path) -> bool:
        return path.exists() and path.is_file() and path.stat().st_size > 0

    @staticmethod
    def empty_file(path: Path, create: bool=True) -> bool:
        if create and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return path.exists() and path.is_file() and len(path.read_text()) == 0

    @staticmethod
    def empty_path(path: Path) -> bool:
        return not path.exists()

# -------------------------------------------------------------------------------------------------|

class BrokenUtils:

    @staticmethod
    def force_list(item: Union[Any, List[Any]]) -> List[Any]:
        """Force an item to be a list, if it's not already"""
        return item if (type(item) is list) else [item]

    @staticmethod
    def truthy(items: List[Any]) -> List[Any]:
        """Transforms a list into a truthy-only values list, removing all falsy values"""
        return [item for item in BrokenUtils.force_list(items) if item]

    @staticmethod
    def flatten(*stuff: Union[Any, List[Any]], truthy: bool=True) -> List[Any]:
        """
        Flatten nested list like iterables to a 1D list
        [[a, b], c, [d, e, (None, 3)], [g, h]] -> [a, b, c, d, e, None, 3, g, h]
        """
        flatten = lambda stuff: [
            item for subitem in stuff for item in
            (flatten(subitem) if isinstance(subitem, (list, tuple)) else [subitem])
        ]
        return BrokenUtils.truthy(flatten(stuff)) if truthy else flatten(stuff)

    @staticmethod
    def denum(stuff: Iterable[Any]) -> list[Any]:
        """De-enumerates enum iterables to their value"""
        return [item.value if issubclass(type(item), Enum) else item for item in stuff]

    @staticmethod
    def fuzzy_string_search(string: str, choices: List[str], many: int=1, minimum_score: int=0) -> list[tuple[str, int]]:
        """Fuzzy search a string in a list of strings, returns a list of matches"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            import thefuzz.process
            result = thefuzz.process.extract(string, choices, limit=many)
            if many == 1:
                return result[0]
            return result

    @staticmethod
    def recurse(function: callable, **variables) -> Any:
        """
        Calls some function with the previous scope locals() updated by variables
        # Note: Not a fast method, consider using for convenience only

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

    @staticmethod
    def sublist_in_list(sublist: List[Any], list: List[Any]) -> bool:
        """Check if a sublist is in a list"""
        return all(item in list for item in sublist)

    @staticmethod
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

    @staticmethod
    def load_image(
        image: Image | PathLike | URL,
        pixel="RGB",
        *,
        cache=True,
        echo=True
    ) -> Option[Image, None]:
        """Smartly load 'SomeImage', a path, url or PIL Image"""
        # Todo: Maybe a BrokenImage class with some utils?

        # Can't load the Image class
        if image is Image:
            return None

        # Nothing to do if already a PIL Image
        elif isinstance(image, Image):
            return image

        try:
            # Load image if a path or url is supplied
            if isinstance(image, (PathLike, str)):
                if (path := BrokenPath.true_path(image)).exists():
                    log.info(f"Loading image from Path ({path})", echo=echo)
                    return PIL.Image.open(path).convert(pixel)
                else:
                    if not validate.url(str(image)):
                        return None

                    log.info(f"Loading image from URL ({image})", echo=echo)
                    try:
                        import requests
                        return PIL.Image.open(BytesIO(requests.get(image).content)).convert(pixel)
                    except Exception as e:
                        log.error(f"Failed to load image from URL or Path ({image}): {e}", echo=echo)
                        return None
            else:
                log.error(f"Unknown image parameter ({image}), must be a PIL Image, Path or URL", echo=echo)
                return None

        # Can't open file
        except Exception as e:
            log.error(f"Failed to load image ({image}): {e}", echo=echo)
            return None

    @staticmethod
    def have_import(module: str) -> bool:
        """Check if a module has been imported"""
        return module in sys.modules

    @staticmethod
    def relaunch(*, safe: int=3, echo: bool=True) -> subprocess.CompletedProcess:
        """
        Relaunch the current process with the same arguments up until a `safe` recursion
        """
        key = "BROKEN_RELAUNCH_INDEX"

        # Get and assert safe recursion level
        if (level := int(os.environ.get(key, 0))) >= safe:
            log.error(f"Reached maximum relaunch recursion depth ({safe}), aborting")
            exit(1)

        # Increment relaunch index
        os.environ[key] = str(level + 1)

        log.info(f"Relaunching self process with arguments ({sys.argv})", echo=echo)
        return shell(sys.executable, sys.argv, echo=echo)

    @staticmethod
    def sha256sum(data: Union[Path, bytes]) -> str:
        """Get the sha256sum of a file or bytes"""
        if isinstance(data, Path):
            return BrokenUtils.sha256sum(data.read_bytes())
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def is_dunder(name: str) -> bool:
        return name.startswith("__") and name.endswith("__")

# -------------------------------------------------------------------------------------------------|

@define
class BrokenThreadPool:
    threads: List[Thread] = []
    max:     int          = 1

    @property
    def alive(self) -> List[Thread]:
        return list(filter(lambda thread: thread.is_alive(), self.threads))

    @property
    def n_alive(self) -> int:
        return len(self.alive)

    def sanitize(self) -> None:
        self.threads = self.alive

    def append(self, thread: Thread, wait: float=0.01) -> Thread:
        while self.n_alive >= self.max:
            time.sleep(wait)
        self.sanitize()
        self.threads.append(thread)
        return thread

    def join(self) -> None:
        for thread in self.threads:
            thread.join()

@define
class BrokenThread:
    pools = {}

    @staticmethod
    def pool(name: str) -> BrokenThreadPool:
        return BrokenThread.pools.setdefault(name, BrokenThreadPool())

    @staticmethod
    def new(
        callable,
        *args,
        start: bool=True,
        loop: bool=False,
        pool: str=None,
        max: int=1,
        **kwargs
    ) -> Thread:
        """
        Create a thread on a callable, yeet whatever you think it works
        • Support for a basic Thread Pool, why no native way?

        Args:
            callable: The function to call, consider using functools.partial
            args:     Arguments to pass to the function
            kwargs:   Keyword arguments to pass to the function
            start:    Whether to immediately start the thread or not
            loop:     Whether to loop the callable or not (non blocking)
            pool:     Name of the pool to append the thread to, see BrokenThreadPool
            max:      Maximum threads in the pool

        Returns:
            Thread: The created thread
        """

        # Wrap callable on a loop
        if loop:
            original = copy.copy(callable)

            @functools.wraps(callable)
            def infinite_callable(*args, **kwargs):
                while True:
                    original(*args, **kwargs)
            callable = infinite_callable

        # Create Thread object
        thread = Thread(target=callable, args=args, kwargs=kwargs)

        # Maybe wait for the pool to be free
        if pool and (pool := BrokenThread.pools.setdefault(pool, BrokenThreadPool(max=max))):
            pool.append(thread)

        thread.start() if start else None
        return thread

# -------------------------------------------------------------------------------------------------|

@define
class BrokenEventClient:
    """
    Client configuration for BrokenEventLoop

    # Function:
    - callback:   Function callable to call every syncronization
    - args:       Arguments to pass to callback
    - kwargs:     Keyword arguments to pass to callback
    - output:     Output of callback (returned value)
    - context:    Context to use when calling callback (with statement)
    - lock:       Lock to use when calling callback (with statement)
    - enabled:    Whether to enable this client or not
    - once:       Whether to call this client only once or not

    # Syncronization
    - frequency:  Frequency of callback calls
    - frameskip:  Constant deltatime mode (False) or real deltatime mode (True)
    - decoupled:  "Rendering" mode, do not sleep on real time, implies frameskip False

    # Timing:
    - next_call:  Next time to call callback (initializes $now+next_call, value in now() seconds)
    - last_call:  Last time callback was called (initializes $now+last_call, value in now() seconds)
    - started:    Time when client was started (initializes $now+started, value in now() seconds)
    - time:       Whether to pass time (time since first call) to callback
    - dt:         Whether to pass dt (time since last call) to callback
    """

    # Callback
    callback:   callable       = None
    args:       List[Any]      = Factory(list)
    kwargs:     Dict[str, Any] = Factory(dict)
    output:     Any            = None
    context:    Any            = None
    lock:       threading.Lock = None
    enabled:    bool           = True
    once:       bool           = False

    # Syncronization
    frequency:  float          = 60
    frameskip:  bool           = True
    decoupled:  bool           = False

    # Timing:
    next_call:  float          = Factory(lambda: time.perf_counter())
    last_call:  float          = Factory(lambda: time.perf_counter())
    started:    float          = Factory(lambda: time.perf_counter())
    time:       bool           = False
    dt:         bool           = False

    # # Useful properties

    @property
    def fps(self) -> Union[float, "hertz"]:
        return self.frequency

    @fps.setter
    def fps(self, value: Union[float, "hertz"]):
        self.frequency = value

    @property
    def period(self) -> Union[float, "seconds"]:
        return 1/self.frequency

    @period.setter
    def period(self, value: Union[float, "seconds"]):
        self.frequency = 1/value

    # # Implementation

    def next(self, block: bool=True) -> None | Any:

        # Time to wait for next call if block
        # - Next call at 110 seconds, now=100, wait=10
        # - Positive means to wait, negative we are behind
        wait = self.next_call - time.perf_counter()

        if self.decoupled:
            pass
        elif block:
            time.sleep(max(0, wait))
        elif wait > 0:
            return None

        # The assumed instant the code below will run instantly
        now = self.next_call if self.decoupled else time.perf_counter()

        # Delta time between last call and next call
        if self.dt: self.kwargs["dt"] = now - (self.last_call or now)

        # Time since client started
        if self.time: self.kwargs["time"] = now - self.started

        # Update last call time
        if self.frameskip or self.decoupled:
            self.last_call = now
        else:
            self.last_call = self.next_call

        # Enter or not the given context, call callback with args and kwargs
        with (self.lock or contextlib.nullcontext()):
            with (self.context or contextlib.nullcontext()):
                self.output = self.callback(*self.args, **self.kwargs)

        # Disabled plus Once clients gets deleted
        if self.once:
            self.enabled = False

        # Add periods until next call is in the future
        while self.next_call <= now:
            self.next_call += self.period

        return self.output

@define
class BrokenEventLoop:
    clients:    List[BrokenEventClient] = Factory(list)
    __thread__: Option[Thread, None] = None
    __stop__:   bool = False

    def add_client(self, client: BrokenEventClient) -> BrokenEventClient:
        """Adds a client to the manager with immediate next call"""
        self.clients.append(client)
        return client

    def get_client(self, name: str) -> Option[BrokenEventClient, None]:
        """Gets a client by name"""
        return next((client for client in self.clients if client.name == name), None)

    def new(self, *args, **kwargs) -> BrokenEventClient:
        """Wraps around BrokenVsync for convenience"""
        return self.add_client(BrokenEventClient(*args, **kwargs))

    def once(self, *args, **kwargs) -> BrokenEventClient:
        """Wraps around BrokenVsync for convenience"""
        return self.add_client(BrokenEventClient(*args, once=True, **kwargs))

    @property
    def enabled_clients(self) -> List[BrokenEventClient]:
        """Returns a list of enabled clients"""
        return [client for client in self.clients if client.enabled]

    @property
    def next_client(self) -> BrokenEventClient | None:
        """Returns the next client to be called"""
        if clients := sorted(self.enabled_clients, key=lambda item: item.next_call):
            return clients[0]

    def __sanitize__(self) -> None:
        """Removes disabled 'once' clients"""
        delete = set()
        for i, client in enumerate(self.clients):
            if client.once and (not client.enabled):
                delete.add(i)
        for i in sorted(delete, reverse=True):
            del self.clients[i]

    def next(self, block=True) -> None | Any:
        """Calls the next call client in the list"""
        self.__sanitize__()
        if not (client := self.next_client):
            return None
        return client.next(block=block)

    # # Thread-wise wording

    def start_thread(self) -> None:
        self.__stop__   = False
        self.__thread__ = BrokenThread.new(self.loop)

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

class BrokenWatchdog(ABC):

    @abstractmethod
    def __changed__(self, key, value) -> None:
        """Called when a property changes"""
        ...

    def __setattr__(self, key, value):
        """Calls __changed__ when a property changes"""
        super().__setattr__(key, value)
        self.__changed__(key, value)

# -------------------------------------------------------------------------------------------------|

class BrokenSerde:

    def serialize(self) -> Dict:
        return cattrs.unstructure(self)

    @classmethod
    def deserialize(data: Dict) -> Self['cls']:
        return cattrs.structure(data, cls)

# -------------------------------------------------------------------------------------------------|

class BrokenSingleton(ABC):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super().__new__(cls)
            cls.__singleton__(*args, **kwargs)
        return cls.__instance__

    @abstractmethod
    def __singleton__(self, *args, **kwargs):
        """__init__ but for the singleton"""
        ...

# -------------------------------------------------------------------------------------------------|

class BrokenFluentBuilder:
    """
    Do you ever feel like using a builder-like fluent syntax for changing attributes of an object?
    """
    def __call__(self, **kwargs) -> Self:
        """Updates the instance with the provided kwargs"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def copy(self) -> Self:
        """Returns a copy of this instance"""
        return copy.deepcopy(self)

# -------------------------------------------------------------------------------------------------|

class BrokenNOP:
    """A class that does nothing"""
    def __nop__(self, *args, **kwargs) -> Self:
        return self

    def __getattr__(self, _):
        return self.__nop__

# -------------------------------------------------------------------------------------------------|

@define
class BrokenRelay:
    """
    A class to bind some callback to many callables.

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
    callbacks: list[callable] = field(factory=list)

    def __bind__(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        self.callbacks += BrokenUtils.flatten(callbacks)
        return self

    def bind(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        return self.__bind__(callbacks)

    def subscribe(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        return self.__bind__(callbacks)

    def __matmul__(self, *callbacks: callable) -> Self:
        """Convenience syntax for binding"""
        return self.__bind__(callbacks)

    def __call__(self, *args, **kwargs):
        """Pass through all callbacks to who called "us" (self)"""
        for callback in self.callbacks:
            callback(*args, **kwargs)

# -------------------------------------------------------------------------------------------------|

@define
class BrokenTyper:
    """
    A wrap around Typer with goodies

    • Why? Automation.
    • Stupid? Absolutely.
    • Useful? Maybe.
    • Fun? Yes.
    • Worth it? Probably not.
    • Will I use it? Yes.
    """
    description: str         = ""
    app:         typer.Typer = None
    chain:       bool        = False
    commands:    List[str]   = Factory(list)
    default:     str         = None
    help_option: bool        = False
    __first__:   bool        = True
    epilog:      str         = (
        f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]v{BROKEN_VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://github.com/sponsors/Tremeschin]Sponsoring[/link][/blue] my Open Source Work[/italic grey53]"
    )

    def __attrs_post_init__(self):
        self.app = typer.Typer(
            help=self.description or "No help provided",
            add_help_option=self.help_option,
            pretty_exceptions_enable=False,
            no_args_is_help=True,
            add_completion=False,
            rich_markup_mode="rich",
            chain=self.chain,
            epilog=self.epilog,
        )

    __panel__: str = None

    @contextlib.contextmanager
    def panel(self, name: str) -> None:
        try:
            self.__panel__ = name
            yield
        finally:
            self.__panel__ = None

    def command(self,
        callable: Callable,
        help: str=None,
        add_help_option: bool=True,
        name: str=None,
        context: bool=True,
        default: bool=False,
        panel: str=None,
        **kwargs,
    ):
        # Command must be implemented
        if getattr(callable, "__isabstractmethod__", False):
            return

        # Maybe get callable name
        name = name or callable.__name__

        # Create Typer command
        self.app.command(
            help=help or callable.__doc__ or None,
            add_help_option=add_help_option,
            name=name,
            rich_help_panel=panel or self.__panel__ ,
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            **kwargs,
        )(callable)

        # Add to known commands
        self.commands.append(name)

        # Set as default command
        self.default = name if default else self.default

    def __call__(self, *args, shell: bool=False):
        while True:
            args = BrokenUtils.flatten(args)

            # Insert default implied command
            if self.default and ((not args) or (args.get(0) not in self.commands)):
                args.insert(0, self.default)

            # Update args to BrokenTyper
            if not self.__first__:
                args = shlex.split(input("\n:: BrokenShell (enter for help) $ "))
            self.__first__ = False

            try:
                self.app(args)
            except SystemExit:
                pass
            except KeyboardInterrupt:
                log.success("BrokenTyper stopped by user")
                pass
            except Exception as e:
                raise e

            # Don't continue on non BrokenShell mode
            if not shell:
                break

# -------------------------------------------------------------------------------------------------|

class BrokenProfilerEnum(BrokenEnum):
    """List of profilers"""
    cprofile      = "cprofile"
    # imports       = "imports"
    # pyinstrument  = "pyinstrument"

@define
class BrokenProfiler:
    name: str = "NONE"
    profiler: BrokenProfilerEnum = BrokenProfilerEnum.cprofile

    def __attrs_post_init__(self):
        profiler = os.environ.get(f"{self.name}_PROFILER", self.profiler)
        self.profiler = BrokenProfilerEnum.get(profiler)

    # Base properties

    @property
    def enabled(self) -> bool:
        return os.environ.get(f"{self.name}_PROFILE", "0") == "1"

    @property
    def output(self) -> Path:
        return Path(tempfile.gettempdir())/f"{self.name}.prof"

    # The actual profiler object
    __profiler__: Any = None

    def __enter__(self) -> Self:
        if not self.enabled:
            return self

        match self.profiler:
            case BrokenProfilerEnum.cprofile:
                log.action("Profiling with cProfile")
                import cProfile
                self.__profiler__ = cProfile.Profile()
                self.__profiler__.enable()
                return self

    def __exit__(self, *args) -> None:
        if not self.enabled:
            return

        match self.profiler:
            case BrokenProfilerEnum.cprofile:
                log.action("Finishing cProfile")
                output = self.output.with_suffix(".prof")
                self.__profiler__.disable()
                self.__profiler__.dump_stats(output)
                shell("snakeviz", output)
                return
