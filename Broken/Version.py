#!/usr/bin/env python3
__version__ = "0.8.0"
__all__ = ["__version__"]

def export(**options) -> None:
    for key, value in options.items():
        print(f"{key}={value}")

if (__name__ == "__main__"):
    export(
        GHA_VERSION=__version__,
        GHA_PYAPP=True,
        GHA_PYPI=True,
        GHA_TAG=True,
    )
