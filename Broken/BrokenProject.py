from __future__ import annotations

from . import *


@attrs.define(slots=False)
class _BrokenProjectDirectories:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # App basic information
    APP_DIRS: AppDirs = attrs.field(default=None)

    def __attrs_post_init__(self):
        self.APP_DIRS = AppDirs(
            self.BROKEN_PROJECT.APP_AUTHOR,
            self.BROKEN_PROJECT.APP_AUTHOR
        )

    @property
    def PACKAGE(self) -> Path:
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
        self.__dict__[name] = value if not isinstance(value, Path) else self.__mkdir__(value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    # # Base directories

    @property
    def WORKSPACE(self) -> Path:
        if (path := os.environ.get("WORKSPACE", None)):
            return self.__mkdir__(Path(path)/self.APP_AUTHOR/self.APP_NAME)
        return self.__mkdir__(Path(self.APP_DIRS.user_data_dir)/self.APP_NAME)

    @property
    def REPOSITORY(self) -> Path:
        return self.__mkdir__(self.PACKAGE.parent)

    @property
    def HOME(self) -> Path:
        return self.__mkdir__(Path.home())

    # # Common system directories

    @property
    def SYSTEM_ROOT(self) -> Path:
        """(Unix: /), (Windows: C://)"""
        return self.__mkdir__("/")

    @property
    def BROKEN_SHARED(self) -> Path:
        """Returns the shared directory of Broken"""
        return self.__mkdir__(self.HOME/".BrokenSource", resolve=False)

    # # Broken monorepo specific, potentially useful

    @property
    def BROKEN_RELEASES(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Release")

    @property
    def BROKEN_BUILD(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Build")

    @property
    def BROKEN_WINEPREFIX(self) -> Path:
        return self.__mkdir__(self.BUILD/"Wineprefix")

    @property
    def BROKEN_PROJECTS(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Projects")

    @property
    def HOOK(self) -> Path:
        return self.__mkdir__(self.PROJECTS/"Hook")

    # # Meta directories - Broken monorepo specific

    @property
    def META(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Meta")

    @property
    def DOCS(self) -> Path:
        return self.__mkdir__(self.META/"Docs")

    @property
    def PAPERS(self) -> Path:
        return self.__mkdir__(self.META/"Papers")

    @property
    def TEMPLATES(self) -> Path:
        return self.__mkdir__(self.META/"Templates")

    @property
    def WEBSITE(self) -> Path:
        return self.__mkdir__(self.META/"Website")

    @property
    def _ASSETS(self) -> Path:
        return self.__mkdir__(self.META/"Assets")

    # # Workspace directories

    @property
    def CONFIG(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Data")

    @property
    def PROJECTS(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Projects")

    @property
    def DOWNLOADS(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Downloads")

    @property
    def EXTERNALS(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Externals")

    @property
    def TEMP(self) -> Path:
        return self.__mkdir__(self.WORKSPACE/"Temp")

# -------------------------------------------------------------------------------------------------|

@attrs.define(slots=False)
class _BrokenProjectResources:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # # Internal states

    __RESOURCES__: Path = attrs.field(default=None)

    def __attrs_post_init__(self):
        if self.BROKEN_PROJECT.RESOURCES:
            self.__RESOURCES__ = importlib.resources.files(self.BROKEN_PROJECT.RESOURCES)

    # # Branding section

    @property
    def ICON(self) -> Path:
        return self.__RESOURCES__/f"{self.BROKEN_PROJECT.APP_NAME}.png"

    # # Shaders section

    @property
    def SHADERS(self) -> Path:
        return self.__RESOURCES__/"Shaders"

    @property
    def FRAGMENT(self) -> Path:
        return self.SHADERS/"Fragment"

    @property
    def VERTEX(self) -> Path:
        return self.SHADERS/"Vertex"

    # Divide operator -> Get a path relative to the root

    def __div__(self, name: str) -> Path:
        return self.__RESOURCES__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

# -------------------------------------------------------------------------------------------------|

@attrs.define(slots=False)
class BrokenProject:
    # Note: Send the importer's __init__.py's __file__ variable
    PACKAGE: str

    # App information
    APP_NAME:   str     = attrs.field(default="Broken")
    APP_AUTHOR: str     = attrs.field(default="BrokenSource")

    # Standard Broken objects for a project
    DIRECTORIES: _BrokenProjectDirectories = None
    RESOURCES:   _BrokenProjectResources   = None
    CONFIG:      BrokenDotmap              = None

    def __attrs_post_init__(self):

        # Create Directories class
        self.DIRECTORIES = _BrokenProjectDirectories(BROKEN_PROJECT=self)
        self.RESOURCES   = _BrokenProjectResources  (BROKEN_PROJECT=self)

        # Create default config
        self.CONFIG = BrokenDotmap(path=self.DIRECTORIES.CONFIG/f"{self.APP_NAME}.toml")

        # Create logger based on configuration
        try:
            # Fixme: Two logging instances on the same file on Windows
            BrokenLogging().stdout(__loglevel__ := self.CONFIG.logging.default("level", "trace").upper())
            BrokeLogging().file(BROKEN.DIRECTORIES.LOGS/"Broken.log", __loglevel__)
        except Exception:
            pass

        # Fixme: Anywhere to unify envs?
        # Load .env files from the project
        for env in self.DIRECTORIES.REPOSITORY.glob("*.env"):
            log.info(f"Loading environment variables ({env})")
            dotenv.load_dotenv(env)
