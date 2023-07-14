"""See BrokenDict class documentation"""
from . import *


class BrokenDotmap(dict):
    """
    Trivia
    • Tremeschin 🐙 🎲 🌿 🔱 🪶, [7/7/23 1:29 AM]
    • I just made the most cursed user friendly lazy dictionary you'll ever see

    # Description
    BrokenDict is a file-synced dictionary similar to DotMap with some extra utilities
    - Any dictionary modification outside .no_sync() context will be synced to the file
    - Utility function ._default(key, value) to set a default value for a key
    - Support for TOML, JSON, YAML file formats, just specify the file extension of path on creation

    # Usage
    ```python
    broken_dict = BrokenDict("path/to/file.{toml,json,yaml}")

    # Assignment
    broken_dict["key"] = "value"
    broken_dict.key = "value"

    # Nested works
    broken_dict.nested.key = "value"

    # Default values (returns key if exists else sets value)
    broken_dict._default("key", "value")

    # Load from dictionary (loads dict into broken_dict["key"] = {"cat": "dog"})
    broken_dict.key.from_dict({"cat": "dog"})

    # Get dictionary from this instance nest downwards
    broken_dict.dict
    broken_dict.nested.dict

    # Load dictionary from also any TOML, JSON, YAML file
    broken_dict.inner_loaded.from_file("path/to/file.{toml,json,yaml}")
    ```
    """

    is_dunder = lambda key: key.startswith("__") and key.endswith("__")

    def __init__(self, path: Path, sorted=True, super: Self=None):
        """
        Initializes BrokenDict, reads from file or creates it if it doesn't exist
        - **Do not send `super` argument unless you know what you're doing**
        """

        # A reference to the root instance of the dictionaries
        self.__super__ = super or self

        # This instance is the root instance
        if super is None:
            self.__path__   = BrokenPath.true_path(path)
            self.__sorted__ = sorted
            self.__sync__   = True

            # Information on screen
            info(f"• New BrokenDict instance created")
            if self.__path__.exists():
                info(f"└─ Loading from File: [{self.__path__}]")
                self.from_file(self.__path__)
            else:
                info(f"└─ Creating new File: [{self.__path__}]")

    @property
    def dict(self):
        """Get a dictionary from this instance downwards"""
        return {
            k: v.dict if isinstance(v, self.__class__) else v
            for k, v in (
                sorted(self.items(), key=lambda x: x[0])
                if self.__super__.__sorted__ else self.items()
            )
            if not BrokenDotmap.is_dunder(k)
        }

    def inverse(self, value: Any) -> Any:
        """Search by value"""
        return next((k for k, v in self.items() if v == value), None)

    # # Loading and saving

    def from_file(self, path: Path):
        """Load a file into this nested instance"""
        path = BrokenPath.true_path(path)
        format = path.suffix

        # Load data from file
        try:
            if format == ".toml":
                data = toml.loads(path.read_text())
            elif format == ".json":
                data = json.loads(path.read_text())
            elif format == ".yaml":
                data = yaml.load(path.read_text(), Loader=yaml.FullLoader)
            else:
                error(f"• BrokenDict: Unknown file format")
                error(f"└─ File: [{path}]")
                return

        except Exception as e:
            error(f"• BrokenDict: Failed to load file [{path}]")
            error(f"└─ {e}")
            exit(1)

        self.from_dict(data)

    # # From / to methods

    def from_dict(self, data={}) -> Self:
        """Append a dictionary to this instance"""
        for key, value in (data or {}).items():
            super().__setitem__(key, self.__recurse__(value))
        self._sync()
        return self

    # # Utilities

    @contextmanager
    def no_sync(self, sync_after=True) -> None:
        """Temporarily disables syncing, for example bulk operations"""
        self.__sync__ = False
        yield None
        self.__sync__ = True
        if sync_after:
            self._sync()

    def _default(self, key: str, value: Any) -> Any:
        """Set a default value for a key else don't change, returns it"""
        if key not in self:
            self[key] = value
        return self[key]

    # # Internal dunder methods

    def __recurse__(self, value={}) -> Union[Self, Any]:
        """Transforms a dict-like into Self or return the value itself"""
        if isinstance(value, dict):
            nested = self.__class__(path=None, super=self.__super__)
            nested.from_dict(value)
            value = nested
        return value

    # Get methods

    def __get__(self, key) -> Union[Self, Any]:
        """If a key doesn't exist, recurse, else return its the value"""
        return super().setdefault(key, self.__recurse__())

    def __getitem__(self, key) -> Union[Self, Any]:
        """Handle dictionary item access using key indexing"""
        return self.__get__(key)

    def __getattr__(self, key) -> Union[Self, Any]:
        """Handle attribute access using dot notation"""
        return self.__get__(key)

    # Set methods

    def __set__(self, key, value={}) -> None:
        """Set a key to a value, recurses on the value"""
        super().__setitem__(key, self.__recurse__(value))
        self._sync()

    def __setitem__(self, key, value) -> None:
        """Handle dictionary item assignment using key indexing"""
        self.__set__(key, value)

    def __setattr__(self, key, value) -> None:
        """Handle attribute assignment using dot notation"""

        # Do not "recurse" on dunder attributes, they are self!
        if BrokenDotmap.is_dunder(key):
            self.__dict__[key] = value
            return

        self.__set__(key, value)

    # # Internal save to file method

    def _sync(self) -> None:
        """Save dictionary data to the specified file"""

        # Don't sync mode
        if not self.__super__.__sync__:
            return

        # Get the full dictionary to save
        format = self.__super__.__path__.suffix
        dict  = self.__super__.dict

        # Load file based on format
        if format == ".toml":
            data = toml.dumps(dict)
        elif format == ".json":
            data = json.dumps(dict, indent=2, ensure_ascii=False)
        elif format == ".yaml":
            data = yaml.dump(dict)
        else:
            error(f"BrokenDict: Unknown file format [{format}], cannot save to file")
            return

        # Write to file the full dictionary data
        self.__super__.__path__.write_text(data)
