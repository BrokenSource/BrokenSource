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

# -------------------------------------------------------------------------------------------------|

# # Unix-like Python "ported" functions

def mkdir(path: PathLike, echo=True):
    """Creates a directory and its parents, fail safe™"""
    path = Path(path)
    if path.exists():
        success(f"Directory [{path}] already exists", echo=echo)
        return
    info(f"Creating directory {path}", echo=echo)
    path.mkdir(parents=True, exist_ok=True)

def touch(path: PathLike, echo=True):
    """Creates a file, fail safe™"""
    path = Path(path)
    if path.exists():
        success(f"File [{path}] already exists", echo=echo)
        return
    info(f"Creating file {path}", echo=echo)
    path.touch()

def copy_path(source: PathLike, destination: PathLike, echo=True):
    source, destination = Path(source), Path(destination)
    info(f"Copying [{source}] -> [{destination}]", echo=echo)
    shutil.copy2(source, destination)

# Path may be a file or directory
def remove_path(path: PathLike, confirm=False, echo=True) -> bool:
    path = Path(path)
    info(f"Removing Path ({confirm=}) [{path}]", echo=echo)

    # Symlinks are safe to remove
    if path.is_symlink():
        path.unlink()
        return True

    # Confirm removal: directory contains data
    if confirm and (not rich.prompt.Confirm.ask(f"Confirm removing path ({path})")):
        return False

    # Remove the path
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink()

    return True

@contextmanager
def pushd(directory):
    """Change directory, then change back when done"""
    cwd = working_directory()
    os.chdir(directory)
    yield directory
    os.chdir(cwd)

# -------------------------------------------------------------------------------------------------|

def print_centered(text: str, width: int="auto", function=print):
    """Prints text centered on the terminal"""
    if width == "auto":
        width = shutil.get_terminal_size().columns
    for line in text.splitlines():
        function(line.center(width))

def open_in_file_explorer(path: PathLike):
    """Opens a path in the file explorer"""
    path = Path(path)
    if BrokenPlatform.Windows:
        os.startfile(str(path))
    elif BrokenPlatform.Linux:
        shell("xdg-open", path)
    elif BrokenPlatform.MacOS:
        shell("open", path)

def true_path(path: PathLike) -> Path:
    return Path(path).expanduser().resolve().absolute()

def binary_exists(binary_name: str) -> bool:
    return find_binary(binary_name) is not None

def get_binary(binary_name: Union[str, List[str]], echo=True) -> Path:

    # Recurse if a list of binaries is given (for all)
    if type(binary_name) is list:
        for binary in binary_name:
            binary = get_binary(binary, echo=echo)
            if binary is not None: return binary
        return None

    # Enforce string
    binary_name = str(binary_name)

    # Attempt to find the binary
    if (binary := find_binary(binary_name)) is not None:
        success(f"Binary [{binary_name.ljust(8)}] is on PATH at [{binary}]", echo=echo)
        return binary
    else:
        warning(f"Binary [{binary_name.ljust(8)}] it not on PATH", echo=echo)
        return None

@lru_cache
def get_binary_cached(binary_name: Union[str, List[str]], echo=True) -> Path:
    return get_binary(binary_name, echo=echo)

class BrokenDependencies:
    def update_path(self, path: PathLike, recursive: bool=True) -> None:
        ...

# Endless war of how to get a FFmpeg binary available
try:
    import imageio_ffmpeg
    BROKEN_FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    try:
        BROKEN_FFMPEG_BINARY = get_binary("ffmpeg", echo=False)
    except FileNotFoundError:
        BROKEN_FFMPEG_BINARY = None

@contextmanager
def download(url) -> Path:
    BROKEN_DIRECTORIES.DOWNLOADS
    download_file = BROKEN_DIRECTORIES.DOWNLOADS / Path(url).name
    with halo.Halo(f"Downloading ({url}) -> [{download_file}]"):
        download_file.write_bytes(BROKEN_REQUESTS_CACHE.get(url).content)
    yield download_file

def make_executable(path: PathLike) -> None:
    """Make a file executable"""
    path = Path(path)
    if BrokenPlatform.Unix:
        info(f"Make Executable [{path}]")
        shell("chmod", "+x", path)

class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__singleton__"):
            cls.__singleton__ = super().__new__(cls)
        return cls.__singleton__
