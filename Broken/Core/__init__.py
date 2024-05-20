import enum
import hashlib
import inspect
import os
import re
import shutil
import subprocess
import sys
import time
import types
import uuid
from numbers import Number
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    List,
    Optional,
    Union,
)

import click
from loguru import logger as log


def precise_sleep(seconds: float, *, error: float=1e-3) -> None:
    """
    Sleep for a precise amount of time. This function is very interesting for some reasons:
    - time.sleep() obviously uses syscalls, and it's up to the OS to implement it
    - This is usually done by scheduling the thread to wake up after the time has passed
    - On Windows, this precision was 15ms (terrible), and on Python 3.11+ was optimized to 100ns
    - On Unix, the precision is great with nanosleep() or usleep() (1ms or less)

    So, in practice, the best ever precision time sleep function would be:
    ```python
    while (now - start) < wait:
        now = time.perf_counter()
    ```

    As evident, this spins the thread full time due the .perf_counter() and conditional, which
    is not wanted on a sleep function (to use 100% of a thread)

    Taking advantage of the fact that time.sleep() is usually precise enough, and always will
    overshoot the time, we can sleep close to the time and apply the previous spinning method
    to achieve a very precise sleep, with a low enough overhead, relatively speaking.

    Args:
        seconds: Precise time to sleep

    Returns:
        None
    """
    if seconds < 0:
        return

    # Sleep close to the due time
    start = time.perf_counter()
    ahead = max(0, seconds - error)
    time.sleep(ahead)

    # Spin the thread until the time is up (precise Sleep)
    while (time.perf_counter() - start) < seconds:
        pass

# Count time since.. the big bang with the bang counter. Shebang #!
# Serious note, a Decoupled client starts at the Python's time origin, others on OS perf counter
BIG_BANG: float = time.perf_counter()
time.bang_counter = (lambda: time.perf_counter() - BIG_BANG)
time.precise_sleep = precise_sleep

def flatten(*stuff: Union[Any, List[Any]], truthy: bool=True) -> List[Any]:
    """Flatten nested iterables (list, tuple, Generator) to a 1D list
    - [[a, b], c, [d, e, (None, 3)], [g, h]] -> [a, b, c, d, e, None, 3, g, h]
    - [(x for x in "abc"), "def"] -> ["a", "b", "c", "def"]
    - range(3) -> [0, 1, 2]
    """
    # Fixme: Add allow_none argument
    iterables = (list, tuple, Generator)
    def flatten(stuff):
        return [
            item for subitem in stuff for item in
            (flatten(subitem) if isinstance(subitem, iterables) else [subitem])
            if (not truthy) or (truthy and item)
        ]
    return flatten(stuff)

def shell(
    *args:   list[Any],
    output:  bool=False,
    Popen:   bool=False,
    shell:   bool=False,
    env:     dict[str, str]=None,
    echo:    bool=True,
    confirm: bool=False,
    do:      bool=True,
    **kwargs
) -> Union[None, str, subprocess.Popen, subprocess.CompletedProcess]:
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works
    • This is arguably the most important function in Broken 🙈

    Example:
        ```python
        shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
        ```

    Args:
        `args`:    The command to run, can be a list of arguments or a list of lists of arguments, don't care
        `output`:  Return the process's stdout as a decoded string
        `Popen`:   Run the process with subprocess.Popen
        `shell`:   (discouraged) Run the command with shell=True, occasionally useful
        `echo`:    Log the command being run or not
        `confirm`: Ask for confirmation before running the command or not
        `do`:      Inverse of `skip`, do not run the command, but log it as minor

    Kwargs (subprocess.* arguments):
        `cwd`: Current working directory for the command
        `env`: Environment variables for the command
        `*`:   Any other keyword arguments are passed to subprocess.*
    """
    if output and Popen:
        raise ValueError(log.error("Cannot use (output=True) and (Popen=True) at the same time"))

    # Flatten a list, remove falsy values, convert to strings
    command = tuple(map(str, flatten(args)))

    if shell:
        log.warning("Running command with (shell=True), be careful.." + " Consider using (confirm=True)"*(not confirm))
        command = '"' + '" "'.join(command) + '"'

    # Assert command won't fail due unknown binary
    if (not shell) and (not shutil.which(command[0])):
        raise FileNotFoundError(log.error(f"Binary doesn't exist or was not found on PATH ({command[0]})"))

    # Get the current working directory
    cwd = f" @ ({kwargs.get('cwd', '') or Path.cwd()})"
    (log.info if do else log.skip)(("Running" if do else "Skipping") + f" Command {command}{cwd}", echo=echo)
    if (not do): return

    # Confirm running command or not
    if confirm and not click.confirm("• Confirm running the command above"):
        return

    # Update kwargs on the fly
    kwargs["env"] = os.environ | (env or {})
    kwargs["shell"] = shell

    # preexec_fn is not supported on windows, pop from kwargs
    if (os.name == "nt") and (kwargs.pop("preexec_fn", None)):
        log.minor("preexec_fn is not supported on Windows, ignoring..")

    # Run the command and return specified object
    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

def clamp(value: float, low: float=0, high: float=1) -> float:
    return max(low, min(value, high))

def apply(callback: Callable, iterable: Iterable[Any]) -> List[Any]:
    """map(f, x) is lazy, this consumes the generator, returning a list"""
    return list(map(callback, iterable))

def denum(item: Union[enum.Enum, Any]) -> Any:
    """De-enumerates an item: Returns the item's value if Enum else the item itself"""
    return (item.value if isinstance(item, enum.Enum) else item)

def dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")

def hyphen_range(string: Optional[str], *, inclusive: bool=True) -> Generator[int, None, None]:
    """
    Yields the numbers in a hyphenated CSV range, just like when selecting what pages to print
    - Accepts "-", "..", "...", or a hyphenated range

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
            start, end = map(int, re.split("-|\.\.|\.\.\.", part))
            yield from range(start, end + int(inclusive))
        else:
            yield int(part)

def image_hash(image) -> str:
    """A Fast-ish method to get an object's hash that implements .tobytes()"""
    return str(uuid.UUID(hashlib.sha256(image.tobytes()).hexdigest()[::2]))

def nearest(number: Number, multiple: Number, *, type=int, operator: Callable=round) -> Number:
    """Finds the nearest multiple of a base number"""
    return type(multiple * operator(number/multiple))

def have_import(module: str, *, load: bool=False) -> bool:
    if load:
        try:
            __import__(module)
            return True
        except ImportError:
            return False
    return sys.modules.get(module, False)

# -------------------------------------------------------------------------------------------------|

def transcends(method, base, generator: bool=False):
    """
    Are you tired of managing and calling super().<name>(*args, **kwargs) in your methods?
    > We have just the right solution for you!

    Introducing transcends, the decorator that crosses your class's MRO and calls the method
    with the same name as the one you are decorating. It's an automatic super() !
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

def last_locals(level: int=1, self: bool=True) -> dict:
    locals = inspect.currentframe()

    # Keep getting the previous's frame
    for _ in range(level):
        locals = locals.f_back

    # Get the locals
    locals = locals.f_locals

    # Remove self from locals
    if self:
        locals.pop("self", None)

    return locals

def extend(base: type, name: str=None, as_property: bool=False) -> type:
    """
    Extend a class with another class's methods or a method directly.

    # Usage:
    Decorator of the class or method, class to extend as argument

    @BrokenUtils.extend(BaseClass)
    class ExtendedClass:
        def method(self):
            ...

    @BrokenUtils.extend(BaseClass)
    def method(self):
        ...

    @BrokenUtils.extend(BaseClass, as_property=True)
    def method(self):
        ...
    """
    def extender(add: type):

        # Extend as property
        if as_property:
            return extend(base, name=name, as_property=False)(property(add))

        # If add is a method
        if isinstance(add, types.FunctionType):
            setattr(base, name or add.__name__, add)
            return base

        # If it's a property
        if isinstance(add, property):
            setattr(base, name or add.fget.__name__, add)
            return base

        # If add is a class, add its methods to base
        for key, value in add.__dict__.items():
            if key.startswith("__"):
                continue
            setattr(base, key, value)
            return base

    return extender
