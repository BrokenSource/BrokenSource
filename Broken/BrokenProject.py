from . import *


@attrs.define(slots=False)
class BrokenProjectDirectories:

    # App information
    PACKAGE: Path

    APP_NAME:   str     = attrs.field(default="Broken")
    APP_AUTHOR: str     = attrs.field(default="BrokenSource")
    APP_DIRS:   AppDirs = attrs.field(default=None)

    def __attrs_post_init__(self):
        self.APP_DIRS = AppDirs(self.APP_AUTHOR, self.APP_AUTHOR)

        # Find the package directory
        if BROKEN_PYINSTALLER:
            self.PACKAGE = Path(sys.executable).parent.resolve()
        elif BROKEN_NUITKA:
            self.PACKAGE = Path(sys.argv[0]).parent.resolve()
        else:
            self.PACKAGE = Path(self.PACKAGE).parent.resolve()

        print(self.APP_NAME, self.PACKAGE)

        # Load .env file on the package
        if (env := self.PACKAGE/".env").exists():
            log.info(f"Loading environment variables from: {env}")
            dotenv.load_dotenv(env)

    def __mkdir__(self, path: Path) -> Path:
        """Make a directory and return it"""
        path = Path(path).resolve()
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
        return self.__mkdir__(self.HOME/".BrokenSource")

    # # Broken monorepo specific, potentially useful

    @property
    def RELEASES(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Release")

    @property
    def BUILD(self) -> Path:
        return self.__mkdir__(self.REPOSITORY/"Build")

    @property
    def WINEPREFIX(self) -> Path:
        return self.__mkdir__(self.BUILD/"Wineprefix")

    @property
    def PROJECTS(self) -> Path:
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
class BrokenProject:

    # App information
    APP_NAME:   str     = attrs.field(default="Broken")
    APP_AUTHOR: str     = attrs.field(default="BrokenSource")
    RESOURCES:  Any = None

    DIRECTORIES: BrokenProjectDirectories = None
    CONFIG:      BrokenDotmap             = None

    def __init__(self, __file__, *args, **kwargs):
        self.__attrs_init__(*args, **kwargs)

        # Create Directories class
        self.DIRECTORIES = BrokenProjectDirectories(
            PACKAGE=__file__,
            APP_NAME=self.APP_NAME,
            APP_AUTHOR=self.APP_AUTHOR,
        )

        # Create default config
        self.CONFIG = BrokenDotmap(path=self.DIRECTORIES.CONFIG/f"{self.APP_NAME}.toml")
        self.RESOURCES = importlib.resources.files(self.RESOURCES) if self.RESOURCES else None

        # Create logger based on configuration
        try:
            # Fixme: Two logging instances on the same file on Windows
            BrokenLogging().stdout(__loglevel__ := self.CONFIG.logging.default("level", "trace").upper())
            BrokeLogging().file(BROKEN.DIRECTORIES.LOGS/"Broken.log", __loglevel__)
        except Exception:
            pass

