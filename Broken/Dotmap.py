import contextlib
import json
import pickle
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
from typing import Self
from typing import Union

import toml
import yaml

from Broken.Base import BrokenPath
from Broken.Logging import log


class BrokenDotmap:
    """
    Trivia
    • Tremeschin 🐙 🎲 🌿 🔱 🪶, [7/7/23 1:29 AM]
    • I just made the most cursed user friendly lazy dictionary you'll ever see

    # Description
    BrokenDict is a file-synced (or not!) dictionary similar to DotMap with some extra utilities
    - Support for TOML, JSON, YAML file formats, just specify the file extension of path on creation
    - Utility function .default(key, value) to set a default value for a key and sync it
    - Any dictionary modification outside .no_sync() context will be synced to the file

    # Usage
    ```python
    # Any file format or None for file-less operation
    broken_dict = BrokenDict("path/to/file.{toml,json,yaml}")

    # Assignment
    broken_dict["key"] = "value"
    broken_dict.key = "value"

    # Nested works
    broken_dict.nested.key = "value"

    # Default values (returns key if exists else sets value)
    broken_dict.default("key", "value")

    # Load from dictionary (loads dict into broken_dict["key"] = {"cat": "dog"})
    broken_dict.key.from_dict({"cat": "dog"})

    # Get dictionary from this instance nest downwards
    broken_dict.to_dict()
    broken_dict.nested.to_dict()

    # Load dictionary from also any TOML, JSON, YAML file
    broken_dict.inner_loaded.from_file("path/to/file.{toml,json,yaml}")

    # Do some heavy operations without syncing and then sync
    with broken_dict.no_sync():
        for i in range(100):
            broken_dict.primes[i] = is_prime(i)
    ```
    """

    @staticmethod
    def is_dunder(key: str) -> bool:
        """Check if a key is a dunder attribute"""
        return key.startswith("__") and key.endswith("__")

    def __init__(self,
        path: Path=None,
        sync: bool=True,
        echo: bool=False,
        super: Self=None,
    ):

        # A reference to the root instance of the dictionaries
        self.__super__ = super or self

        # Behavior configuration
        self.__path__ = path
        self.__sync__ = sync

        # Load or create from file
        if self.__path__ is not None:
            self.__path__ = BrokenPath(self.__path__)

            log.info(f"• New BrokenDotmap @ ({self.__path__})", echo=echo)

            if self.__path__.exists():
                self.from_file(self.__path__)
            else:
                self.sync()

    # # Convenience flags

    @property
    def __ext__(self) -> str:
        """Get the file extension of the path"""
        return self.__path__.suffix.lower()

    # # Loading and saving

    def from_dict(self, data: dict={}) -> Self:
        """Append a dictionary to this instance"""
        for key, value in (data or {}).items():
            self.set(key, self.__recurse__(value))
        return self

    def to_dict(self) -> dict:
        """Get a dictionary from this instance downwards"""
        return {
            k: v.to_dict() if isinstance(v, type(self)) else v
            for k, v in sorted(self.items(), key=lambda x: x[0])
            if not BrokenDotmap.is_dunder(k)
        }

    def from_file(self, path: Path) -> Self:
        """Load a file into this dotmap instance"""
        path   = BrokenPath(path)
        format = path.suffix.lower()

        # Load data from file
        try:
            match format:
                case ".toml":
                    data = toml.loads(path.read_text())
                case ".json":
                    data = json.loads(path.read_text())
                case ".yaml":
                    data = yaml.load(path.read_text(), Loader=yaml.FullLoader)
                case ".pickle":
                    data = pickle.loads(path.read_bytes())
                case _:
                    log.error(f"• BrokenDotmap: Unknown file format ({format})")
                    log.error(f"└─ File: ({path})")
                    return

        except Exception as e:
            log.error(f"• BrokenDotmap: Failed to load file ({path})")
            log.error(f"└─ {e}")
            return

        return self.from_dict(data)

    def sync(self, sync: bool=True) -> None:
        """Sync this instance to the file"""
        self.__sync__ = sync
        self.__super__.__sync_to_file__()

    # Internal recursion

    def __recurse__(self, value={}) -> Union[Self, Any]:
        """Transforms a dict-like into Self or return the value itself"""
        if isinstance(value, dict):
            return type(self)(super=self.__super__).from_dict(value)
        return value

    # # Redirect items, keys

    def items(self) -> Dict[str, Any]:
        return self.__dict__.items()

    def keys(self) -> list:
        return list(self.__dict__.keys())

    # # Patch Get methods

    def get(self, key: str) -> Union[Self, Any]:
        """If a key doesn't exist, recurse, else return its the value"""
        return self.__dict__.setdefault(key, self.__recurse__())

    def __getitem__(self, key: str) -> Union[Self, Any]:
        """Handle dictionary item access using key indexing"""
        return self.get(key)

    def __getattr__(self, key: str) -> Union[Self, Any]:
        """Handle attribute access using dot notation"""
        return self.get(key)

    # # Patch Set methods

    def set(self, key: str, value: Any={}) -> Any:
        """Set a key to a value, recurses on the value"""
        self.__dict__[key] = self.__recurse__(value)
        self.sync()
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """Handle dictionary item assignment using key indexing"""
        self.set(key, value)

    def __setattr__(self, key: str, value: Any) -> None:
        """Handle attribute assignment using dot notation"""

        # Do not "recurse" on dunder attributes, they are self!
        if BrokenDotmap.is_dunder(key):
            self.__dict__[key] = value
            return

        self.set(key, value)

    # # Utilities

    def default(self, key: str, value: Any) -> Any:
        """Set a default value for a key else don't change, returns it"""

        # Return the value if it exists
        if key in self.__dict__:
            return self.__dict__[key]

        # Set the value and sync (call it if callable - a use as a cache)
        return self.set(key, value() if callable(value) else value)

    def setdefault(self, key: str, value: Any) -> Any:
        """Set a default value for a key else don't change, returns it"""
        return self.default(key, value)

    @contextlib.contextmanager
    def no_sync(self) -> Generator[None, None, None]:
        """Temporarily disables syncing, for example bulk operations"""
        self.__sync__ = False
        yield None
        self.__sync__ = True
        self._sync()

    def inverse(self, value: Any) -> Any | None:
        """Search by value"""
        return next((k for k, v in self.items() if v == value), None)

    # # Sync

    def __sync_to_file__(self) -> None:

        # Non file mode
        if self.__path__ is None:
            return

        # Don't sync mode
        if not self.__sync__:
            return

        # Get the full dictionary to save
        dict = self.to_dict()

        # Load file based on format
        match self.__ext__:
            case ".toml":
                self.__path__.write_text(toml.dumps(dict))
            case ".json":
                self.__path__.write_text(json.dumps(dict, indent=2, ensure_ascii=False))
            case ".yaml":
                self.__path__.write_text(yaml.dump(dict))
            case ".pickle":
                self.__path__.write_bytes(pickle.dumps(dict))
            case _:
                log.error(f"BrokenDotmap: Unknown file format ({self.__ext__}), cannot save to file")
                return
