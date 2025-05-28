#!/usr/bin/env python3

# Manual trigger count: 1
__version__ = "0.9.0.dev1"
__options__ = dict(
    GHA_VERSION=__version__,
)

# Export options to environment
if (__name__ == "__main__"):
    for (key, value) in __options__.items():
        if isinstance(value, bool):
            value = int(value)
        print(f"{key}={value}")
