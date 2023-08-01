from . import *

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(
    datetime.timedelta, "milliseconds",
    property(lambda self: f"{(self.seconds*1000 + self.microseconds/1000):5.0f}")
)

# Set up empty logger
loguru.logger.remove()
logger = loguru.logger.bind()

# Get the current project name that imported Broken, on the logging format a
# lambda is needed to inject the current project name into the format string
BROKEN_CURRENT_PROJECT_NAME = os.environ.get("BROKEN_CURRENT_PROJECT_NAME", "Broken")
BROKEN_LOG_LEVEL = os.environ.get("LOG_LEVEL", "TRACE").upper()

def _make_logging_format(type: Option["stdout", "file"]="stdout") -> str:

    if type == "stdout":
        # Get the project name color, "dim" Broken since it's the manager
        project_color = "dim" if (BROKEN_CURRENT_PROJECT_NAME == "Broken") else "light-blue"

        # Beautiful logging format for the terminal
        return (
            f"│<{project_color}>{BROKEN_CURRENT_PROJECT_NAME.ljust(10)}</{project_color}>├┤<green>{{elapsed.milliseconds}}ms</green>├"
            "┤<level>{level:7}</level>"
            "│ ▸ <level>{message}</level>"
        )

    elif type == "file":
        # Nice logging format, no colors, detailed
        return (
            f"[{BROKEN_CURRENT_PROJECT_NAME}]"
            "[{time:YYYY-MM-DD HH:mm:ss}]-"
            "[{elapsed.milliseconds}ms]-"
            "[{level:7}]"
            " ▸ {message}"
        )
    else:
        log.error(f"Unknown logging type: {type}")
        raise ValueError(f"Unknown logging type: {type}")

# Add stdout logging
logger.add(sys.stdout, colorize=True, level=BROKEN_LOG_LEVEL,
    format=_make_logging_format(type="stdout")
)

# Uncolored raw text logging asame format as above
def add_logging_file(path: PathLike):
    logger.add(path, level=BROKEN_LOG_LEVEL, format=_make_logging_format(type="file"))

def add_log_option(name: str, loglevel: int=0, color: str=None):

    def log(*args, echo=True, **kwargs):
        if not echo: return
        loguru.logger.log(name, ' '.join(map(str, args)), **kwargs)

    # Maybe add new log level, TypeErrors if it already exists
    try:
        loguru.logger.level(name, loglevel, f"<{color}><bold>" if color else "<bold>")
    except TypeError:
        pass

    # Assign function, return it
    loguru.logger.name = log
    return loguru.logger.name

log = logger

log.info      = add_log_option("INFO")
log.warning   = add_log_option("WARNING")
log.error     = add_log_option("ERROR")
log.debug     = add_log_option("DEBUG")
log.trace     = add_log_option("TRACE")
log.success   = add_log_option("SUCCESS")
log.critical  = add_log_option("CRITICAL")
log.exception = add_log_option("EXCEPTION")

# Custom logging functions
log.fixme = add_log_option("FIXME", 35, "cyan")
log.todo  = add_log_option("TODO",  35, "blue")
log.note  = add_log_option("NOTE",  35, "magenta")
log.minor = add_log_option("MINOR", 35, "fg #777")
