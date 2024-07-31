from __future__ import annotations

import copy
import functools
import sys
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Any, Callable, Deque, Iterable, Self

from attr import Factory, define, field

from Broken import flatten


@define
class SameTracker:
    """Doumo same desu. If a value is the same, returns True, else updates it and returns False
    • Useful on ignoring expensive calls where parameters doesn't changes"""
    value: Any = None

    def __call__(self, value: Any=True) -> bool:
        if self.value != value:
            self.value = value
            return False
        return True


@define
class OnceTracker:
    """Returns False the first time it's called, never nest style: `if once/already(): return`"""
    _first: bool = False

    def __call__(self) -> bool:
        if not self._first:
            self._first = True
            return False
        return True

    def decorator(method: Callable) -> Callable:
        tracker = OnceTracker()
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            if tracker():
                return
            return method(*args, **kwargs)
        return wrapper


@define
class PlainTracker:
    value: Any = None

    def __call__(self, set: bool=None) -> bool:
        """Returns value if None else sets it"""
        if set is not None:
            self.value = set
        return self.value


class Ignore:
    """A class that does nothing. No-operation faster Mock"""
    def __nop__(self, *args, **kwargs) -> Self:
        return self
    def __call__(self, *args, **kwargs) -> Self:
        return self
    def __getattr__(self, _):
        return self.__nop__


class BrokenAttrs:
    """
    Walk over an @attrs.defined class and call __post__ on all classes in the MRO
    # Warn: Must NOT define __attrs_post_init__ in an inheriting class
    # Fixme: Can improve by starting on BrokenAttrs itself
    """
    def __attrs_post_init__(self):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    @abstractmethod
    def __post__(self) -> None:
        ...


class BrokenWatchdog(ABC):

    @abstractmethod
    def __changed__(self, key, value) -> None:
        """Called when a property changes"""
        ...

    def __setattr__(self, key, value):
        """Calls __changed__ when a property changes"""
        super().__setattr__(key, value)
        self.__changed__(key, value)


class BrokenSingleton(ABC):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super().__new__(cls)
            cls.__singleton__(*args, **kwargs)
        return cls.__instance__

    @abstractmethod
    def __singleton__(self, *args, **kwargs):
        """__init__ but for the singleton"""
        ...


class BrokenFluentBuilder:
    """
    Do you ever feel like using a builder-like fluent syntax for changing attributes of an object?
    """
    def __call__(self, **kwargs) -> Self:
        """Updates the instance with the provided kwargs"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def copy(self, **kwargs) -> Self:
        """Returns a copy of this instance"""
        new = copy.deepcopy(self)
        for key, value in kwargs.items():
            setattr(new, key, value)
        return new


@define
class BrokenRelay:
    """
    A utility class for sharing one-to-many callbacks in a 'observer' pattern style. Multiple
    callabacks can be subscribed to receive the same args and kwargs when an instance of this class
    is called. Useful cases are to avoid inheritance when sharing callbacks.

    Example:
        ```python
        relay = BrokenRelay()

        # Basic usage
        relay.subscribe(callback1, callback2)
        relay(*args, **kwargs) # Calls callback1 and callback2

        # Can also 'inject' us to bound callables
        window = moderngl_window(...)
        window.key_event_func = relay
        window.key_event_func = relay @ (camera.walk, camera.rotate)
        ```
    """
    callbacks: Deque[Callable] = Factory(deque)

    def __bind__(self, *callbacks: Iterable[Callable]) -> Self:
        self.callbacks += flatten(callbacks)
        return self

    def subscribe(self, *callbacks: Iterable[Callable]) -> Self:
        """Adds callbacks to be called with same arguments as self.__call__"""
        return self.__bind__(callbacks)

    def __matmul__(self, *callbacks: Iterable[Callable]) -> Self:
        """Convenience syntax for subscribing with `relay @ (A, B)`"""
        return self.__bind__(callbacks)

    def __call__(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)


class LazyImport:
    __import__ = copy.deepcopy(__import__)

    def __init__(self, _name: str=None):
        self._lzname_ = _name

    def __load__(self) -> Any:
        del sys.modules[self._lzname_]
        module = LazyImport.__import__(self._lzname_)
        sys.modules[self._lzname_] = module

        # Update the caller's globals with the reloaded
        sys._getframe(2).f_globals[self._lzname_] = module

        return module

    def __getattr__(self, name) -> Any:
        return getattr(self.__load__(), name)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self._lzname_}')"

    def __enter__(self):

        @functools.wraps(LazyImport.__import__)
        def laziest(*args):
            module = self.__class__(_name=args[0])
            return sys.modules.setdefault(module._lzname_, module)

        # Patch the import function with ours
        __builtins__["__import__"] = laziest

    def __exit__(self, *args):
        __builtins__["__import__"] = LazyImport.__import__


@define
class Patch:
    file: Path = field(converter=Path)
    replaces: dict[str, str] = field(factory=dict)
    __original__: str = None

    def __attrs_post_init__(self):
        self.__original__ = self.file.read_text("utf-8")

    def apply(self):
        content = self.__original__
        for key, value in self.replaces.items():
            content = content.replace(key, value)
        self.file.write_text(content, "utf-8")

    def revert(self):
        self.file.write_text(self.__original__, "utf-8")

    def __enter__(self):
        self.apply()
    def __exit__(self, *args):
        self.revert()
