from . import *

# Workaround: Temporary debugging
GLOBAL_UUID = 0
def __next_uuid__():
    global GLOBAL_UUID
    GLOBAL_UUID += 1
    return GLOBAL_UUID

class BrokenDotmap(
    collections.abc.MutableMapping,
    collections.abc.Mapping,
    collections.OrderedDict
):
    def __init__(self,
        data: Dict[str, Any]=None,
        *,
        path: Path=None,
        sync: bool=True,
        auto: bool=True,

        # Internal
        _super:  Self=None,
        _parent: Self=None,
        _name:   str=None,
        **kwargs
    ):

        # Initialize attributes
        self.__path__   = BrokenPath(path)
        self.__disk__   = bool(self.__path__)
        self.__sync__   = sync
        self.__auto__   = auto
        self.__super__  = _super or self
        self.__parent__ = _parent
        self.__name__   = _name
        self.__uuid__   = __next_uuid__()

        # Update data with kwargs and load
        data = (data or {}) | kwargs
        self.from_dict(data)

        # Can any loader load from path?
        if self.__disk__ and not data:
            if (loader := DotmapLoader.smart_find(key=self.__path__)):
                self.from_dict(loader(self.__path__).load())

    # # Internal

    @property
    def __is_super__(self) -> bool:
        return self == self.__super__

    def __recurse__(self, key: str=None, value=None) -> Self:
        log.trace(f"({self.__uuid__:2}) self.__recurse__(data={value}, key={key})")
        if isinstance(value, dict) or value is None:
            log.trace("• Recursing with Self class")
            return type(self)(
                _super  = self.__super__,
                _parent = self,
                _name   = key
            ).from_dict(value)
        return value

    # # Loading and saving as Python dictionary

    def from_dict(self, data: Dict=None) -> Self:
        """Append a dictionary to this instance"""
        log.trace(f"({self.__uuid__:2}) self.from_dict(data={data})")

        # Transform self to a dictionary
        if isinstance(data, type(self)):
            data = data.as_dict

        # Recurse on all values
        for key, value in (data or {}).items():
            self.set(key, self.__recurse__(key=key, value=value))

        return self

    def to_dict(self) -> Dict[str, Any]:
        """Get a dictionary from this instance downwards"""
        log.trace(f"({self.__uuid__:2}) self.to_dict()")
        return {
            k: v.to_dict() if isinstance(v, type(self)) else v
            for k, v in sorted(self.items(), key=lambda x: x[0])
            if not dunder(k)
        }

    @property
    def as_dict(self) -> Dict[str, Any]:
        log.trace(f"({self.__uuid__:2}) self.as_dict")
        return self.to_dict()

    @property
    def dict(self) -> Dict[str, Any]:
        log.trace(f"({self.__uuid__:2}) self.dict")
        return self.to_dict()

    # # Base dictionary methods

    def items(self) -> Dict[str, Any]:
        log.trace(f"({self.__uuid__:2}) self.items()")
        return [(k, v) for k, v in self.__dict__.items() if not dunder(k)]

    def keys(self) -> list:
        log.trace(f"({self.__uuid__:2}) self.keys()")
        return [k for k in self.__dict__.keys() if not dunder(k)]

    def values(self) -> list:
        log.trace(f"({self.__uuid__:2}) self.values()")
        return [v for k, v in self.__dict__.items() if not dunder(k)]

    # # Random dunder

    def __len__(self) -> int:
        return len(self.keys())

    def __iter__(self) -> Iterator:
        return iter(self.keys())

    def delete(self, key: str) -> None:
        # if self.__disk__:
            # (self.disk_path/key).unlink()
        del self.__dict__[key]

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __delattr__(self, key: str) -> None:
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __add__(self, other: Any) -> Self:
        if isinstance(other, dict):
            self.update(other)
            return self

        if isinstance(other, type(self)):
            self.update(other.as_dict)
            return self

        raise TypeError(f"Cannot add {type(other)} to {type(self)}")

    # # Cool utilities

    def update(self, other: Dict[str, Any], **kwargs) -> Self:
        self.__dict__.update((other or dict()) | kwargs)
        return self

    def copy(self):
        return self.from_dict(self.as_dict)

    def pop(self, key: str, default: Any=None) -> Any:
        return self.__dict__.pop(key, default)

    def pretty_print(self, indent: int=4) -> None:
        try:
            from rich import print as rich_print
            rich_print(self.as_dict)
        except ImportError:
            print(json.dumps(self.as_dict, indent=indent, ensure_ascii=False))

    # # Define get methods

    def get(self, key: str) -> Union[Self, Any]:
        """If a key doesn't exist, recurse, else return its the value"""
        log.trace(f"({self.__uuid__:2}) self.get(key={key})")
        return self.__dict__.setdefault(key, self.__recurse__(key=key))

    def __getitem__(self, key: str) -> Union[Self, Any]:
        """Handle dictionary item access using key indexing"""
        log.trace(f"({self.__uuid__:2}) self.__getitem__(key={key})")
        return self.get(key)

    def __getattr__(self, key: str) -> Union[Self, Any]:
        """Handle attribute access using dot notation"""
        log.trace(f"({self.__uuid__:2}) self.__getattr__(key={key})")
        return self.get(key)

    # # Define set methods

    def set(self,
        key: str,
        value: Any=None,
        loader: DotmapLoader=None,
    ) -> Any:
        """Set a key to a value, recurses on the value"""
        log.trace(f"({self.__uuid__:2}) self.set(key={key}, value={value})")

        dot_key = key.replace("_", ".")

        # Directly received a loader
        if loader or not self.__auto__:
            pass

        # Value is a loader
        elif issubclass(type(value), DotmapLoader):
            loader = value

        # Find any loaders that can load the input
        else:
            if (loader := DotmapLoader.smart_find(key=dot_key, value=value)):
                log.trace(f"• Matched Loader: {loader.__name__}")

        # Standard recurse on the value
        if not loader:
            self.__dict__[key] = self.__recurse__(key=key, value=value)
            self.__name__ = key
            self.sync()
            return value

        sync: bool = True

        # Build path if disk, change value to be loaded from it
        if self.__disk__:
            path  = self.disk_path/dot_key
            value = path if path.exists() else value
            log.trace(f"• Using path: {path}")

        # We have a loader class, not a loader instance
        if not isinstance(loader, DotmapLoader):
            value = loader(value).load()

        # We have an instance of a loader
        else:
            if self.__disk__:
                value = loader(path).load()
            else:
                value = loader.load()

        # Replace this instance of Self with the loaded value on parent
        (self.__parent__ or self).__dict__[key] = value
        self.__sync_key__(key=key, value=value)
        return value

    def __setitem__(self, key: str, value: Any) -> Union[Self, Any]:
        """Handle dictionary item assignment using key indexing"""
        log.trace(f"({self.__uuid__:2}) self.__setitem__(key={key}, value={value})")
        return self.set(key=key, value=value)

    def __setattr__(self, key: str, value: Any) -> Union[Self, Any]:
        """Handle attribute assignment using dot notation"""

        # Do not "recurse" on dunder attributes, they are self!
        if dunder(key):
            self.__dict__[key] = value
            return

        log.trace(f"({self.__uuid__:2}) self.__setattr__(key={key}, value={value})")
        return self.set(key=key, value=value)

    def __call__(self, value: Any) -> Union[Self, Any]:
        """Handle calling the instance as a function"""
        log.trace(f"({self.__uuid__:2}) self.__call__(value={value})")
        return self.set(key=self.__name__, value=value)

    # # Syncing

    @contextlib.contextmanager
    def no_sync(self, after: bool=True) -> Self:
        """
        Temporarily disables syncing

        Args:
            after: Whether to sync after the context exits

        Returns:
            Self: Fluent interface
        """
        log.trace(f"({self.__uuid__:2}) self.no_sync()")
        self.__super__.__sync__ = False
        yield self
        self.__super__.__sync__ = after
        self.sync()

    def enable_sync(self) -> None:
        self.__super__.__sync__ = True

    def disable_sync(self) -> None:
        self.__super__.__sync__ = False

    def __sync_key__(self, key: str, value: Any=None) -> Self:
        if not (self.__disk__ and self.__sync__):
            return self

        if (path := self.disk_path/key.replace("_", ".")).exists():
            log.trace(f"• Skipping syncing to path {path} as it exists")
            return self

        # # Can any loader save this key?
        if (loader := DotmapLoader.smart_find(key=path, value=value)):
            log.trace(f"• Matched save nested Loader: {loader.__name__}")
            loader(value).dump(path=BrokenPath.mkdir(path))

    def sync(self) -> Self:
        log.trace(f"({self.__uuid__:2}) self.sync()")

        # Must call sync on the super instance
        if not self.__is_super__:
            return self.__super__.sync()

        # Syncing must be enabled
        if not self.__sync__:
            log.trace("• Syncing disabled")
            return self

        # Do nothing on non-disk mode
        if not self.__disk__:
            return self

        path = self.disk_path
        log.trace(f"• Syncing to disk: {path}")

        # Can any loader save the entirety of self?
        if (loader := DotmapLoader.smart_find(key=path, value=self.as_dict)):
            log.trace(f"• Matched save Loader: {loader.__name__}")
            loader(self.as_dict).dump(path=BrokenPath.mkdir(path))
            return self

        # Else save each key individually, recursively
        def save(path: Path, data: Dict[str, Any]):
            for key, value in data.items():
                if isinstance(value, dict):
                    save(path/key, value)
                    continue
                self.__sync_key__(key, value)

        save(path, self.as_dict)

    # # Utilities

    def default(self, key: str, value: Any) -> Any:
        """Set a default value for a key else don't change, returns it"""
        log.trace(f"({self.__uuid__:2}) self.default(key={key}, value={value})")

        # Return the value if it exists
        if key in self.__dict__:
            return self.__dict__[key]

        # Set the value and sync (call it if callable - a use as a cache)
        return self.set(key, value() if callable(value) else value)

    def setdefault(self, key: str, value: Any) -> Any:
        """Set a default value for a key else don't change, returns it"""
        log.trace(f"({self.__uuid__:2}) self.setdefault(key={key}, value={value})")
        return self.default(key, value)

    def inverse(self, value: Any) -> Any | None:
        """Search by value"""
        log.trace(f"({self.__uuid__:2}) self.inverse(value={value})")
        return next((k for k, v in self.items() if v == value), None)

    # # Disk mode

    @property
    def disk_path(self) -> Path:
        """Get the path to the file on disk"""
        log.trace(f"({self.__uuid__:2}) self.disk_path")

        # The super instance is the one who saves to disk
        if not self.__is_super__:
            return self.__super__.disk_path

        return self.__path__

        # Traverse up the tree to get the path
        components = []

        while self.__name__:
            components.append(self.__name__)
            self = self.__parent__

        # Build the path plus base
        return Path(*reversed(components + [self.__path__]))
