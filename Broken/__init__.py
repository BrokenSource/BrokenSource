import sys as system
from contextlib import contextmanager

# -------------------------------------------------------------------------------------------------|
# Ignore import errors inside BrokenImports context, replace the module with BrokenImportError class
#
# Usage:
# | while True:
# |     with BrokenImports():
# |         import A
# |         import B
# |         import C
# |         break

class BrokenImportError:
    ...

@contextmanager
def BrokenImports():
    try:
        yield
    except (ModuleNotFoundError, ImportError) as error:
        # Module and its spec import error class
        import_error = BrokenImportError()

        # Patch system.modules for no re-importing
        system.modules[error.name]          = import_error

        # "spec is not None" -> make it something, might break stuff
        system.modules[error.name].__spec__ = import_error

        # Make it available on local globals() else name not found
        globals()[error.name]               = import_error

# -------------------------------------------------------------------------------------------------|

while True:
    with BrokenImports():
        import ctypes
        import datetime
        import hashlib
        import importlib
        import inspect
        import os
        import platform
        import random
        import re
        import shutil
        import subprocess
        import tempfile
        import zipfile
        from abc import ABC, abstractmethod
        from contextlib import suppress
        from copy import deepcopy
        from dataclasses import dataclass
        from functools import wraps
        from io import BytesIO
        from math import *
        from os import PathLike
        from os import environ as env
        from os import getcwd as working_directory
        from pathlib import Path
        from shutil import which as find_binary
        from subprocess import PIPE, Popen, check_output, run
        from sys import argv
        from threading import Thread
        from time import sleep
        from time import time as now
        from typing import Any, Dict, Iterable, List, Tuple, Union
        from uuid import uuid4 as uuid

        import arrow
        import distro
        import forbiddenfruit
        import halo
        import loguru
        import moderngl
        import PIL.Image
        import numpy
        import openai
        import PIL
        import pygit2
        import requests
        import requests_cache
        import rich
        import rich.prompt
        import toml
        import transformers
        import typer
        from appdirs import AppDirs
        from dotmap import DotMap
        from numpy import *
        from tqdm import tqdm

        break

# Add milliseconds to timedelta for logging
forbiddenfruit.curse(
    datetime.timedelta, "milliseconds",
    property(lambda self: f"{(self.seconds*1000 + self.microseconds/1000):5.0f}")
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

# Uncolored raw text logging asame format as above
def add_logging_file(path: PathLike):
    logger.add(path, level="TRACE",
        format=(
            "[{time:YYYY-MM-DD HH:mm:ss}]-"
            "[{elapsed.milliseconds}ms]-"
            "[{level:7}]"
            " ▸ {message}"
        )
    )

def _custom_loglevel(name: str, no: int, color: str):
    loguru.logger.level(name, no, color)
    loguru.logger.name = lambda message, **kwargs: logger.log(name, message, **kwargs)
    return loguru.logger.name

# Logging functions
info      = logger.info
warning   = logger.warning
error     = logger.error
debug     = logger.debug
trace     = logger.trace
success   = logger.success
critical  = logger.critical
exception = logger.exception
fixme     = _custom_loglevel("FIXME", 35, "<cyan><bold>")
todo      = _custom_loglevel("TODO",  35, "<blue><bold>")

# -------------------------------------------------------------------------------------------------|

# Flatten nested lists and tuples to a single list
# [[a, b], c, [d, e, None], [g, h]] -> [a, b, c, d, e, None, g, h]
flatten = lambda stuff: [
    item for sub in stuff for item in
    (flatten(sub) if type(sub) in (list, tuple) else [sub])
]

# shell(["binary", "-m"], "arg1", None, "arg2", 3, output=True)
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
# # Unix-like Python "ported" functions

true_path = lambda path: Path(path).expanduser().resolve().absolute()

def mkdir(path: PathLike, echo=True):
    """Creates a directory and its parents, fail safe™"""
    path = Path(path)

    if path.exists():
        if echo: success(f"Path [{path}] already exists")
        return

    if echo: info(f"Creating directory {path}")
    path.mkdir(parents=True, exist_ok=True)

def cp(source: PathLike, destination: PathLike, echo=True):
    source, destination = Path(source), Path(destination)
    if echo: info(f"Copying [{source}] -> [{destination}]")
    shutil.copy2(source, destination)

# Path may be a file or directory
def rmdir(path: PathLike, confirm=False, echo=True):
    path = Path(path)
    if echo: info(f"Removing Path [{path}] ({confirm=})")

    # Symlinks are safe to remove
    if path.is_symlink(): path.unlink(); return

    # Confirm removal: directory contains data
    if confirm and (not rich.prompt.Confirm.ask(f"Confirm removing path ({path})")):
        return

    # Remove the path
    if path.is_dir(): shutil.rmtree(path, ignore_errors=True)
    else:             path.unlink()

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
    # Name of the current platform
    Name    = platform.system()

    # Booleans if the current platform is the following
    Linux   = Name.lower() == "linux"
    Windows = Name.lower() == "windows"
    MacOS   = Name.lower() == "darwin"
    BSD     = Name.lower() == "bsd"

    # Family of platforms
    Unix    = Linux or MacOS or BSD

# -------------------------------------------------------------------------------------------------|
# # Directories

def make_project_directories(app_name: str="Broken", app_author: str="BrokenSource", echo=True) -> DotMap:
    """Make directories for a project, returns a DotMap of directories (.ROOT, .CACHE, .CONFIG, .DATA, .EXTERNALS)"""
    if echo: info(f"Making project directories for [AppName: {app_name}] by [AppAuthor: {app_author}]")
    directories = DotMap()

    # Root of the project directories
    directories.ROOT      = Path(AppDirs(app_name, app_author).user_data_dir)
    directories.CACHE     = directories.ROOT/"Cache"
    directories.CONFIG    = directories.ROOT/"Config"
    directories.DATA      = directories.ROOT/"Data"
    directories.EXTERNALS = directories.ROOT/"Externals"

    # The directory of the file that called this function itself, think of BROKEN_ROOT but for the caller
    directories.EXECUTABLE = Path(inspect.stack()[1].filename).parent.absolute().resolve()

    # If pyinstaller or nuitka is used, respectively, get the original exercutable binary
    # not the ont on the temp directory that got extracted
    if getattr(system, "frozen", False):
        directories.EXECUTABLE = Path(system.executable).parent.absolute().resolve()
    if getattr(__builtins__, "__compiled__", False):
        directories.EXECUTABLE = Path(__builtins__.__compiled__).parent.absolute().resolve()

    # Make all project directories
    for name, directory in directories.items():
        if echo: info(f"• ({name.ljust(9)}): [{directory}]")
        mkdir(directory, echo=False)
    return directories

# Root of BrokenSource Monorepo
BROKEN_ROOT_DIR = Path(__file__).parent.parent.absolute().resolve()
SYSTEM_ROOT_DIR = Path("/").absolute().resolve()

# Where Broken shall be placed as a symlink to be shared
# (on other pyproject.toml have it as broken = {path="/Broken", develop=true})
BROKEN_SHARED_DIR = SYSTEM_ROOT_DIR/"Broken"

# Shared directories of Broken package
BROKEN_DIRECTORIES = make_project_directories(echo=False)

# Constants
USERNAME = env.get("USER") or env.get("USERNAME")
HOME_DIR = Path.home()

# -------------------------------------------------------------------------------------------------|
# # Utility functions

def binary_exists(binary_name: str) -> bool:
    return find_binary(binary_name) is not None

def get_binary(binary_name: Union[str, List[str]], echo=True) -> Path:

    # Recurse if a list of binaries is given (for all)
    if type(binary_name) is list:
        for binary in binary_name:
            binary = get_binary(binary, echo=echo)
            if binary is not None: return binary
        return None

    # Enforce string
    binary_name = str(binary_name)

    # Attempt to find the binary
    if (binary := find_binary(binary_name)) is not None:
        if echo: success(f"Binary [{binary_name.ljust(8)}] is on PATH at [{binary}]")
        return binary
    else:
        if echo: warning(f"Binary [{binary_name.ljust(8)}] it not on PATH")
        return None

# Endless war of how to get a FFmpeg binary available
try:
    import imageio_ffmpeg
    BROKEN_FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    try:
        BROKEN_FFMPEG_BINARY = get_binary("ffmpeg", echo=False)
    except FileNotFoundError:
        BROKEN_FFMPEG_BINARY = None

@contextmanager
def download(url) -> Path:
    with tempfile.TemporaryDirectory() as tempdir:
        download_file = Path(tempdir) / Path(url).name
        with halo.Halo(text=f"Downloading {url}", spinner="dots") as spinner:
            with open(download_file, "wb") as file:
                file.write(requests.get(url).content)
            spinner.succeed()
        yield download_file

def make_executable(path: PathLike) -> None:
    """Make a file executable"""
    path = Path(path)
    if BrokenPlatform.Unix:
        info(f"Make Executable [{path}]")
        shell("chmod", "+x", path)

# -------------------------------------------------------------------------------------------------|
# # Utility classes

class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__singleton__"):
            cls.__singleton__ = super().__new__(cls)
        return cls.__singleton__

# -------------------------------------------------------------------------------------------------|
# # Path utilities

class ShellCraft:

    # Current shell name (binary path)
    SHELL_BINARY = os.environ.get("SHELL", "unknown")

    # Booleans if the current shell is the following
    BASH       = "bash" in SHELL_BINARY
    ZSH        = "zsh"  in SHELL_BINARY
    FISH       = "fish" in SHELL_BINARY
    Unknown    = (not (BASH or ZSH or FISH)) or (SHELL_BINARY == "unknown")

    def add_path_to_system_PATH(path: PathLike, echo=True) -> bool:
        """Add a path to the system PATH _ideally_ for all platforms. Sincerely, f-pointer-comment-at this function"""
        path = Path(path)

        # If the path is already in the system path, no work to do
        if str(path) in os.environ.get("PATH", "").split(os.pathsep):
            if echo: success(f"Path [{path}] already in PATH")
            return True

        # Unix is complicated, ideally one would put on /etc/profile but it's only reloaded on logins
        # The user shell varies a lot, but most are in BASH, ZSH or FISH apparently, but need sourcing or restarting
        if BrokenPlatform.Unix:

            # The export line adding to PATH the wanted path
            export = f"export PATH={path}:$PATH"

            # Add the export line based on the current shell
            for current_shell, shellrc in [
                (ShellCraft.BASH,    HOME_DIR/".bashrc"                 ),
                (ShellCraft.ZSH,     HOME_DIR/".zshrc"                  ),
                (ShellCraft.FISH,    HOME_DIR/".config/fish/config.fish"),
                (ShellCraft.Unknown, HOME_DIR/".profile")
            ]:
                # Skip if not on this chell
                if not current_shell: continue

                # Info on what's going on
                if echo and ShellCraft.Unknown: error(f"Your shell is unknown and PATH will be re-exported in [{shellrc}], you need to log out and log in for changes to take effect, go touch some grass..   (PRs are welcome!)")
                if echo: info(f"Your current shell is [{ShellCraft.SHELL_BINARY}], adding the directory [{path}] to PATH in the shell rc file [{shellrc}] as [{export}]")

                # Add the export line to the shell rc file
                with open(shellrc, "a") as file:
                    file.write(f"{export}\n")

            # Need to restart the shell or source it
            warning(f"Please restart your shell for the changes to take effect or run [source {shellrc}] or [. {shellrc}] on current one, this must be done since a children process (Python) can't change the parent process (your shell) environment variables plus the [source] or [.] not binaries but shell builtins")

        # No clue if this works.
        elif BrokenPlatform.Windows:
            fixme("I don't know if the following reg command works for adding a PATH to PATH on Windows")
            shell("reg", "add", r"HKCU\Environment", "/v", "PATH", "/t", "REG_SZ", "/d", f"{path};%PATH%", "/f")
            shell("refreshenv")

        else:
            error(f"Unknown Platform [{BrokenPlatform.Name}]")
            return False

        return True

