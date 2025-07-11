#!/usr/bin/env python3
__version__ = "0.9.2"
__options__ = dict(
    GHA_VERSION=__version__,
)

# Export options to environment
if (__name__ == "__main__"):
    for (key, value) in __options__.items():
        if isinstance(value, bool):
            value = int(value)
        print(f"{key}={value}")
