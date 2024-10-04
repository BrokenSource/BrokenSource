#!/usr/bin/env python3
__version__ = "0.7.0.dev1"
__all__ = ["__version__"]

# Continuous Integration options
BROKEN_VERSION: str = __version__
BROKEN_PYAPP: bool = True
BROKEN_PYPI: bool = True
BROKEN_TAG: bool = True

if (__name__ == "__main__"):
    print(f"{BROKEN_VERSION=}")
    print(f"{BROKEN_PYAPP=}")
    print(f"{BROKEN_PYPI=}")
    print(f"{BROKEN_TAG=}")
