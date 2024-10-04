#!/usr/bin/env python3
__version__ = "0.7.0"
__all__ = ["__version__"]

def export(**options) -> None:
    for key, value in options.items():
        print(f"{key}={value}")

if (__name__ == "__main__"):
    export(
        BROKEN_VERSION=__version__,
        BROKEN_PYAPP=True,
        BROKEN_PYPI=True,
        BROKEN_TAG=True,
    )
