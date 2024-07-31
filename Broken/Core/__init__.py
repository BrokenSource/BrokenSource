import contextlib
import enum
import hashlib
import inspect
import os
import re
import shutil
import subprocess
import time
import uuid
from collections import deque
from numbers import Number
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

import click
from attrs import Factory, define
from loguru import logger as log


def flatten(*stuff: Union[Any, Iterable[Any]], truthy: bool=True) -> List[Any]:
    """Flatten nested iterables (list, deque, tuple, Generator) to a 1D list"""
    iterables = (list, deque, tuple, map, Generator)
    def flatten(stuff):
        if truthy:
            stuff = [item for item in stuff if (item is not None) and (item != "")]
        return [
            item for subitem in stuff for item in
            (flatten(subitem) if isinstance(subitem, iterables) else [subitem])
        ]
    return flatten(stuff)

def every(*stuff: Union[Any, Iterable[Any]], ban: List[Any]=[None, ""]) -> Optional[List[Any]]:
    """Returns the flattened args if all elements are truthy (not None or '')"""
    stuff = flatten(stuff, truthy=False)
    if any(item in ban for item in stuff):
        return None
    return stuff

def shell(
    *args:   list[Any],
    output:  bool=False,
    Popen:   bool=False,
    shell:   bool=False,
    env:     dict[str, str]=None,
    echo:    bool=True,
    confirm: bool=False,
    wrapper: bool=False,
    do:      bool=True,
    **kwargs
) -> Union[None, str, subprocess.Popen, subprocess.CompletedProcess]:
    """
    Better subprocess.* commands, all in one, yeet whatever you think it works
    - This is arguably the most important function in the library 🙈

    Example:
        ```python
        shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True, echo=False, confirm=True)
        ```

    Args:
        args:    The command to run, can be a list of arguments or a list of lists of arguments, don't care
        output:  Return the process's stdout as a decoded string
        Popen:   Run the process with subprocess.Popen
        shell:   (discouraged) Run the command with shell=True, occasionally useful
        echo:    Log the command being run or not
        confirm: Ask for confirmation before running the command or not
        wrapper: Enables threaded stdin writing speed workaround (Unix only)
        do:      Inverse of `skip`, do not run the command, but log it as minor

    Kwargs (subprocess.* arguments):
        cwd: Current working directory for the command
        env: Environment variables for the command
        *:   Any other keyword arguments are passed to subprocess.*
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
    if output:
        return subprocess.check_output(command, **kwargs).decode("utf-8")

    elif Popen:
        process = subprocess.Popen(command, **kwargs)

        # Linux non-threaded pipes were slower than Windows plain subprocess
        if (os.name != "nt") and ("stdin" in kwargs) and bool(wrapper):

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
        return subprocess.run(command, **kwargs)

def clamp(value: float, low: float=0, high: float=1) -> float:
    return max(low, min(value, high))

def apply(callback: Callable, iterable: Iterable[Any]) -> List[Any]:
    """map(f, x) is lazy, this consumes the generator, returning a list"""
    return list(map(callback, iterable))

def denum(item: Union[enum.Enum, Any]) -> Any:
    """De-enumerates an item: Returns the item's value if Enum else the item itself"""
    return (item.value if isinstance(item, enum.Enum) else item)

def pydantic_cli(instance: object, post: Callable=None):
    """Makes a Pydantic BaseModel class signature Typer compatible, by copying the class's signature
    to a wrapper virtual function. All kwargs sent are set as attributes on the instance, and typer
    will send all default ones overriden by the user commands. The 'post' method is called afterwards,
    for example `post = self.set_object` for back-communication between the caller and the instance"""
    def wrapper(**kwargs):
        for name, value in kwargs.items():
            setattr(instance, name, value)
        if post: post(instance)
    wrapper.__signature__ = inspect.signature(instance.__class__)
    wrapper.__doc__ = instance.__doc__
    return wrapper

def nearest(number: Number, multiple: Number, *, type=int, operator: Callable=round) -> Number:
    """Finds the nearest multiple of a base number"""
    return type(multiple * operator(number/multiple))

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
            start, end = map(int, re.split(r"-|\.\.|\.\.\.", part))
            yield from range(start, end + int(inclusive))
        else:
            yield int(part)

def image_hash(image) -> str:
    """A Fast-ish method to get an object's hash that implements .tobytes()"""
    return str(uuid.UUID(hashlib.sha256(image.tobytes()).hexdigest()[::2]))

def limited_integer_ratio(number: Optional[float], *, limit: float=None) -> Optional[Tuple[int, int]]:
    """Same as Number.as_integer_ratio but with an optional upper limit and optional return"""
    if number is None:
        return None

    num, den = number.as_integer_ratio()

    if limit and (den > limit or num > limit):
        normalize = limit/min(num, den)
        num, den = int(num * normalize), int(den * normalize)

    return num, den

@contextlib.contextmanager
def temp_env(**env: Dict[str, str]) -> Generator[None, None, None]:
    """Temporarily sets environment variables"""
    old = os.environ.copy()
    os.environ.clear()
    os.environ.update({k: str(v) for k, v in (old | env).items() if v})
    yield
    os.environ.clear()
    os.environ.update(old)

@contextlib.contextmanager
def Stack(*contexts: contextlib.AbstractContextManager) -> Generator[None, None, None]:
    """Enter multiple contexts at once"""
    with contextlib.ExitStack() as stack:
        for context in flatten(contexts):
            stack.enter_context(context)
        yield

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
