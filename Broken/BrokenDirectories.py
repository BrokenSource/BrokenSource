from . import *


@attrs.define(slots=False, hash=True)
class BrokenDirectories:

    # App information
    app_name:   str     = attrs.field(default="Broken")
    app_author: str     = attrs.field(default="BrokenSource")
    app_dirs:   AppDirs = attrs.field(default=None)

    def __attrs_post_init__(self):
        self.app_dirs = AppDirs(self.app_author, self.app_author)

        # Load .env file on the package
        if (env := self.PACKAGE/".env").exists():
            log.info(f"Loading environment variables from: {env}")
            dotenv.load_dotenv(env)

    def __mkdir__(self, path: Path) -> Path:
        """Make a directory and return it"""
        path = Path(path).absolute()
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
    def PACKAGE(self, level: int=0):
        """
        Source Code:
            Returns the __init__.py file's parent directory
            (where 'shared' and 'common' directories are located)

        Compiled:
            Returns the executable's directory
        """
        if BROKEN_PYINSTALLER:
            return Path(sys.executable).parent.absolute().resolve()

        elif BROKEN_NUITKA:
            return Path(sys.argv[0]).parent.absolute().resolve()

        # Search as when the stack's self is not the current selv
        while (stack := inspect.stack()[level := level+1]):
            if stack.frame.f_locals.get("self", None) != self:
                break

        return Path(stack.filename).parent.parent.absolute().resolve()

    @property
    @cache
    def WORKSPACE(self) -> Path:
        if (path := os.environ.get("WORKSPACE", None)):
            return self.__mkdir__(Path(path)/self.app_author/self.app_name)
        return self.__mkdir__(Path(self.app_dirs.user_data_dir)/self.app_name)

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
        return self.__mkdir__(self.SYSTEM_ROOT/"Broken")

    # # Broken monorepo specific, potentially useful

    @property
    def RELEASES(self) -> Path:
        return self.__mkdir__(self.PACKAGE/"Release")

    @property
    def BUILD(self) -> Path:
        return self.__mkdir__(self.PACKAGE/"Build")

    @property
    def WINEPREFIX(self) -> Path:
        return self.__mkdir__(self.BUILD/"Wineprefix")

    @property
    def PROJECTS(self) -> Path:
        return self.__mkdir__(self.PACKAGE/"Projects")

    @property
    def HOOK(self) -> Path:
        return self.__mkdir__(self.PROJECTS/"Hook")

    # # Meta directories - Broken monorepo specific

    @property
    def META(self) -> Path:
        return self.__mkdir__(self.PACKAGE/"Meta")

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
    def RESOURCES(self) -> Path:
        return self.__mkdir__(self.PACKAGE/"Resources")

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

# Broken package shared and common directories
BROKEN_DIRECTORIES = BrokenDirectories()
