import datetime
import os
import platform
import shutil
import subprocess
import sys as system
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

import arrow
import distro
import forbiddenfruit
import loguru
import pygit2
import requests
import toml
import typer
from dotmap import DotMap

# ------------------------------------------------------------------------------------------------|

# Distros IDs: https://distro.readthedocs.io/en/latest/
LINUX_DISTRO = distro.id()
HOST_OS = platform.system().lower()

# ------------------------------------------------------------------------------------------------|

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(datetime.timedelta, "milliseconds", property(lambda self: f"{self.microseconds/1000:5.0f}"))

# Set up empty logger
loguru.logger.remove()
logger = loguru.logger.bind()

# Add stdout logging
logger.add(system.stdout, colorize=True, level="TRACE",
    format=f"[<green>{{elapsed.milliseconds}}ms</green>]─[<level>{{level:7}}</level>]<level> ▸ {{message}}</level>")

# self.* functions logging
info     = logger.info
warning  = logger.warning
error    = logger.error
debug    = logger.debug
trace    = logger.trace
success  = logger.success
critical = logger.critical

# ------------------------------------------------------------------------------------------------|

# ['', True, "string", None, "--a"] -> [True, "string", "--a"]
truthyList = lambda stuff: [x for x in stuff if x]

# [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
flatten = lambda stuff: [item for sub in stuff for item in (flatten(sub) if type(sub) in (list, tuple) else [sub])]

# Flatten a list, remove falsy values, convert to strings
__shellify = lambda stuff: truthyList(map(str, flatten(stuff)))

# shell(["binary", "-m"], "arg1", "arg2", 3)
def shell(*a, output=False, echo=True, **k):
    command = __shellify(a)
    if echo: info(f"Running command {command}")
    if output:
        try:
            return subprocess.check_output(__shellify(a), **k).decode("utf-8")
        except subprocess.CalledProcessError as error:
            return error.output.decode("utf-8")
    else:
        subprocess.run(command, **k)

# # Utility functions

def binaryExists(binary) -> bool:
    return shutil.which(binary) is not None

def getBinary(binary) -> Path:
    if not binaryExists(binary):
        raise FileNotFoundError(f"Binary {binary} not found in PATH")
    return Path(shutil.which(binary))

@contextmanager
def download(url) -> Path:
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(requests.get(url).content)
        yield Path(temp.name)

mkdir = lambda path: Path(path).mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------------------------|
