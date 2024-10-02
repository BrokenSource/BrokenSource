#!/usr/bin/env python3
__version__ = "0.7.0.dev1"
__all__ = ["__version__"]

# Continuous Integration options
BROKEN_VERSION: str = __version__
BROKEN_BINARY: bool = False
BROKEN_PYPI: bool = False
BROKEN_TAG: bool = False

if __name__ == "__main__":
    print(f"{BROKEN_VERSION=}")
    print(f"{BROKEN_BINARY=}")
    print(f"{BROKEN_PYPI=}")
    print(f"{BROKEN_TAG=}")
