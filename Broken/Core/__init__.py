import contextlib
import copy
import enum
import functools
import hashlib
import inspect
import itertools
import os
import re
import shutil
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable, Collection, Generator, Iterable
from numbers import Number
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Any, Optional, Self, Union

import click
from attrs import Factory, define, field
from dotmap import DotMap
from loguru import logger as log
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    import requests
    import requests_cache


def flatten(
    *items: Any,
    cast: type = list,
    block: Optional[Collection] = (None, ""),
    unpack: Iterable[type] = (list, deque, tuple, map, Generator),
) -> Collection[Any]:
    """
    Flatten/unpack nested iterables (list, deque, tuple, map, Generator) to a plain 1D list
    - Removes common falsy values by default, modify with `block={None, False, "", [], ...}`

    Example:
        ```python
        # [1, 2, 3, 4, 5, 6, 7]
        flatten([1, [2, 3], 4, [5, [6, 7]]])

        # [0, 1, 2, True, False, "Hello"]
        flatten(range(3), (True, False), None, "Hello")
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
    *items: Any,
    cast: type = list,
    block: Collection[Any] = (None, ""),
) -> Optional[Collection]:
    """
    Returns the flattened items if not any element is in the block list, else None. Useful when
    a Model class has a list of optional arguments that doesn't add falsy values to a command

    Usage:
        ```python
        every(1, 2, 3) # [1, 2, 3]
        every(1, 2, 3, None) # None
        every("-arg, "") # None
        ```
    """
    items = flatten(*items, block=None, cast=cast)
    if any(item in block for item in items):
        return None
    return items


def shell(
    *args: Any,
    output: bool = False,
    Popen: bool = False,
    env: dict[str, str] = None,
    confirm: bool = False,
    skip: bool = False,
    echo: bool = True,
    **kwargs
) -> Optional[Union[
    subprocess.CompletedProcess,
    subprocess.Popen,
    str,
]]:
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
    if (not shell) and (not shutil.which(args[0])):
        raise FileNotFoundError(log.error(f"Binary doesn't exist or was not found on PATH ({args[0]})"))

    # Log the command being run, temp variables
    _log = (log.skip if skip else log.info)
    _cwd = f" @ ({kwargs.get('cwd', '') or Path.cwd()})"
    _log(f"{args}{_cwd}", echo=echo)
    if skip: return

    if kwargs.get("shell", False):
        args = ' '.join(args)
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

    if (output):
        return subprocess.check_output(args, **kwargs).decode("utf-8")

    if (Popen):
        return subprocess.Popen(args, **kwargs)

    return subprocess.run(args, **kwargs)


def apply(
    callback: Callable,
    iterable: Iterable, *,
    cast: Callable = list
) -> Collection:
    """Applies a callback to all items of an iterable, returning a $cast of the results"""
    return cast(map(callback, iterable))


def denum(item: Union[enum.Enum, Any]) -> Any:
    """De-enumerates an item: if it's an Enum, returns the value, else the item itself"""
    return (item.value if isinstance(item, enum.Enum) else item)


def pop_fill(data: Collection, fill: type, length: int) -> Collection:
    """Pop or fill until a data's length is met"""
    while (len(data) > length):
        data.pop()
    while (len(data) < length):
        data.append(fill())
    return data


@contextlib.contextmanager
def multi_context(*contexts: contextlib.AbstractContextManager) -> Generator:
    """Enter multiple contexts at once"""
    with contextlib.ExitStack() as stack:
        for context in flatten(contexts):
            stack.enter_context(context)
        yield None


@contextlib.contextmanager
def tempvars(**variables: str) -> Generator:
    """Temporarily sets environment variables inside a context"""
    original = os.environ.copy()
    os.environ.update(variables)
    try:
        log.info(f"Setting environment variables: {tuple(variables.items())}")
        yield None
    finally:
        log.info(f"Restoring environment variables: {tuple(variables.keys())}")
        os.environ.clear()
        os.environ.update(original)


@contextlib.contextmanager
def block_modules(*modules: str) -> Generator:
    """Pretend a module isn't installed"""
    state = sys.modules.copy()
    try:
        for module in flatten(modules):
            sys.modules[module] = None
        yield None
    finally:
        for module in modules:
            if (module in state):
                sys.modules[module] = state[module]
                continue
            del sys.modules[module]


def smartproxy(object: Any) -> Any:
    """Returns a weakref proxy if the object is not already proxied"""
    from weakref import CallableProxyType, ProxyType, proxy

    if not isinstance(object, (CallableProxyType, ProxyType)):
        object = proxy(object)

    return object


def clamp(value: float, low: float=0, high: float=1) -> float:
    return max(low, min(value, high))


def nearest(number: Number, multiple: Number, *, cast=int, operator: Callable=round) -> Number:
    """Finds the nearest multiple of a base number, by default ints but works for floats too"""
    return cast(multiple * operator(number/multiple))


def list_get(data: list, index: int, default: Any=None) -> Optional[Any]:
    """Returns the item at 'index' or 'default' if out of range"""
    if (index >= len(data)):
        return default
    return data[index]


def hyphen_range(string: Optional[str], *, inclusive: bool=True) -> Iterable[int]:
    """
    Yields the numbers in a hyphenated CSV range, just like when selecting what pages to print
    - Accepts any of ("-", "..", "...", "_", "->") as a hyphenated range
    - Special values:
        - "all", returns infinite range from 0
        - "even", returns even numbers
        - "odd", returns odd numbers

    Example:
        ```python
        hyphen_range("2,3") # 2, 3
        hyphen_range("2-5") # 2, 3, 4, 5
        hyphen_range("1-3, 5") # 1, 2, 3, 5
        ```
    """
    if not bool(string):
        return None

    if (string == "all"):
        yield from itertools.count()
    elif (string == "even"):
        yield from itertools.count(0, 2)
    elif (string == "odd"):
        yield from itertools.count(1, 2)

    for part in string.split(","):
        if ("-" in part):
            start, end = map(int, re.split(r"_|-|\.\.|\.\.\.|\-\>", part))
            yield from range(start, end + int(inclusive))
            continue
        yield int(part)


def limited_ratio(
    number: Optional[float], *,
    limit: float = None
) -> Optional[tuple[int, int]]:
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
    old: Any,
    new: Optional[Any],
    default: Optional[Any]=None,
    resets: Any=-1
) -> Optional[Any]:
    """Returns 'new' if is not None, else keeps 'old' value"""
    if (new == resets):
        return default
    if (new is None):
        return old
    return new


def install(*,
    packages: Union[str, Iterable[str]],
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


def combinations(**options: Any) -> Iterable[DotMap]:
    """Returns a dictionary of key='this' of itertools.product"""
    for items in itertools.product(*options.values()):
        yield DotMap(zip(options.keys(), items))


def arguments() -> bool:
    """Returns True if any arguments are present on sys.argv"""
    return bool(sys.argv[1:])


def easyloop(method: Callable=None, *, period: float=0.0):
    """Wraps a method in an infinite loop called every 'period' seconds"""

    def decorator(method):

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            while True:
                method(*args, **kwargs)
                time.sleep(period)

        return wrapper

    if (method is None):
        return decorator

    return decorator(method)

# ------------------------------------------------------------------------------------------------ #
# Classes


class Nothing:
    """No-operation faster than Mock - A class that does nothing"""
    def __nop__(self, *args, **kwargs) -> Self:
        return self
    def __call__(self, *args, **kwargs) -> Self:
        return self
    def __getattr__(self, _) -> Callable:
        return self.__nop__


class StaticClass:
    """A class that can't be instantiated directl, only used for static methods (namespace)"""

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Can't instantiate static class '{cls.__name__}'")


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
        """Returns an updated copy of this instance"""
        return copy.deepcopy(self)(**update)


class BrokenAttrs:
    """
    Walk over an @attrs.defined class and call __post__ on all classes in the MRO
    Warn: Must NOT define __attrs_post_init__ in an inheriting class
    Fixme: Can improve by starting on BrokenAttrs itself
    """
    def __attrs_post_init__(self):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    @abstractmethod
    def __post__(self) -> None:
        ...


class BrokenModel(BaseModel):
    """Pydantic model utilities"""
    model_config = ConfigDict(
        use_attribute_docstrings=True,
    )

    def model_post_init(self, __context):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    def __post__(self) -> None:
        ...

    def __hash__(self) -> int:
        """Deterministic hash heuristic, as hash() is random seeded"""
        return int(hashlib.sha256(self.json(full=True).encode()).hexdigest(), 16)

    # Serialization

    def json(self, full: bool=True) -> str:
        return self.model_dump_json(
            exclude_defaults=(not full),
            exclude_none=False
        )

    def dict(self, full: bool=True) -> dict:
        return self.model_dump(
            exclude_defaults=(not full),
            exclude_none=False
        )

    def schema(self) -> dict:
        return self.model_json_schema()

    # Deserialization

    @classmethod
    def load(cls, data: Union[dict, str]) -> Self:
        if isinstance(data, dict):
            return cls.model_validate(data)
        elif isinstance(data, str):
            return cls.model_validate_json(data)
        elif isinstance(data, cls):
            return data
        raise ValueError(f"Can't load from value of type {type(data)}")

    def update(self, **data: Union[dict, str]) -> Self:
        for (key, value) in data.items():
            setattr(self, key, value)
        return self

    # Dict-like utilities

    def keys(self) -> Iterable[str]:
        yield from self.dict().keys()

    def values(self) -> Iterable[Any]:
        yield from self.dict().values()

    def items(self) -> Iterable[tuple[str, Any]]:
        yield from self.dict().items()

    # Special

    def reset(self) -> None:
        for key, value in self.model_fields.items():
            setattr(self, key, value.default)


class FrozenHash(BaseModel):
    hash: int = Field(0, exclude=True)

    def __hash__(self):
        self.hash = (self.hash or super().__hash__())
        return self.hash


class BrokenAttribute(StaticClass):
    """Recursive implementation for getattr and setattr from strings"""

    @define
    class Parts:
        all: list[str]
        body: list[str]
        last: str

    @classmethod
    def decompose(cls, key: str) -> Parts:
        parts = str(key).replace("-", "_").split(".")

        return cls.Parts(
            all=parts,
            body=parts[:-1],
            last=parts[-1]
        )

    @classmethod
    def get(cls, root: object, key: str) -> Optional[Any]:
        parts = cls.decompose(key)

        for part in parts.all:
            try:
                root = getattr(root, part)
            except AttributeError:
                return None

        return root

    @classmethod
    def set(cls, object: object, attribute: str, value: Any) -> None:
        parts = cls.decompose(attribute)

        for part in parts.body:
            try:
                object = getattr(object, part)
            except AttributeError:
                return None

        setattr(object, parts.last, value)


class StringUtils(StaticClass):

    @classmethod
    def border(cls, string: str, border: str) -> bool:
        """Returns True if 'border' is both a prefix and suffix of 'string'"""
        return (string.startswith(border) and string.endswith(reversed(border)))

    @classmethod
    def dunder(cls, name: str) -> bool:
        """Checks if a string is a double underscore '__name__'"""
        return cls.border(name, "__")

    @classmethod
    def sunder(cls, name: str) -> bool:
        """Checks if a string is a single underscore '_name_'"""
        return (cls.border(name, "_") and not cls.dunder(name))

    @classmethod
    def private(cls, name: str) -> bool:
        """Checks if a string is a private name"""
        return name.startswith("_")


class DictUtils(StaticClass):

    @staticmethod
    def filter_dict(
        data: dict[str, Any], *,
        block: Optional[Collection] = None,
        allow: Optional[Collection] = None,
    ) -> dict[str, Any]:
        """Filters a dictionary by removing 'block' or only allowing 'allow' keys"""
        if block:
            data = {key: value for key, value in data.items() if (key not in block)}
        if allow:
            data = {key: value for key, value in data.items() if (key in allow)}
        return data

    @classmethod
    def ritems(cls, data: dict[str, Any]) -> Iterable[tuple[str, Any]]:
        """Recursively yields all items from a dictionary"""
        for (key, value) in data.items():
            if isinstance(value, dict):
                yield from cls.ritems(value)
                continue
            yield (key, value)

    @classmethod
    def rvalues(cls, data: dict[str, Any]) -> Iterable[Any]:
        """Recursively yields all values from a dictionary"""
        for (key, value) in cls.ritems(data):
            yield value

    @classmethod
    def selfless(cls, data: dict) -> dict:
        """Removes the 'self' key from a dictionary (useful for locals() or __dict__)"""
        # Note: It's also possible to call Class.method(**locals()) instead!
        return cls.filter_dict(data, block=["self"])


class BrokenCache(StaticClass):

    @staticmethod
    @functools.lru_cache
    @functools.wraps(functools.lru_cache)
    def lru(*args, **kwargs) -> Callable:
        """Smarter lru_cache consistent with multi-calls"""
        return functools.lru_cache(*args, **kwargs)

    @staticmethod
    def requests(*args, patch: bool=False, **kwargs):
        import requests
        import requests_cache
        session = requests_cache.CachedSession(*args, **kwargs)
        if patch:
            requests.Session = session
        return session


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
    registry: deque[Callable] = Factory(deque)

    def subscribe(self, *methods: Iterable[Callable]) -> Self:
        """Adds callbacks to be called with same arguments as self.__call__"""
        self.registry.extend(flatten(methods))
        return self

    def __call__(self, *args, **kwargs):
        for callback in self.registry:
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


class BrokenWatchdog(ABC):

    @abstractmethod
    def __changed__(self, key, value) -> None:
        """Called when a property changes"""
        ...

    def __setattr__(self, key, value):
        """Calls __changed__ when a property changes"""
        super().__setattr__(key, value)
        self.__changed__(key, value)


@define
class ThreadedStdin:
    _process: subprocess.Popen
    _queue: Queue = Factory(factory=lambda: Queue(maxsize=10))
    _loop: bool = True

    def __attrs_post_init__(self):
        Thread(target=self.worker, daemon=True).start()
        self._process.stdin = self
    def write(self, data):
        self._queue.put(data)
    def worker(self):
        while self._loop:
            self._process.stdin.write(self._queue.get())
            self._queue.task_done()
    def close(self):
        self._queue.join()
        self._loop = False
        self._process.stdin.close()
        while self._process.poll() is None:
            time.sleep(0.01)


# ------------------------------------------------------------------------------------------------ #
# Stuff that needs a revisit

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
        return f"{type(self).__name__}(name='{self._lzname_}')"

    def __enter__(self):

        @functools.wraps(LazyImport.__import__)
        def laziest(*args):
            module = type(self)(_name=args[0])
            return sys.modules.setdefault(module._lzname_, module)

        # Patch the import function with ours
        __builtins__["__import__"] = laziest

    def __exit__(self, *args):
        __builtins__["__import__"] = LazyImport.__import__
