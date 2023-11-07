from . import *


class BrokenDirectories:
    """
    Class that handles creating directories for Broken projects for consistency.
    # Default directories:
        - Root:      Root directory for the project (data directory)
        - Resources:
    # Directories are created as needed. Suggestions:
        - Cache:     Cache files
        - Config:    Configuration files
        - Data:      Data files
        - Logs:      Log files
        - Externals: External files
        - Temp:      Temporary files
        - Downloads: Downloaded files
    """
    def __init__(self, app_name: str="Broken", app_author: str="BrokenSource", echo=True):

        # App information
        self.app_name   = app_name
        self.app_author = app_author
        self.APPDIRS    = AppDirs(app_author, app_author)

        # Special directories
        self.ROOT = Path(self.APPDIRS.user_data_dir)#/self.app_name
        self.ROOT.mkdir(parents=True, exist_ok=True)

        # On Source Code mode is the __init__.py file's parent, on release is the executable's parent
        self.PACKAGE   = BrokenDirectories.get_system_executable_directory()
        self.RESOURCES = self.PACKAGE/"Resources"

        # Log info and root dir for user convenience
        # log.info(f"Project Directories [AppName: {app_name}] by [AppAuthor: {app_author}] at [{self.ROOT}]", echo=echo)

    def __getattr__(self, name: str) -> Path:
        """Attributes not found are assumed to be a new project directory"""
        return self.new_project_directory(name)

    def new_project_directory(self, name: Path) -> Path:
        """Make a new directory relative to the project's root"""
        name = name.capitalize()
        directory = self.ROOT/name
        directory.mkdir(parents=True, exist_ok=True)
        setattr(self, name.upper(), directory)
        return directory

    def get_system_executable_directory() -> Path:
        """Smartly gets the current "executable" of the current scope, or the release binary's path"""
        if BROKEN_PYINSTALLER:
            return Path(sys.executable).parent.absolute().resolve()
        elif BROKEN_NUITKA:
            return Path(sys.argv[0]).parent.absolute().resolve()
        else:
            return Path(inspect.stack()[2].filename).parent.absolute().resolve()

# Broken package shared and common directories
BROKEN_DIRECTORIES = BrokenDirectories(echo=False)

# Root of BrokenSource Monorepo
BROKEN_MONOREPO_DIR = BROKEN_DIRECTORIES.PACKAGE.parent
BROKEN_SYS_ROOT_DIR = Path("/").absolute().resolve()

# Where Broken shall be placed as a symlink to be shared
# (on other pyproject.toml have it as broken = {path="/Broken", develop=true})
BROKEN_SHARED_DIR = BROKEN_SYS_ROOT_DIR/"Broken"

# Constants
USERNAME = os.environ.get("USER") or os.environ.get("USERNAME")
HOME_DIR = Path.home()