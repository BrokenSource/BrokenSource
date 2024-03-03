from . import *

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(
    datetime.timedelta, "milliseconds",
    property(lambda self: f"{(self.seconds*1000 + self.microseconds/1000):5.0f}")
)

class BrokenLogging:

    # # Singleton

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "singleton"):
            cls.singleton = super().__new__(cls)
            cls.singleton.__start__()
        return cls.singleton

    def __start__(self):
        """__init__ but for the singleton"""
        self.reset()

    # # Context information

    @property
    def project(self):
        """Current project name"""
        return os.environ.get("BROKEN_CURRENT_PROJECT_NAME", "Broken")

    @property
    def project_color(self):
        """Current project 'logging color'"""
        return "dim" if (self.project == "Broken") else "light-blue"

    # # Output log places

    def reset(self):
        """Reset logger bindings"""
        loguru.logger.remove()
        self.logger = loguru.logger.bind()
        self.__loglevel__()

    def stdout(self, loglevel: str) -> Self:
        """Add stdout logging"""
        self.reset()
        self.logger.add(
            sys.stdout,
            colorize=True,
            level=loglevel,
            format=(
                f"\r│<{self.project_color}>{self.project.ljust(10)}</{self.project_color}>├"
                "┤<green>{elapsed.milliseconds}ms</green>├"
                "┤<level>{level:7}</level>"
                "│ ▸ <level>{message}</level>"
            )
        )
        return self

    def file(self, path: PathLike, loglevel: str, empty: bool=True) -> Self:
        """Add file logging"""

        # Remove
        if (path := Path(path)).exists() and empty:
            path.unlink()

        self.logger.add(
            path,
            level=loglevel,
            format=(
                f"({self.project})"
                "({time:YYYY-MM-DD HH:mm:ss})-"
                "({elapsed.milliseconds}ms)-"
                "({level:7})"
                " ▸ {message}"
            )
        )
        return self

    # # Add new log levels

    def __add_loglevel__(self, name: str, loglevel: int=0, color: str=None) -> Self:
        """Create a new loglevel `.{name.lower()}` on the logger"""
        def log(*args, echo=True, **kwargs) -> str:
            message = " ".join(map(str, args))
            if not echo:
                return message
            self.logger.log(name, message, **kwargs)
            return message

        # Create new log level on logger
        try:
            self.logger.level(name, loglevel, f"<{color}><bold>" if color else "<bold>")
        except TypeError:
            pass

        # Assign log function to logger
        setattr(self.logger, name.lower(), log)
        return self

    def __loglevel__(self) -> Self:
        """Bootstrap better log levels"""

        # Override default ones for echo= argument
        self.__add_loglevel__("INFO")
        self.__add_loglevel__("WARNING")
        self.__add_loglevel__("ERROR")
        self.__add_loglevel__("DEBUG")
        self.__add_loglevel__("TRACE")
        self.__add_loglevel__("SUCCESS")
        self.__add_loglevel__("CRITICAL")
        self.__add_loglevel__("EXCEPTION")

        # Add custom ones
        self.__add_loglevel__("FIXME",  35, "cyan"      )
        self.__add_loglevel__("TODO",   35, "blue"      )
        self.__add_loglevel__("NOTE",   35, "magenta"   )
        self.__add_loglevel__("MINOR",  35, "fg #777"   )
        self.__add_loglevel__("ACTION", 35, "fg #7340ff")
        self.__add_loglevel__("SKIP",   35, "fg #777"   )

        return self

# Initialize logging class
log = BrokenLogging().stdout("CRITICAL").logger

# -------------------------------------------------------------------------------------------------|

# I hope one day to implement a log-able pretty exceptions
class BrokenExceptions:
    def hook(self, exception_type, value, traceback) -> None:
        ...
