from __future__ import annotations

import contextlib
import copy
import enum
import functools
import hashlib
import inspect
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from abc import ABC, abstractmethod
from collections import deque
from numbers import Number
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import (
    Any,
    Callable,
    Container,
    Deque,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Self,
    Tuple,
    Type,
    Union,
)

import click
from attrs import Factory, define, field
from loguru import logger as log
from pydantic import BaseModel


def flatten(
    *items: Iterable[Any],
    cast: Type = list,
    block: Optional[Container[Any]] = (None, ""),
    unpack: Iterable[type] = (list, deque, tuple, map, Generator),
) -> Iterable[Any]:
    """
    Flatten/unpack nested iterables (list, deque, tuple, map, Generator) to a plain 1D list
    - Removes common falsy values by default, disable with `block={None, False, "", [], ...}`

    Usage:
        ```python
        flatten([1, [2, 3], 4, [5, [6, 7]]]) # [1, 2, 3, 4, 5, 6, 7]
        flatten(range(3), (True, False), None, "Hello") # [0, 1, 2, True, False, "Hello"]
        ```

    Returns:
        `cast`ed object with all `unpack`ed `items` without any of the `block`ed values
    """
    def flatten(data):
        if bool(block):
            data = filter(lambda item: (item not in block), data)
        for item in data:
            if isinstance(item, unpack):
                yield from flatten(item)
                continue
            yield item
    return cast(flatten(items))

def every(
    *items: Iterable[Any],
    cast: Type = list,
    block: Container[Any] = (None, ""),
) -> Optional[Iterable[Any]]:
    """
    Returns the flattened items if not any element is in the block list, else None. Useful when
    a Model class has a list of optional arguments that doesn't add falsy values to a command

    Usage:
        ```python
        valid(1, 2, 3) # [1, 2, 3]
        valid(1, 2, 3, None) # None
        valid("-arg, "") # None
        ```
    """
    items = flatten(*items, block=None, cast=cast)
    if any(item in block for item in items):
        return None
    return items

def shell(
    *args: Iterable[Any],
    output: bool = False,
    Popen: bool = False,
    env: Dict[str, str] = None,
    confirm: bool = False,
    threaded_stdin: bool = False,
    skip: bool = False,
    echo: bool = True,
    **kwargs
) -> Union[None, str, subprocess.Popen, subprocess.CompletedProcess]:
    """
    Enhanced subprocess runners with many additional features. Flattens the args, converts to str

    Example:
        ```python
        shell(["binary", "-m"], "arg1", None, "arg2", 3, confirm=True)
        ```
    """
    if (output and Popen):
        raise ValueError(log.error("Cannot use (output=True) and (Popen=True) at the same time"))

    args = tuple(map(str, flatten(args)))

    # Assert command won't fail due unknown binary
    if (not shutil.which(args[0])):
        raise FileNotFoundError(log.error(f"Binary doesn't exist or was not found on PATH ({args[0]})"))

    # Log the command being run, temp variables
    _cwd = f" @ ({kwargs.get('cwd', '') or Path.cwd()})"
    _log = (log.skip if skip else log.info)
    _the = ("Skipping" if skip else "Running")
    _log(_the + f" command {args}{_cwd}", echo=echo)
    if skip: return

    if kwargs.get("shell", False):
        args = '"' + '" "'.join(args) + '"'
        log.warning((
            "Running command with (shell=True), be careful.. "
            "Consider using (confirm=True)"*(not confirm)
        ))

    if confirm and not click.confirm("• Confirm running the command above"):
        return

    # Update current environ for the command only
    kwargs["env"] = os.environ | (env or {})

    # Windows: preexec_fn is not supported, remove from kwargs
    if (os.name == "nt") and (kwargs.pop("preexec_fn", None)):
        log.minor("shell(preexec_fn=...) is not supported on Windows, ignoring..")

    if output:
        return subprocess.check_output(args, **kwargs).decode("utf-8")

    elif Popen:
        process = subprocess.Popen(args, **kwargs)

        if bool(threaded_stdin):

            @define
            class StdinWrapper:
                _process: subprocess.Popen
                _queue: Queue = Factory(factory=lambda: Queue(maxsize=10))
                _loop: bool = True
                _stdin: Any = None

                def __attrs_post_init__(self):
                    Thread(target=self.worker, daemon=True).start()
                def write(self, data):
                    self._queue.put(data)
                def worker(self):
                    while self._loop:
                        self._stdin.write(self._queue.get())
                        self._queue.task_done()
                def close(self):
                    self._queue.join()
                    self._stdin.close()
                    self._loop = False
                    while self._process.poll() is None:
                        time.sleep(0.01)

            process.stdin = StdinWrapper(process=process, stdin=process.stdin)
        return process
    else:
        return subprocess.run(args, **kwargs)

def apply(callback: Callable, iterable: Iterable[Any], *, cast: Callable=list) -> List[Any]:
    """Applies a callback to all items of an iterable, returning a $cast of the results"""
    return cast(map(callback, iterable))

def denum(item: Union[enum.Enum, Any]) -> Any:
    """De-enumerates an item: if it's an Enum, returns the value, else the item itself"""
    return (item.value if isinstance(item, enum.Enum) else item)

def filter_dict(
    data: Dict[str, Any], *,
    block: Optional[Container[Any]] = None,
    allow: Optional[Container[Any]] = None,
) -> Dict[str, Any]:
    """Filters a dictionary by removing 'block' or only allowing 'allow' keys"""
    if block:
        data = {key: value for key, value in data.items() if (key not in block)}
    if allow:
        data = {key: value for key, value in data.items() if (key in allow)}
    return data

def iter_dict(data: Dict[str, Any]) -> Generator[Any, None, None]:
    """Recursively yields all values from a dictionary"""
    for value in data.values():
        if isinstance(value, dict):
            yield from iter_dict(value)
            continue
        yield value

def selfless(data: Dict) -> Dict:
    """Removes the 'self' key from a dictionary (useful for locals() or __dict__)"""
    # Note: It's also possible to call Class.method(**locals()) instead!
    return filter_dict(data, block=["self"])

def border(name: str, substring: str) -> bool:
    """Returns True if 'substring' is the border [^1] of 'name'

    [^1]: https://en.wikipedia.org/wiki/Substring#Border
    """
    return (name.startswith(substring) and name.endswith(reversed(substring)))

def dunder(name: str) -> bool:
    """Checks if a string is a double underscore '__name__'"""
    return border(name, "__")

def sunder(name: str) -> bool:
    """Checks if a string is a single underscore '_name_'"""
    return (border(name, "_") and not dunder(name))

def private(name: str) -> bool:
    """Checks if a string is a private name"""
    return name.startswith("_")

@contextlib.contextmanager
def Stack(*contexts: contextlib.AbstractContextManager) -> Generator[None, None, None]:
    """Enter multiple contexts at once as `with Stack(open() as f1, open() as f2): ...`"""
    with contextlib.ExitStack() as stack:
        for context in flatten(contexts):
            stack.enter_context(context)
        yield

@contextlib.contextmanager
def temp_env(**env: Dict[str, str]) -> Generator[None, None, None]:
    """Temporarily sets environment variables inside a context"""
    old = os.environ.copy()
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)

def pydantic2typer(instance: object, post: Callable=None) -> Callable:
    """Makes a Pydantic BaseModel class signature Typer compatible, by copying the class's signature
    to a wrapper virtual function. All kwargs sent are set as attributes on the instance, and typer
    will send all default ones overriden by the user commands. The 'post' method is called afterwards,
    for example `post = self.set_object` for back-communication between the caller and the instance"""
    import typer
    from pydantic import BaseModel

    if not issubclass(this := type(instance), BaseModel):
        raise TypeError(f"Object {this} is not a Pydantic BaseModel")

    def wrapper(**kwargs):
        for name, value in kwargs.items():
            setattr(instance, name, value)
        if post: post(instance)

    wrapper.__signature__ = inspect.signature(instance.__class__)
    wrapper.__doc__ = instance.__doc__

    # Inject docstring into typer.Option's help
    for value in instance.model_fields.values():
        for metadata in value.metadata:
            if isinstance(metadata, type(typer.Option())):
                metadata.help = (metadata.help or value.description)

    return wrapper

def clamp(value: float, low: float=0, high: float=1) -> float:
    return max(low, min(value, high))

def nearest(number: Number, multiple: Number, *, cast=int, operator: Callable=round) -> Number:
    """Finds the nearest multiple of a base number, by default ints but works for floats too"""
    return cast(multiple * operator(number/multiple))

def hyphen_range(string: Optional[str], *, inclusive: bool=True) -> Generator[int, None, None]:
    """
    Yields the numbers in a hyphenated CSV range, just like when selecting what pages to print
    - Accepts any of ("-", "..", "...", "_", "->") as a hyphenated range

    Example:
        ```python
        hyphen_range("2,3") # 2, 3
        hyphen_range("2-5") # 2, 3, 4, 5
        hyphen_range("1-3, 5") # 1, 2, 3, 5
        ```
    """
    if not bool(string):
        return None

    for part in string.split(","):
        if ("-" in part):
            start, end = map(int, re.split(r"_|-|\.\.|\.\.\.|\-\>", part))
            yield from range(start, end + int(inclusive))
            continue
        yield int(part)

def limited_ratio(
    number: Optional[float], *,
    limit: float = None
) -> Optional[Tuple[int, int]]:
    """Same as Number.as_integer_ratio but with an optional upper limit and optional return"""
    if (number is None):
        return None

    num, den = number.as_integer_ratio()

    if limit and (den > limit or num > limit):
        normalize = limit/min(num, den)
        num *= normalize
        den *= normalize

    return (int(num), int(den))

def overrides(
    old: Optional[Any],
    new: Optional[Any],
) -> Optional[Any]:
    """Returns 'new' if is not None, else keeps 'old' value"""
    if (new is None):
        return old
    return new

def install(
    *packages: Union[str, Iterable[str]],
    pypi: Optional[Union[str, Iterable[str]]]=None,
    args: Optional[Union[str, Iterable[str]]]=None
) -> None:
    # Ensure arguments are tuples
    packages = flatten(packages, cast=tuple)
    pypi = flatten(pypi or packages, cast=tuple)
    args = flatten(args, cast=tuple)

    caller = inspect.currentframe().f_back.f_globals

    # Import the package and insert on the caller's globals
    def inject_packages():
        for package in packages:
            caller[package] = __import__(package)

    try:
        return inject_packages()
    except ImportError:
        log.info(f"Installing packages: {packages}..")

    for method in (
        (sys.executable, "-m", "uv", "pip", "install"),
        (sys.executable, "-m", "pip", "install")
    ):
        if shell(*method, *pypi, *args).returncode == 0:
            return inject_packages()

    raise RuntimeError(log.error(f"Failed to install packages: {packages}"))

# ------------------------------------------------------------------------------------------------ #
# Classes

# # Common, useful

class Nothing:
    """No-operation faster than Mock - A class that does nothing"""
    def __nop__(self, *args, **kwargs) -> Self:
        return self
    def __call__(self, *args, **kwargs) -> Self:
        return self
    def __getattr__(self, _):
        return self.__nop__

class BrokenSingleton(ABC):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance__"):
            self = super().__new__(cls)
            cls.__instance__ = self
        return cls.__instance__

class BrokenFluent:
    """Fluent-like .copy(**update) and .(**update) setter for classes"""

    def __call__(self, **update) -> Self:
        """Updates the instance with the provided kwargs"""
        for key, value in update.items():
            setattr(self, key, value)
        return self

    def copy(self, **update) -> Self:
        """Returns a copy of this instance"""
        other = copy.deepcopy(self)
        for key, value in update.items():
            setattr(other, key, value)
        return other

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

class SerdeBaseModel(BaseModel):
    def serialize(self, json: bool=True) -> Union[dict, str]:
        if json: return self.model_dump_json()
        return self.model_dump()

    @classmethod
    def deserialize(cls, value: Union[dict, str]) -> Self:
        if isinstance(value, dict):
            return cls.model_validate(value)
        elif isinstance(value, str):
            return cls.model_validate_json(value)
        else:
            raise ValueError(f"Can't deserialize value of type {type(value)}")

# # Trackers

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

# # Specific, special

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
        self.callbacks.extend(flatten(callbacks))
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

@define
class Patch:
    file: Path = field(converter=Path)
    replaces: dict[str, str] = field(factory=dict)
    _original: str = None

    def __attrs_post_init__(self):
        self._original = self.file.read_text("utf-8")

    def apply(self):
        content = self._original
        for key, value in self.replaces.items():
            content = content.replace(key, value)
        self.file.write_text(content, "utf-8")

    def revert(self):
        self.file.write_text(self._original, "utf-8")

    def __enter__(self):
        self.apply()
    def __exit__(self, *args):
        self.revert()

# ------------------------------------------------------------------------------------------------ #
# Stuff that needs a revisit

def image_hash(image) -> str:
    """A Fast-ish method to get an object's hash that implements .tobytes()"""
    return str(uuid.UUID(hashlib.sha256(image.tobytes()).hexdigest()[::2]))

def transcends(method, base, generator: bool=False):
    """
    Are you tired of managing and calling super().<name>(*args, **kwargs) in your methods?
    > We have just the right solution for you!

    Introducing transcends, the decorator that crosses your class's MRO and calls the method
    with the same name as the one you are decorating. It's an automatic super() everywhere!
    """
    name = method.__name__

    def decorator(func: Callable) -> Callable:
        def get_targets(self):
            for cls in type(self).mro()[:-2]:
                if cls in (base, object):
                    continue
                if (target := cls.__dict__.get(name)):
                    yield target

        # Note: We can't have a `if generator` else the func becomes a Generator
        def yields(self, *args, **kwargs):
            for target in get_targets(self):
                yield from target(self, *args, **kwargs)
        def plain(self, *args, **kwargs):
            for target in get_targets(self):
                target(self, *args, **kwargs)

        return (yields if generator else plain)
    return decorator

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

