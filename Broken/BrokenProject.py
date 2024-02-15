from __future__ import annotations

from . import *


@define(slots=False)
class _BrokenProjectDirectories:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # App basic information
    APP_DIRS: AppDirs = field(default=None)

    def __attrs_post_init__(self):
        args = (self.BROKEN_PROJECT.APP_AUTHOR, self.BROKEN_PROJECT.APP_NAME)
        self.APP_DIRS = AppDirs(*reversed(args) if (os.name == "nt") else args)

    @property
    def PACKAGE(self) -> Path:
        """
        When running from the Source Code:
            - The current project's __init__.py location

        When running from a Release:
            - Directory where the executable is located
        """
        if BROKEN_PYINSTALLER:
            return Path(sys.executable).parent.resolve()
        elif BROKEN_NUITKA:
            return Path(sys.argv[0]).parent.resolve()
        else:
            return Path(self.BROKEN_PROJECT.PACKAGE).parent.resolve()

    # # Convenience properties

    @property
    def APP_NAME(self) -> str:
        return self.BROKEN_PROJECT.APP_NAME

    @property
    def APP_AUTHOR(self) -> str:
        return self.BROKEN_PROJECT.APP_AUTHOR

    # # Internal methods

    def __mkdir__(self, path: Path, resolve: bool=True) -> Path:
        """Make a directory and return it"""
        path = Path(path).resolve() if resolve else Path(path)
        if not path.exists():
            log.info(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)
        return path

    # # Unknown / new project directories

    def __set__(self, name: str, value: Path) -> Path:
        """Create a new directory property if Path is given, else set the value"""
        self.__dict__[name] = value if not isinstance(value, Path) else self.__mkdir__(value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    # # Base directories

    @property
    def REPOSITORY(self) -> Path:
        """Broken Source's Monorepo directory"""
        return self.__mkdir__(self.PACKAGE.parent)

    @property
    def HOME(self) -> Path:
        """(Unix: /home/$USER), (Windows: C://Users//$USER)"""
        return self.__mkdir__(Path.home())

    # # Common system directories

    @property
    def SYSTEM_ROOT(self) -> Path:
        """(Unix: /), (Windows: C://)"""
        return self.__mkdir__("/")

    @property
    def SYSTEM_TEMP(self) -> Path:
        """(Unix: /tmp), (Windows: C://Windows//Temp)"""
        return self.__mkdir__(tempfile.gettempdir())

    # # Broken monorepo specific, potentially useful

    @property
    def BROKEN_BRAKEIT(self) -> Path:
        """Brakeit bootstrap script"""
        return self.__mkdir__(self.REPOSITORY/"brakeit.py")

    @property
    def BROKEN_RELEASES(self) -> Path:
        """Broken Source's Monorepo general Releases directory"""
        return self.__mkdir__(self.REPOSITORY/"Release")

    @property
    def BROKEN_BUILD(self) -> Path:
        """Broken Source's Monorepo general Build directory"""
        return self.__mkdir__(self.REPOSITORY/"Build")

    @property
    def BROKEN_WINEPREFIX(self) -> Path:
        """Broken Source's Monorepo Wineprefix directory for Build"""
        return self.__mkdir__(self.BUILD/"Wineprefix")

    @property
    def BROKEN_PROJECTS(self) -> Path:
        """Broken Source's Monorepo Projects directory"""
        return self.__mkdir__(self.REPOSITORY/"Projects")

    @property
    def BROKEN_HOOK(self) -> Path:
        """Hook directory for other projects to be managed by Broken"""
        return self.__mkdir__(self.PROJECTS/"Hook")

    @property
    def BROKEN_META(self) -> Path:
        """Broken Source's Monorepo Meta directory (Many submodules there)"""
        return self.__mkdir__(self.REPOSITORY/"Meta")

    @property
    def BROKEN_PRIVATE(self) -> Path:
        """Broken Source's Monorepo Private directory"""
        return self.__mkdir__(self.REPOSITORY/"Private")

    # # Meta directories - Broken monorepo specific

    @property
    def DOCS(self) -> Path:
        """Broken Source's Monorepo Docs directory"""
        return self.__mkdir__(self.REPOSITORY/"Docs")

    @property
    def WEBSITE(self) -> Path:
        """Broken Source's Website directory"""
        return self.__mkdir__(self.REPOSITORY/"Website")

    @property
    def PAPERS(self) -> Path:
        """Broken Source's Monorepo Papers directory"""
        return self.__mkdir__(self.META/"Papers")

    @property
    def TEMPLATES(self) -> Path:
        """Broken Source's Monorepo Templates directory"""
        return self.__mkdir__(self.META/"Templates")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        """Root for the current Project's Workspace"""
        if (path := os.environ.get("WORKSPACE", None)):
            return self.__mkdir__(Path(path)/self.APP_AUTHOR/self.APP_NAME)
        if (os.name == "nt"):
            return self.__mkdir__(Path(self.APP_DIRS.user_data_dir))
        else:
            return self.__mkdir__(Path(self.APP_DIRS.user_data_dir)/self.APP_NAME)

    @property
    def CONFIG(self) -> Path:
        """General config directory"""
        return self.__mkdir__(self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        """General logs directory"""
        return self.__mkdir__(self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        """General cache directory"""
        return self.__mkdir__(self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        """General Data directory"""
        return self.__mkdir__(self.WORKSPACE/"Data")

    @property
    def MOCK(self) -> Path:
        """Mock directory for testing"""
        return self.__mkdir__(self.WORKSPACE/"Mock")

    @property
    def PROJECTS(self) -> Path:
        """Projects directory (e.g. Video Editor or IDEs)"""
        return self.__mkdir__(self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        """Output directory if it makes more sense than .DATA or .PROJECTS"""
        return self.__mkdir__(self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        """Downloads directory"""
        return self.__mkdir__(self.WORKSPACE/"Downloads")

    @property
    def EXTERNALS(self) -> Path:
        """Third party dependencies"""
        return self.__mkdir__(self.WORKSPACE/"Externals")

    @property
    def TEMP(self) -> Path:
        """Temporary directory for working files"""
        return self.__mkdir__(self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        """Dump directory for debugging (e.g. Shaders)"""
        return self.__mkdir__(self.WORKSPACE/"Dump")

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class _BrokenProjectResources:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # # Internal states

    __RESOURCES__: Path = field(default=None)

    def __attrs_post_init__(self):
        if self.BROKEN_PROJECT.RESOURCES:
            self.__RESOURCES__ = importlib.resources.files(self.BROKEN_PROJECT.RESOURCES)

    def __div__(self, name: str) -> Path:
        return self.__RESOURCES__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Branding section

    @property
    def ICON(self) -> Path:
        """Application icon in PNG format"""
        return self.__RESOURCES__/f"{self.BROKEN_PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        """Application icon in ICO format"""
        return self.__RESOURCES__/f"{self.BROKEN_PROJECT.APP_NAME}.ico"

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        """Scenes directory"""
        return self.__RESOURCES__/"Scenes"

    @property
    def SHADERS(self) -> Path:
        """Shaders directory - May you use .FRAGMENT and .VERTEX?"""
        return self.__RESOURCES__/"Shaders"

    @property
    def SHADERS_INCLUDE(self) -> Path:
        """Shaders include directory"""
        return self.SHADERS/"Include"

    @property
    def FRAGMENT(self) -> Path:
        """Fragment shaders directory"""
        return self.SHADERS/"Fragment"

    @property
    def VERTEX(self) -> Path:
        """Vertex shaders directory"""
        return self.SHADERS/"Vertex"

    # # Generic

    @property
    def PROMPTS(self) -> Path:
        """Prompts directory"""
        return self.__RESOURCES__/"Prompts"

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class BrokenProject:
    # Note: Send the importer's __init__.py's __file__ variable
    PACKAGE: str

    # App information
    APP_NAME:   str = field(default="Broken")
    APP_AUTHOR: str = field(default="BrokenSource")

    # Standard Broken objects for a project
    DIRECTORIES: _BrokenProjectDirectories = None
    RESOURCES:   _BrokenProjectResources   = None
    CONFIG:      BrokenDotmap              = None
    CACHE:       BrokenDotmap              = None
    VERSION:     str                       = None

    def __attrs_post_init__(self):

        # Create Directories class
        self.DIRECTORIES = _BrokenProjectDirectories(BROKEN_PROJECT=self)
        self.RESOURCES   = _BrokenProjectResources  (BROKEN_PROJECT=self)
        self.PACKAGE     = Path(self.PACKAGE)

        # Assign version - Package's parent folder name
        self.VERSION = importlib.metadata.version(self.PACKAGE.parent.name
            .replace("Broken", "broken-source")
        )

        # Create default config
        self.CONFIG = BrokenDotmap(path=self.DIRECTORIES.CONFIG/f"{self.APP_NAME}.toml")
        self.CACHE  = BrokenDotmap(path=self.DIRECTORIES.SYSTEM_TEMP/f"{self.APP_NAME}.pickle")

        # Create logger based on configuration
        os.environ["BROKEN_CURRENT_PROJECT_NAME"] = self.APP_NAME
        self.__START_LOGGING__()

        # Convenience: Symlink Workspace to projects data directory
        if BROKEN_DEVELOPMENT:
            try:
                BrokenPath.symlink(
                    virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
                    real=self.DIRECTORIES.WORKSPACE,
                    echo=False
                )
            except Exception as e:
                log.minor(f"Failed to symlink Workspace: {e}")

        # Fixme: Anywhere to unify envs?
        # Load .env files from the project
        for env in self.DIRECTORIES.REPOSITORY.glob("*.env"):
            log.minor(f"Loading environment variables at ({env})")
            dotenv.load_dotenv(env)

    def welcome(self):
        """Pretty Welcome Message!"""
        import pyfiglet

        # Build message
        message  = [line for line in pyfiglet.figlet_format(self.APP_NAME).split("\n") if line.strip()]
        message += [""]
        message += [f"Made with ❤️ by {self.APP_AUTHOR}, Version: ({self.VERSION})"]
        message += [("Release version." if BROKEN_RELEASE else "Development version") + f" @ Python {sys.version.split()[0]}"]
        message += [""]

        # Get longest line size for centering
        size = max(map(len, message))

        for line in message:
            log.info(line.center(size).rstrip())

    @property
    def LOGLEVEL(self) -> str:
        return (
            os.environ.get("LOGLEVEL", "").upper()
            or self.CONFIG.logging.default("level", "info").upper()
        )

    @LOGLEVEL.setter
    def LOGLEVEL(self, value: str):
        self.CONFIG.logging.level = value
        self.__START_LOGGING__()

    def __START_LOGGING__(self):
        BrokenLogging().reset()
        BrokenLogging().stdout(self.LOGLEVEL)

        # Fixme: Two logging instances on the same file on Windows?
        try:
            BrokenLogging().file(self.DIRECTORIES.LOGS/f"{self.APP_NAME}.log", self.LOGLEVEL)
        except PermissionError as e:
            # Fixme: Two logging instances for the same file on Windows doesn't work
            if os.name == "nt":
                pass
            else:
                raise e
        except Exception as e:
            raise e

# -------------------------------------------------------------------------------------------------|

@define
class BrokenApp(ABC):
    broken_typer: BrokenTyper = None

    @abstractmethod
    def cli(self) -> None:
        pass
