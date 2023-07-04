from . import *

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(
    datetime.timedelta, "milliseconds",
    property(lambda self: f"{(self.seconds*1000 + self.microseconds/1000):5.0f}")
)

# Set up empty logger
loguru.logger.remove()
logger = loguru.logger.bind()

# Add stdout logging
logger.add(system.stdout, colorize=True, level="TRACE",
    format=(
        "│<green>{elapsed.milliseconds}ms</green>├"
        "┤<level>{level:7}</level>"
        "│ ▸ <level>{message}</level>"
    )
)

# Uncolored raw text logging asame format as above
def add_logging_file(path: PathLike):
    logger.add(path, level="TRACE",
        format=(
            "[{time:YYYY-MM-DD HH:mm:ss}]-"
            "[{elapsed.milliseconds}ms]-"
            "[{level:7}]"
            " ▸ {message}"
        )
    )

def _new_logging_function(name: str, loglevel: int=0, color: str=None):

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

# Default logging functions
_new      = _new_logging_function
info      = _new("INFO")
warning   = _new("WARNING")
error     = _new("ERROR")
debug     = _new("DEBUG")
trace     = _new("TRACE")
success   = _new("SUCCESS")
critical  = _new("CRITICAL")
exception = _new("EXCEPTION")

# Custom logging functions
fixme     = _new("FIXME", 35, "cyan")
todo      = _new("TODO",  35, "blue")
note      = _new("NOTE",  35, "magenta")
