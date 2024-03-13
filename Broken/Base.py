from __future__ import annotations

import Broken

from . import *

# -------------------------------------------------------------------------------------------------|

class Ignore:
    """A class that does nothing. No-operation"""

    def __nop__(self, *args, **kwargs) -> Self:
        return self

    def __call__(self, *args, **kwargs) -> Self:
        return self

    def __getattr__(self, _):
        return self.__nop__

def Maybe(call, when, **args):
    if when:
        return call(**args)

# -------------------------------------------------------------------------------------------------|
# Lazy Bastard methods

inverse = lambda x: 1 / x
clamp = lambda value, low, high: max(low, min(value, high))

@contextlib.contextmanager
def LazyCounter():
    start = time.perf_counter()
    yield None
    log.info(f"Took: {time.perf_counter() - start:.4f} seconds")

def flatten(*stuff: Union[Any, List[Any]], truthy: bool=True) -> List[Any]:
    """
    Flatten nested list like iterables to a 1D list
    [[a, b], c, [d, e, (None, 3)], [g, h]] -> [a, b, c, d, e, None, 3, g, h]
    """
    # Fixme: Add allow_none argument
    iterables = (list, tuple, Generator)
    flatten = lambda stuff: [
        item for subitem in stuff for item in
        (flatten(subitem) if isinstance(subitem, iterables) else [subitem])
        if (not truthy) or (truthy and item)
    ]
    return flatten(stuff)

def easy_multiple(method: Callable) -> Callable:
    """Returns first element if the method returns len 1 else list of outputs"""
    def wrapper(*args, **kwargs):
        result = list(method(*args, **kwargs))
        if len(result) == 1:
            return result[0]
        return result
    return wrapper

def apply(callback: Callable, iterable: Iterable[Any]) -> List[Any]:
    """map(f, x) is lazy, this consumes the generator returning a list"""
    return list(map(callback, iterable))

@easy_multiple
def denum(*items: Any) -> Any:
    """De-enumerates enum iterables to their value"""
    return apply(lambda item: item.value if isinstance(item, Enum) else item, items)

@staticmethod
def dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")

# -------------------------------------------------------------------------------------------------|
# Cursed Python ahead, here be dragons!

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
            for cls in type(self).mro()[:-2]:
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

class BrokenAttrs:
    """
    Walk over an @attrs.defined class and call __post__ on all classes in the MRO.
    # Warn: Must NOT define __attrs_post_init__ in an inheriting class
    # Fixme: Can improve by starting on BrokenAttrs itself
    """
    def __attrs_post_init__(self):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    def __post__(self) -> None:
        pass

# -------------------------------------------------------------------------------------------------|

def shell(
    *args:   list[Any],
    output:  bool=False,
    Popen:   bool=False,
    shell:   bool=False,
    env:     dict[str, str]=None,
    echo:    bool=True,
    confirm: bool=False,
    do:      bool=True,
    **kwargs
) -> Option[None, str, subprocess.Popen, subprocess.CompletedProcess]:
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works
    • This is arguably the most important function in Broken 🙈

    Example:
        ```python
        shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
        ```

    Args:
        `args`:    The command to run, can be a list of arguments or a list of lists of arguments, don't care
        `output`:  Return the process's stdout as a decoded string
        `Popen`:   Run the process with subprocess.Popen
        `shell`:   (discouraged) Run the command with shell=True, occasionally useful
        `echo`:    Log the command being run or not
        `confirm`: Ask for confirmation before running the command or not
        `do`:      Inverse of `skip`, do not run the command, but log it as minor

    Kwargs (subprocess.* arguments):
        `cwd`: Current working directory for the command
        `env`: Environment variables for the command
        `*`:   Any other keyword arguments are passed to subprocess.*
    """
    if output and Popen:
        raise ValueError(log.error("Cannot use (output=True) and (Popen=True) at the same time"))

    # Flatten a list, remove falsy values, convert to strings
    command = tuple(map(str, flatten(args)))

    if shell:
        log.warning("Running command with (shell=True), be careful.." + " Consider using (confirm=True)"*(not confirm))
        command = '"' + '" "'.join(command) + '"'

    # Assert command won't fail due unknown binary
    if (not shell) and (not shutil.which(command[0])):
        raise FileNotFoundError(log.error(f"Binary doesn't exist or was not found on PATH ({command[0]})"))

    # Get the current working directory
    cwd = f" @ ({kwargs.get('cwd', '') or Path.cwd()})"
    (log.info if do else log.skip)(("Running" if do else "Skipping") + f" Command {command}{cwd}", echo=echo)
    if not do: return

    # Confirm running command or not
    if confirm and not click.confirm(f"• Confirm running the command above"):
        return

    # Get current environment variables
    env = os.environ.copy() | (env or {})

    # Run the command and return specified object
    if output: return subprocess.check_output(command, env=env, shell=shell, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, env=env, shell=shell, **kwargs)
    else:      return subprocess.run(command, env=env, shell=shell, **kwargs)

# -------------------------------------------------------------------------------------------------|

class BrokenPlatform:
    """
    Host Platform information, Cross Compilation targets and some utilities
    """

    # Name of the current platform - (linux, windows, macos, bsd)
    Name:         str  = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    OnLinux:      bool = (Name == "linux")
    OnWindows:    bool = (Name == "windows")
    OnMacOS:      bool = (Name == "macos")
    OnBSD:        bool = (Name == "bsd")

    # Platform release binaries extension and CPU architecture
    Extension:    str  = (".exe" if OnWindows else ".bin")
    Architecture: str  = (platform.machine().lower().replace("x86_64", "amd64"))

    # Family of platforms
    OnUnix:       bool = (OnLinux or OnMacOS or OnBSD)

    # Distro IDs: https://distro.readthedocs.io/en/latest/
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
    OnManjaro:    bool = (LinuxDistro == "manjaro")
    OnArchLike:   bool = (OnArch or OnManjaro)

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
        MacosAMD64:   str = "macos-amd64"
        MacosARM:     str = "macos-arm64"

    CurrentTarget:    str = f"{Name}-{Architecture}"

    @staticmethod
    def clear_terminal(**kwargs):
        if not kwargs.get("do", True):
            return

        if BrokenPlatform.OnWindows:
            os.system("cls")
        else:
            shell("clear", **kwargs)

    @staticmethod
    def log_system_info():
        log.info(f"• System Info: {platform.system()} {platform.release()}, Python {platform.python_version()} {platform.machine()}")

    # Simply, why Windows/Python have different directory names for scripts? ...
    # https://github.com/pypa/virtualenv/commit/993ba1316a83b760370f5a3872b3f5ef4dd904c1
    PyScripts         = ("Scripts" if OnWindows else "bin")
    PyScriptExtension = (".cmd" if OnWindows else "")

# -------------------------------------------------------------------------------------------------|

class ShutilFormat(BrokenEnum):
    Zip   = "zip"
    Tar   = "tar"
    GzTar = "tar.gz"
    BzTar = "tar.bz2"
    XzTar = "tar.xz"

class BrokenPath(Path):
    """
    BrokenPath is not supposed to be instantiated as a class but used as a namespace (static class)
    • The __new__ method returns the value of .get method, which is pathlib.Path
    • Many Path utilities as staticmethod and contextmanager
    """
    def __new__(cls, *paths: PathLike, valid: bool=False) -> Optional[Path]:
        return cls.get(*paths, valid=valid)

    @staticmethod
    def get(*paths: PathLike, valid: bool=False) -> Optional[Path] | List[Optional[Path]]:
        """Resolve paths to absolute None-safe, optionally verify their existence, None if invalid"""
        paths = map(lambda path: Path(path).expanduser().resolve() if path else None, paths)
        paths = map(lambda path: (path if (path and path.exists()) else None) if valid else path, paths)
        paths = list(paths)
        return paths[0] if (len(paths) == 1) else paths

    @staticmethod
    def copy(src: PathLike, dst: PathLike, *, echo=True) -> "destination":
        src, dst = BrokenPath(src, dst)
        BrokenPath.mkdir(dst.parent, echo=False)
        if src.is_dir():
            log.info(f"Copying Directory ({src})\n → ({dst})", echo=echo)
            shutil.copytree(src, dst)
        else:
            log.info(f"Copying File ({src})\n → ({dst})", echo=echo)
            shutil.copy2(src, dst)
        return dst

    @staticmethod
    def move(src: PathLike, dst: PathLike, *, echo=True) -> "destination":
        src, dst = BrokenPath(src, dst)
        log.info(f"Moving ({src})\n → ({dst})", echo=echo)
        shutil.move(src, dst)
        return dst

    @staticmethod
    def remove(path: PathLike, *, confirm=False, echo=True) -> Path:
        path = BrokenPath(path)
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

    @staticmethod
    def touch(path: PathLike, *, echo=True) -> Path:
        """Creates a file, fail safe™"""
        if (path := BrokenPath(path)).exists():
            log.success(f"File ({path}) already touched", echo=echo)
            return
        log.info(f"Touching file {path}", echo=echo)
        path.touch()
        return path

    @staticmethod
    def mkdir(path: PathLike, parent: bool=False, *, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        path = BrokenPath(path)
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

    @contextmanager
    def pushd(path: PathLike, *, echo: bool=True) -> Generator[Path, None, None]:
        """Change directory, then change back when done"""
        path = BrokenPath(path)
        cwd = os.getcwd()
        log.info(f"Pushd ({path})", echo=echo)
        os.chdir(path)
        yield path
        log.info(f"Popd  ({path})", echo=echo)
        os.chdir(cwd)

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
        log.info(f"Symlinking ({virtual})\n → ({real})", echo=echo)

        # Return if already symlinked
        if (BrokenPath(virtual) == BrokenPath(real)):
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
            if click.confirm(f"• Path ({virtual}) exists, but Broken wants to create a symlink to ({real})\nConfirm removing the 'virtual' path and continuing? (It might contain data or be a important symlink)"):
                BrokenPath.remove(virtual, echo=False)
            else:
                return

        # Actually symlink
        virtual.symlink_to(real)
        return virtual

    @staticmethod
    def make_executable(path: PathLike, *, echo=False) -> Path:
        """Make a file executable"""
        path = BrokenPath(path)
        if BrokenPlatform.OnUnix:
            shell("chmod", "+x", path, echo=echo)
        elif BrokenPlatform.OnWindows:
            shell("attrib", "+x", path, echo=echo)
        return path

    @staticmethod
    def zip(path: Path, output: Path=None, *, format: ShutilFormat=ShutilFormat.Zip, echo: bool=True) -> Path:
        format = ShutilFormat(format)
        output = BrokenPath(output or path).with_suffix(f".{format}")
        path   = BrokenPath(path)
        BrokenPath.remove(output, echo=echo)
        log.info(f"Zipping ({path})\n → ({output})", echo=echo)
        shutil.make_archive(output.with_suffix(""), format, path)
        return output

    @staticmethod
    def stem(path: PathLike) -> str:
        """
        Get the "true stem" of a path, as pathlib's only gets the last dot one
        • "/path/with/many.ext.ens.ions" -> "many" instead of "many.ext.ens"
        """
        stem = Path(Path(path).stem)
        while (stem := Path(stem).with_suffix("")).suffix:
            continue
        return str(stem)

    @staticmethod
    def sha256sum(data: Union[Path, str, bytes]) -> Optional[str]:
        """Get the sha256sum of a file, directory or bytes"""

        # Nibble the bytes !
        if isinstance(data, bytes):
            return hashlib.sha256(data).hexdigest()

        # String or Path is a valid path
        elif (path := BrokenPath(data, valid=True)):
            with yaspin(text=log.info(f"Calculating sha256sum of ({path})")):
                if path.is_file():
                    return hashlib.sha256(path.read_bytes()).hexdigest()

                # Iterate on all files for low memory footprint
                feed = hashlib.sha256()
                for file in path.rglob("*"):
                    if not file.is_file():
                        continue
                    with open(file, "rb") as file:
                        while (chunk := file.read(8192)):
                            feed.update(chunk)
                return feed.hexdigest()

        elif isinstance(data, str):
            return hashlib.sha256(data.encode("utf-8")).hexdigest()

        return

    @staticmethod
    def extract(
        path: Path,
        output: Path=None,
        *,
        overwrite: bool=False,
        PATH: bool=False,
        echo: bool=True
    ) -> Path:
        path, output = BrokenPath(path, output)

        # Output is input without suffix if not given
        if (output is None):
            output = path.parent/BrokenPath.stem(path)

        # Add stem to the output as some archives might be flat
        output /= BrokenPath.stem(path)

        # Re-extract on order
        Maybe(BrokenPath.remove, overwrite, echo=echo)

        # A file to skip if it exists, created after successful extraction
        if (extract_flag := (output/"BrokenPath.extract.ok")).exists():
            log.minor(f"Already extracted ({output})", echo=echo)
            Maybe(BrokenPath.add_to_path, PATH, path=output, recursively=True, echo=echo)
            return output

        # Show progress as this might take a while on slower IOs
        log.info(f"Extracting ({path})\n → ({output})", echo=echo)
        with yaspin(text="Extracting archive.."):
            shutil.unpack_archive(path, output)

        extract_flag.touch()
        Maybe(BrokenPath.add_to_path, PATH, path=output, recursively=True, echo=echo)
        return output/BrokenPath.stem(path)

    @staticmethod
    def download(
        url: URL,
        output: Path=None,
        *,
        size_check: bool=True,
        chunk: int=1024,
        echo: bool=True
    ) -> Optional[Path]:

        # Link must be valid
        if not validators.url(url):
            log.error(f"The string ({url}) doesn't look like a valid URL", echo=echo)
            return

        import requests

        # Default to Broken's Download directory
        if (output is None):
            output = Broken.BROKEN.DIRECTORIES.DOWNLOADS

        # Append url's file name to the output path
        if (output := BrokenPath(output)).is_dir():
            output /= Path(url.split("#")[0].split("?")[0].split("/")[-1])

        # Without size check, the existence of the file is enough
        if output.exists() and (not size_check):
            log.info(f"Already Downloaded ({output})", echo=echo)
            log.minor(f"• Size check was skipped, the file might be incomplete", echo=echo)
            return

        # Send the GET request, we might be offline!
        try:
            response = requests.get(url, stream=True)
        except requests.exceptions.RequestException as error:
            log.error(f"Failed to download file ({url}) → ({output}): {error}", echo=echo)
            return

        size = int(response.headers.get('content-length', 0))

        # The file might already be (partially) downloaded
        if output.exists():
            A, B = (output.stat().st_size, size)
            if (A == B):
                log.info(f"Already Downloaded ({output})", echo=echo)
                return output
            else:
                log.warning(f"Wrong Download at ({output})", echo=echo)

        log.info(f"Downloading file at ({url}):", echo=echo)
        log.info(f"• Output: ({output})", echo=echo)

        # It is binary prefix, right? kibi, mebi, gibi, etc. as we're dealing with raw bytes
        with open(output, "wb") as file, tqdm.tqdm(
            desc=f"Downloading ({output.name})",
            total=size, unit="iB", unit_scale=True, unit_divisor=1024,
            mininterval=1/30, maxinterval=0.5, leave=False
        ) as progress:
            for data in response.iter_content(chunk_size=chunk):
                progress.update(file.write(data))

        # Url was invalid
        if (response.status_code != 200):
            log.error(f"Failed to Download File at ({url}):", echo=echo)
            log.error(f"• HTTP Error: {response.status_code}", echo=echo)
            return

        # Wrong downloaded and expected size
        elif (output.stat().st_size != size):
            log.error(f"File ({output}) was not downloaded correctly", echo=echo)
            return

        log.success(f"Downloaded file ({output}) from ({url})", echo=echo)
        return output

    @staticmethod
    def get_external(url: URL, *, subdir: str="", echo: bool=True) -> Path:
        file = BrokenPath.download(denum(url), echo=echo)

        # File is a Archive, extract
        if any((str(file).endswith(ext) for ext in ShutilFormat.values)):
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_ARCHIVES
            return BrokenPath.extract(file, directory, PATH=True, echo=echo)

        # File is some known type, move to their own external directory
        if file.suffix in AUDIO_EXTENSIONS:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_AUDIO
        elif file.suffix in IMAGE_EXTENSIONS:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_IMAGES
        elif file.suffix in FONT_EXTENSIONS:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_FONTS
        elif file.suffix in SOUNDFONTS_EXTENSIONS:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_SOUNDFONTS
        elif file.suffix in MIDI_EXTENSIONS:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNAL_MIDIS
        else:
            directory = Broken.BROKEN.DIRECTORIES.EXTERNALS
        return BrokenPath.move(file, directory/subdir, echo=echo)

    @staticmethod
    @easy_multiple
    def which(*name: str, echo=True) -> Optional[Path]:
        BrokenPath.update_externals_path()
        return apply(shutil.which, name)

    @staticmethod
    def update_externals_path(path: PathLike=None, *, echo: bool=True) -> Optional[Path]:
        path = path or Broken.BROKEN.DIRECTORIES.EXTERNALS
        return BrokenPath.add_to_path(path, recursively=True, echo=echo)

    @staticmethod
    def on_path(path: PathLike) -> bool:
        """Check if a path is on PATH, works with symlinks"""
        return BrokenPath(path) in map(BrokenPath, os.environ.get("PATH", "").split(os.pathsep))

    @staticmethod
    def add_to_path(
        path: PathLike,
        *,
        recursively: bool=False,
        persistent: bool=False,
        preferential: bool=True,
        echo: bool=True
    ) -> Path:
        """
        Add a path, recursively or not, to System's Path or this Python process's Path

        Args:
            `recursively`:  Also add all subdirectories of the given path
            `persistent`:   Use 'userpath' package to add to the Shell's or Registry PATH
            `preferential`: Prepends the path for less priority on system binaries

        Returns:
            The Path argument itself
        """
        path = BrokenPath(path)

        # Can't recurse on file or non existing directories
        if (not path.exists()) and path.is_file() and recursively:
            log.warning(f"Can't add non existing path or file recursively to Path ({path})", echo=echo)
            return path

        log.debug(f"Adding to Path (Recursively: {recursively}, Persistent: {persistent}): ({path})", echo=echo)

        for other in (path.glob("**/*") if recursively else [path]):
            if other.is_file():
                continue
            if BrokenPath.on_path(other):
                continue
            if persistent:
                import userpath
                userpath.append(str(other))
            else:
                if preferential:
                    os.environ["PATH"] = (str(other)+os.pathsep+os.environ["PATH"])
                    sys.path.insert(0, str(other))
                else:
                    os.environ["PATH"] = (os.environ["PATH"]+os.pathsep+str(other))
                    sys.path.append(str(other))
        return path

    # # Specific / "Utils"

    @staticmethod
    def open_in_file_explorer(path: PathLike):
        """Opens a path in the file explorer"""
        path = BrokenPath(path)
        if BrokenPlatform.OnWindows:
            os.startfile(str(path))
        elif BrokenPlatform.OnLinux:
            shell("xdg-open", path)
        elif BrokenPlatform.OnMacOS:
            shell("open", path)

    # Fixme: Untested functions, needs better name; are these useful?

    @staticmethod
    def non_empty_file(path: Path) -> bool:
        return path.exists() and path.is_file() and path.stat().st_size > 0

    @staticmethod
    def empty_file(path: Path, create: bool=True) -> bool:
        if create and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return path.exists() and path.is_file() and len(path.read_text()) == 0

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
        directories = apply(Path, flatten(directories))

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

# -------------------------------------------------------------------------------------------------|

class BrokenUtils:

    @staticmethod
    def truthy(items: List[Any]) -> List[Any]:
        """Transforms a list into a truthy-only values list, removing all falsy values"""
        return [item for item in flatten(items) if item]

    @staticmethod
    def get_free_tcp_port():
        import socket
        temp_socket = socket.socket()
        temp_socket.bind(('', 0))
        port = temp_socket.getsockname()[1]
        temp_socket.close()
        return port

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
        Extend a class with another class's methods or a method directly.

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
    def have_import(module: str, *, load: bool=False) -> bool:
        """Check if a module has been imported"""
        if load:
            try:
                __import__(module)
                return True
            except ImportError:
                return False
        return not isinstance(sys.modules.get(module), BrokenImportError)

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

    # Todo: Move this to a proper class
    PRECISE_SLEEP_AHEAD_SECONDS     = (5e-3 if BrokenPlatform.OnWindows else 5e-4)
    PRECISE_SLEEP_LATE_MULTIPLIER   = 4
    PRECISE_SLEEP_INTERPOLATE_RATIO = 0.05
    PRECISE_SLEEP_MAX_AHEAD_SECONDS = 0.1

    @staticmethod
    def precise_sleep(seconds: float) -> None:
        """
        Sleep for a precise amount of time. This function is very interesting for some reasons:
        - time.sleep() obviously uses syscalls, and it's up to the OS to implement it
        - This is usually done by scheduling the thread to wake up after the time has passed
        - On Windows, this precision was 15ms (terrible), and on Python 3.11+ was optimized to 100ns
        - On Unix, the precision is great with nanosleep() or usleep() (1ms or less)

        So, in practice, the best ever precision time sleep function would be:
        ```python
        while (now - start) < wait:
            now = time.perf_counter()
        ```

        As evident, this spins the thread full time due the .perf_counter() and conditional, which
        is not wanted on a sleep function (to use 100% of a thread)

        Taking advantage of the fact that time.sleep() is usually precise enough, and always will
        overshoot the time, we can sleep close to the time and apply the previous spinning method
        to achieve a very precise sleep, with a low enough overhead, relatively speaking.

        Args:
            seconds: Precise time to sleep

        Returns:
            None
        """
        if seconds < 0:
            return

        # Sleep close to the due time
        ahead = max(0, seconds - BrokenUtils.PRECISE_SLEEP_AHEAD_SECONDS)
        start = time.perf_counter()
        time.sleep(max(0, ahead))

        # How much error the last sleep() just did
        late = ((time.perf_counter() - start) - ahead) * BrokenUtils.PRECISE_SLEEP_LATE_MULTIPLIER

        # Adjust future sleeps based on the error
        BrokenUtils.PRECISE_SLEEP_AHEAD_SECONDS += BrokenUtils.PRECISE_SLEEP_INTERPOLATE_RATIO * \
            (late - BrokenUtils.PRECISE_SLEEP_AHEAD_SECONDS)

        # Clamp the ahead time: 0 <= ahead <= max
        BrokenUtils.PRECISE_SLEEP_AHEAD_SECONDS = min(
            max(0, BrokenUtils.PRECISE_SLEEP_AHEAD_SECONDS),
            BrokenUtils.PRECISE_SLEEP_MAX_AHEAD_SECONDS
        )

        # Spin the thread until the time is up (precise Sleep)
        while (time.perf_counter() - start) < seconds:
            pass

    @staticmethod
    def locals(level: int=1, self: bool=True) -> dict:
        locals = inspect.currentframe()

        # Keep getting the previous's frame
        for _ in range(level):
            locals = locals.f_back

        # Get the locals
        locals = locals.f_locals

        # Remove self from locals
        if self:
            locals.pop("self", None)

        return locals

    @staticmethod
    def round(number: Number, multiple: Number, *, type=int) -> Number:
        return type(multiple * round(number/multiple))

    @staticmethod
    def round_resolution(width: Number, height: Number) -> Tuple[int, int]:
        """FFmpeg likes multiples of 2, so let it be"""
        return (
            BrokenUtils.round(width,  multiple=2, type=int),
            BrokenUtils.round(height, multiple=2, type=int)
        )

    @staticmethod
    def rms_stdlib(data) -> float:
        return math.sqrt(sum(x**2 for x in data) / len(data))

    @staticmethod
    def rms(data) -> float:
        import numpy
        return numpy.sqrt(numpy.mean(numpy.square(data)))

# -------------------------------------------------------------------------------------------------|

@define
class BrokenThreadPool:
    threads: List[Thread] = []
    max:     int          = 1

    @property
    def alive(self) -> List[Thread]:
        return [thread for thread in self.threads if thread.is_alive()]

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

    def __new__(cls, *args, **kwargs) -> Thread:
        return cls.new(*args, **kwargs)

    @staticmethod
    def pool(name: str) -> BrokenThreadPool:
        return BrokenThread.pools.setdefault(name, BrokenThreadPool())

    @staticmethod
    def join_all_pools() -> None:
        for pool in BrokenThread.pools.values():
            pool.join()

    @staticmethod
    def new(
        target: Callable,
        *args,
        start: bool=True,
        join: bool=False,
        loop: bool=False,
        pool: str=None,
        max: int=1,
        daemon: bool=False,
        locals: bool=False,
        self: bool=False,
        callback: Callable=None,
        **kwargs
    ) -> Thread:
        """
        Create a thread on a callable, yeet whatever you think it works
        • Support for a basic Thread Pool, why no native way?

        Args:
            target: The function to call, consider using functools.partial or this kwargs
            args:   Arguments to pass to the function (positional, unnamed)
            kwargs: Keyword arguments to pass to the function
            start:  Start the thread immediately after creation
            join:   Wait for the thread to finish after creation
            loop:   Wrap the target callable in a loop
            pool:   Name of the pool to append the thread to, see BrokenThreadPool
            max:    Maximum threads in the pool
            daemon: When the main thread exits, daemon threads are also terminated

        Advanced:
            locals:   Whether to pass the current scope locals to the callable or not
            self:     Include "self" in the locals if locals=True
            callback: Function to call after the thread finishes

        Returns:
            The created Thread object
        """

        # Update kwargs with locals
        if locals: kwargs.update(BrokenUtils.locals(level=2, self=self))
        the_target = target

        # Wrap the callback in a loop
        @functools.wraps(target)
        def looped(*args, **kwargs):
            while True:
                target(*args, **kwargs)
        the_target = (looped if loop else the_target)

        # Wrap the target in a callback
        @functools.wraps(target)
        def callbacked(*args, **kwargs):
            target(*args, **kwargs)
            if callback is not None:
                callback()
        the_target = (callbacked if callback else the_target)

        # Create Thread object
        parallel = Thread(
            target=the_target,
            daemon=daemon,
            args=args,
            kwargs=kwargs
        )

        # Maybe wait for the pool to be free
        if pool and (pool := BrokenThread.pools.setdefault(pool, BrokenThreadPool())):
            pool.max = max
            pool.append(parallel)
        if start:
            parallel.start()
        if join and start:
            parallel.join()
        return parallel

# -------------------------------------------------------------------------------------------------|

@define
class BrokenEventClient:
    """
    Client configuration for BrokenEventLoop

    # Function:
    - callback:   Function callable to call every synchronization
    - args:       Arguments to pass to callback
    - kwargs:     Keyword arguments to pass to callback
    - output:     Output of callback (returned value)
    - context:    Context to use when calling callback (with statement)
    - lock:       Lock to use when calling callback (with statement)
    - enabled:    Whether to enable this client or not
    - once:       Whether to call this client only once or not

    # Synchronization
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
    callback: callable       = None
    args:     List[Any]      = Factory(list)
    kwargs:   Dict[str, Any] = Factory(dict)
    output:   Any            = None
    context:  Any            = None
    lock:     threading.Lock = None
    enabled:  bool           = True
    once:     bool           = False

    # Synchronization
    frequency:  Hertz = 60.0
    frameskip:  bool  = True
    decoupled:  bool  = False
    precise:    bool  = False

    # Timing
    started:   Seconds = Factory(lambda: time.bang_counter())
    next_call: Seconds = None
    last_call: Seconds = None
    _time:     bool    = False
    _dt:       bool    = False

    def __attrs_post_init__(self):
        signature = inspect.signature(self.callback)
        self._dt   = ("dt"   in signature.parameters)
        self._time = ("time" in signature.parameters)

        # Assign idealistic values for decoupled
        if self.decoupled: self.started = BIG_BANG
        self.last_call = (self.last_call or self.started)
        self.next_call = (self.next_call or self.started)

        # Note: We could use numpy.float128 for the most frametime precision on the above..
        #       .. But the Client code is smart enough to auto adjust itself to sync

    # # Useful properties

    @property
    def fps(self) -> Hertz:
        return self.frequency

    @fps.setter
    def fps(self, value: Hertz):
        self.frequency = value

    @property
    def period(self) -> Seconds:
        return 1/self.frequency

    @period.setter
    def period(self, value: Seconds):
        self.frequency = 1/value

    @property
    def should_delete(self) -> bool:
        return self.once and (not self.enabled)

    # # Sorting

    def __lt__(self, other: Self) -> bool:
        return self.next_call < other.next_call

    def __gt__(self, other: Self) -> bool:
        return self.next_call > other.next_call

    # # Implementation

    def next(self, block: bool=True) -> None | Any:

        # Time to wait for next call if block
        # - Next call at 110 seconds, now=100, wait=10
        # - Positive means to wait, negative we are behind
        wait = (self.next_call - time.bang_counter())

        if self.decoupled:
            pass
        elif block:
            if self.precise:
                BrokenUtils.precise_sleep(wait)
            else:
                time.sleep(max(0, wait))
        elif wait > 0:
            return None

        # The assumed instant the code below will run instantly
        now = self.next_call if self.decoupled else time.bang_counter()
        if self._dt:   self.kwargs["dt"]   = (now - self.last_call)
        if self._time: self.kwargs["time"] = (now - self.started)

        # Enter or not the given context, call callback with args and kwargs
        with (self.lock or contextlib.nullcontext()):
            with (self.context or contextlib.nullcontext()):
                self.output = self.callback(*self.args, **self.kwargs)

        # Fixme: This is a better way to do it, but on decoupled it's not "dt perfect"
        # self.next_call = self.period * (math.floor(now/self.period) + 1)

        # Update future and past states
        self.last_call = now
        while self.next_call <= now:
            self.next_call += self.period

        # (Disabled && Once) clients gets deleted
        self.enabled = not self.once

        return self

@define
class BrokenEventLoop:
    clients: List[BrokenEventClient] = Factory(list)
    thread:  Optional[Thread]        = None

    # # Management

    def add_client(self, client: BrokenEventClient) -> BrokenEventClient:
        """Adds a client to the manager with immediate next call"""
        self.clients.append(client)
        return client

    def get_client(self, name: str) -> Optional[BrokenEventClient]:
        """Gets a client by name"""
        return next((client for client in self.clients if client.name == name), None)

    # # Creation

    def new(self, *a, **k) -> BrokenEventClient:
        """Wraps around BrokenVsync for convenience"""
        return self.add_client(BrokenEventClient(*a, **k))

    def once(self, *a, **k) -> BrokenEventClient:
        """Wraps around BrokenVsync for convenience"""
        return self.add_client(BrokenEventClient(*a, **k, once=True))

    def partial(self, callable: Callable, *a, **k) -> BrokenEventClient:
        """Wraps around BrokenVsync for convenience"""
        return self.once(callable=functools.partial(callable, *a, **k))

    # # Filtering

    @property
    def enabled_clients(self) -> Iterable[BrokenEventClient]:
        """Returns a list of enabled clients"""
        for client in self.clients:
            if client.enabled:
                yield client

    @property
    def next_client(self) -> BrokenEventClient | None:
        """Returns the next client to be called"""
        return min(self.enabled_clients)

    def __sanitize__(self) -> None:
        """Removes disabled 'once' clients"""
        length = len(self.clients)
        for i, client in enumerate(reversed(self.clients)):
            if client.should_delete:
                del self.clients[length - i - 1]

    # # Actions

    def next(self, block=True) -> None | Any:
        try:
            if (client := self.next_client):
                return client.next(block=block)
        finally:
            self.__sanitize__()

    # # Block-free next

    __work__: bool = False

    def smart_next(self) -> None | Any:
        # Note: Proof of concept. The frametime Ticking might be enough for ShaderFlow

        # Too close to the next known call, call blocking
        if abs(time.bang_counter() - self.next_client.next_call) < 0.005:
            return self.next(block=True)

        # By chance any "recently added" client was added
        if (call := self.next(block=False)):
            self.__work__ = True
            return call

        # Next iteration, wait for work but don't spin lock
        if not self.__work__:
            time.sleep(0.001)

        # Flag that there was not work done
        self.__work__ = False

    # # Thread-wise wording

    __stop__: bool = False

    def __loop__(self):
        while not self.__stop__:
            self.next()

    def start_thread(self) -> None:
        self.thread = BrokenThread.new(self.next)

    def stop_thread(self):
        self.__stop__ = True
        self.thread.join()
        self.__stop__ = False

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
    description: str       = ""
    app:         TyperApp  = None
    chain:       bool      = False
    commands:    List[str] = Factory(list)
    default:     str       = None
    help_option: bool      = False
    exit_hook:   Callable  = Factory(Ignore)
    __first__:   bool      = True
    epilog:      str       = (
        f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]v{BROKEN_VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://www.patreon.com/Tremeschin]Sponsoring[/link][/blue] my Open Source Work[/italic grey53]"
    )

    def __attrs_post_init__(self):
        self.app = TyperApp(
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
    def panel(self, name: str) -> Generator[None, None, None]:
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
            args = flatten(args)

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
                self.exit_hook()
            except KeyboardInterrupt:
                log.success("BrokenTyper stopped by user")
                self.exit_hook()
            except Exception as e:
                self.exit_hook()
                raise e

            # Don't continue on non BrokenShell mode
            if not shell:
                break

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

    def copy(self, **kwargs) -> Self:
        """Returns a copy of this instance"""
        new = copy.deepcopy(self)
        for key, value in kwargs.items():
            setattr(new, key, value)
        return new

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
    callbacks: list[callable] = Factory(list)

    def __bind__(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        self.callbacks += flatten(callbacks)
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
                log.trace("Profiling with cProfile")
                import cProfile
                self.__profiler__ = cProfile.Profile()
                self.__profiler__.enable()
                return self

    def __exit__(self, *args) -> None:
        if not self.enabled:
            return

        match self.profiler:
            case BrokenProfilerEnum.cprofile:
                log.trace("Finishing cProfile")
                output = self.output.with_suffix(".prof")
                self.__profiler__.disable()
                self.__profiler__.dump_stats(output)
                shell("snakeviz", output)
                return
