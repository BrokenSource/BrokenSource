import datetime
import importlib
import inspect
import os
import platform
import shutil
import subprocess
import sys as system
import tempfile
import zipfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from os import PathLike
from os import environ as env
from os import getcwd as working_directory
from pathlib import Path
from shutil import which as find_binary
from subprocess import Popen, check_output, run
from sys import argv
from threading import Thread
from time import sleep
from uuid import uuid4 as uuid

import arrow
import distro
import forbiddenfruit
import halo
import loguru
import pygit2
import requests
import rich
import toml
import typer
from appdirs import AppDirs
from dotmap import DotMap

# -------------------------------------------------------------------------------------------------|

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(
    datetime.timedelta, "milliseconds",
    property(lambda self: f"{self.microseconds/1000:5.0f}")
)

# Set up empty logger
loguru.logger.remove()
logger = loguru.logger.bind()

# Add stdout logging
logger.add(system.stdout, colorize=True, level="TRACE",
    format=(
        "[<green>{elapsed.milliseconds}ms</green>]─"
        "[<level>{level:7}</level>]"
        "<level> ▸ {message}</level>"
    )
)

# self.* functions logging
info     = logger.info
warning  = logger.warning
error    = logger.error
debug    = logger.debug
trace    = logger.trace
success  = logger.success
critical = logger.critical

# -------------------------------------------------------------------------------------------------|

# Flatten nested lists and tuples to a single list
# [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
flatten = lambda stuff: [
    item for sub in stuff for item in
    (flatten(sub) if type(sub) in (list, tuple) else [sub])
]

# shell(["binary", "-m"], "arg1", "arg2", 3)
def shell(*args, output=False, Popen=False, echo=True, **kwargs):
    if output and Popen:
        raise ValueError("Cannot use output=True and Popen=True at the same time")

    # Flatten a list, remove falsy values, convert to strings
    command = [item for item in map(str, flatten(args)) if item]

    if echo:   info(f"Running command {command}")
    if output: return subprocess.check_output(command, **kwargs).decode("utf-8")
    if Popen:  return subprocess.Popen(command, **kwargs)
    else:      return subprocess.run(command, **kwargs)

# -------------------------------------------------------------------------------------------------|
# # Unix-like Python ported functions

def mkdir(path: PathLike):
    path = Path(path)
    if path.exists(): return
    info(f"Creating directory {path}")
    Path(path).mkdir(parents=True, exist_ok=True)

def cp(source: PathLike, destination: PathLike):
    info(f"Copying [{source}] -> [{destination}]")
    shutil.copy2(source, destination)

# Path may be a file or directory
def rmdir(path: PathLike, confirm=False):
    path = Path(path)
    info(f"Removing Path [{path}] ({confirm=})")

    # Symlinks are safe to remove
    if path.is_symlink():
        info("Path is a symlink, is safe to remove")
        path.unlink()
        return

    # Confirm removal: directory contains data
    if confirm and not rich.prompt.Confirm.ask(f"Confirm removing path ({path})"):
        return

    # Remove directory
    shutil.rmtree(path)

@contextmanager
def pushd(directory):
    """Change directory, then change back when done"""
    cwd = working_directory()
    os.chdir(directory)
    yield directory
    os.chdir(cwd)

# -------------------------------------------------------------------------------------------------|
# # Platoform specific functions

# Distros IDs: https://distro.readthedocs.io/en/latest/
LINUX_DISTRO = distro.id()

class BrokenPlatform:
    Linux   = platform.system().lower() == "linux"
    Windows = platform.system().lower() == "windows"
    MacOS   = platform.system().lower() == "darwin"

def make_project_directories(app_name: str="Broken", app_author: str="BrokenSource") -> DotMap:
    """Make directories for a project, returns a DotMap of directories
    .SHARED, have .CACHE, .CONFIG, .DATA, .EXTERNALS"""
    directories = DotMap()
    directories.ROOT    = Path(AppDirs(app_name, app_author).user_data_dir)
    directories.CACHE     = directories.ROOT/"Cache"
    directories.CONFIG    = directories.ROOT/"Config"
    directories.DATA      = directories.ROOT/"Data"
    directories.EXTERNALS = directories.ROOT/"Externals"
    for directory in directories.values(): mkdir(directory)

# Root of BrokenSource Monorepo
BROKEN_ROOT = Path(__file__).parent.parent.absolute().resolve()
SYSTEM_ROOT = Path("/").absolute().resolve()

# Where Broken shall be placed as a symlink to be shared
# (on other pyproject.toml have it as broken = {path="/Broken", develop=true})
SHARED_BROKEN_DIRECTORY = SYSTEM_ROOT/"Broken"

# Shared directories of Broken package
BROKEN_DIRECTORIES = make_project_directories()

# Constants
USERNAME = env.get("USER") or env.get("USERNAME")
HOME_DIR = Path.home()

# -------------------------------------------------------------------------------------------------|
# # Utility functions

def binary_exists(binary) -> bool:
    return find_binary(binary) is not None

def get_binary(binary) -> Path:
    if not binary_exists(binary):
        raise FileNotFoundError(f"Binary {binary} not found in PATH")
    binary = Path(find_binary(binary))
    info(f"Found binary {binary}")
    return binary

@contextmanager
def download(url) -> Path:
    with tempfile.TemporaryDirectory() as tempdir:
        download_file = Path(tempdir) / Path(url).name
        with halo.Halo(text=f"Downloading {url}", spinner="dots") as spinner:
            with open(download_file, "wb") as file:
                file.write(requests.get(url).content)
            spinner.succeed()
        yield download_file

def make_executable(path) -> None:
    """Make a file executable"""
    if BrokenPlatform.Linux or BrokenPlatform.MacOS:
        info(f"Make Executable [{path}]")
        shell("chmod", "+x", path)

# -------------------------------------------------------------------------------------------------|
