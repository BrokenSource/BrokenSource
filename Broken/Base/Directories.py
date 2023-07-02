from . import *

# Is the current Python some "compiler" release?
IS_RELEASE_PYINSTALLER = getattr(system, "frozen", False)
IS_RELEASE_NUITKA      = getattr(__builtins__, "__compiled__", False)

# pyproject.toml's version date
BROKEN_VERSION = ""

# FIXME: How to, do we need version on releases?
if not (IS_RELEASE_PYINSTALLER or IS_RELEASE_NUITKA):
    import pkg_resources
    BROKEN_VERSION = f'v{pkg_resources.get_distribution("Broken").version}'

def get_executable_directory() -> Path:
    """Smartly gets the current "executable" of the current scope, or the release binary's path"""
    if IS_RELEASE_PYINSTALLER:
        info("Running from Pyinstaller release")
        return Path(system.executable).parent.absolute().resolve()
    elif IS_RELEASE_NUITKA:
        info("Running from Nuitka release")
        return Path(__builtins__.__compiled__).parent.absolute().resolve()
    else:
        return Path(inspect.stack()[2].filename).parent.absolute().resolve()

def make_project_directories(app_name: str="Broken", app_author: str="BrokenSource", echo=True) -> DotMap:
    """Make directories for a project, returns a DotMap of directories (.ROOT, .CACHE, .CONFIG, .DATA, .EXTERNALS)"""
    info(f"Making project directories for [AppName: {app_name}] by [AppAuthor: {app_author}]", echo=echo)
    directories = DotMap()

    # Root of the project directories
    directories.ROOT       = Path(AppDirs("Broken", app_author).user_data_dir)
    directories.CACHE      = directories.ROOT/app_name/"Cache"
    directories.CONFIG     = directories.ROOT/app_name/"Config"
    directories.DATA       = directories.ROOT/app_name/"Data"
    directories.LOGS       = directories.ROOT/app_name/"Logs"
    directories.TEMP       = directories.ROOT/app_name/"Temporary"
    directories.DOWNLOADS  = directories.ROOT/app_name/"Downloads"
    directories.EXTERNALS  = directories.ROOT/app_name/"Externals"
    directories.EXECUTABLE = get_executable_directory()

    # "Macro" to make a new directory and add it to the DotMap
    def new_directory(name: PathLike, echo=True):
        (directory := directories.ROOT/app_name/name).mkdir(parents=True, exist_ok=True)
        info(f"• ({name.ljust(10)}): [{directory}]", echo=echo)
        setattr(directories, str(name).upper(), directory)

    directories.NEW = new_directory

    # Make all project directories
    for name, directory in directories.items():
        if name == "NEW": continue
        info(f"• ({name.ljust(10)}): [{directory}]", echo=echo)
        directory.mkdir(parents=True, exist_ok=True)
    return directories


# Root of BrokenSource Monorepo
BROKEN_ROOT_DIR = Path(__file__).parent.parent.parent.absolute().resolve()
SYSTEM_ROOT_DIR = Path("/").absolute().resolve()

# Where Broken shall be placed as a symlink to be shared
# (on other pyproject.toml have it as broken = {path="/Broken", develop=true})
BROKEN_SHARED_DIR = SYSTEM_ROOT_DIR/"Broken"

# Shared directories of Broken package
BROKEN_DIRECTORIES = make_project_directories(echo=False)

# Constants
USERNAME = env.get("USER") or env.get("USERNAME")
HOME_DIR = Path.home()