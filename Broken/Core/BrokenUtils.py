from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import (
    Any,
    Self,
)

from attr import Factory, define
from loguru import logger as log

from Broken import flatten


@define
class SameTracker:
    """Doumo same desu"""
    value: Any = None

    def __call__(self, value: Any) -> bool:
        """
        If a value is the same, returns True, else updates it and returns False
        • Useful on ignoring expensive calls where parameters doesn't changes
        """
        if self.value != value:
            self.value = value
            return False
        return True

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
    Walk over an @attrs.defined class and call __post__ on all classes in the MRO.
    # Warn: Must NOT define __attrs_post_init__ in an inheriting class
    # Fixme: Can improve by starting on BrokenAttrs itself
    """
    def __attrs_post_init__(self):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    def __post__(self) -> None:
        pass

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
    A class to bind some callback to many callables.

    Useful for ModernGL window function, eg pseudocode:

    ```python
    window = moderngl_window(...)

    # Create BrokenRelay instance
    scroll_callbacks = BrokenRelay()

    # Map window scroll func callback to this class
    window.mouse_scroll_event_func = scroll_callbacks

    # Define many callbacks that should be called on window resize
    def log_scroll(x, y):
        ...

    camera2d = Camera2D(...)

    # Add callbacks
    scroll_callbacks.bind(log_scroll, camera2d.resize)

    # Or with @ syntax
    scroll_callbacks @ (log_scroll, camera2d.resize)

    # It also returns self when binding
    self.window_mouse_scroll_event_func = scroll_callbacks @ (log_scroll, camera2d.resize)
    ```
    """
    callbacks: list[callable] = Factory(list)

    def __bind__(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        self.callbacks += flatten(callbacks)
        return self

    def bind(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        return self.__bind__(callbacks)

    def subscribe(self, *callbacks: callable) -> Self:
        """Adds callbacks to the list of callables, runs on self.__call__"""
        return self.__bind__(callbacks)

    def __matmul__(self, *callbacks: callable) -> Self:
        """Convenience syntax for binding"""
        return self.__bind__(callbacks)

    def __call__(self, *args, **kwargs):
        """Pass through all callbacks to who called "us" (self)"""
        for callback in self.callbacks:
            callback(*args, **kwargs)
