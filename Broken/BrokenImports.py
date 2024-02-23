import os
from contextlib import contextmanager

from . import *

# Numpy's blas broken multiprocessing on matmul
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
os.environ["OMP_NUM_THREADS"] = "1"

# Patch torch.jit requiring inspect.getsource
# https://github.com/pytorch/vision/issues/1899#issuecomment-598200938
if BROKEN_PYINSTALLER:
    try:
        import torch.jit
        patch = lambda object, **kwargs: object
        torch.jit.script_method = patch
        torch.jit.script = patch
    except (ModuleNotFoundError, ImportError):
        pass

    import pyi_splash  # type: ignore
    pyi_splash.close()

# -------------------------------------------------------------------------------------------------|

class BrokenImportError:
    LAST_ERROR = None
    ...

@contextmanager
def BrokenImports():
    """
    Ignore import errors inside a context;
    replaces the module with a BrokenImportError class

    Usage:
        ```python
        while True:
            with BrokenImports():
                import A
                import B
                import DNE
                import C
                break

        # A = <module 'A' from '...'>
        # B = <module 'B' from '...'>
        # C = <module 'C' from '...'>
        # DNE = <class 'Broken.BrokenImportError'>
        ```
    """
    try:
        yield

    except (ModuleNotFoundError, ImportError) as error:
        if BrokenImportError.LAST_ERROR == str(error):
            raise error
        BrokenImportError.LAST_ERROR = str(error)

        # Inject a fake module on the import error
        import_error = BrokenImportError()
        sys.modules[error.name] = import_error
        sys.modules[error.name].__spec__ = import_error
        globals()[error.name] = import_error

    except Exception as error:
        raise error

# -------------------------------------------------------------------------------------------------|

# Tip: To debug import times, use:
# • PYTHONPROFILEIMPORTTIME=1 broken 2> import_times.txt && tuna import_times.txt

# Standard imports
import ast
import collections
import contextlib
import copy
import ctypes
import datetime
import enum
import functools
import hashlib
import importlib
import inspect
import io
import itertools
import json
import math
import multiprocessing
import operator
import os
import pickle
import platform
import random
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
import uuid
import warnings
import zipfile
from abc import ABC
from abc import abstractmethod
from enum import Enum
from io import BytesIO
from multiprocessing import Process
from numbers import *
from os import PathLike
from pathlib import Path
from subprocess import DEVNULL
from subprocess import PIPE
from threading import Lock
from threading import Thread
from time import time as now
from typing import *

import attrs
import cachetools
import cattrs
import click
import distro
import dotenv
import forbiddenfruit
import halo
import intervaltree
import loguru
import numpy
import PIL
import PIL.Image
import schedule
import toml
import tqdm
import validators
from appdirs import AppDirs
from attrs import Factory
from attrs import define
from attrs import field
from dotmap import DotMap
from numpy import pi as PI
from typer import Context as TyperContext
from typer import Option as TyperOption
from typer import Typer as TyperApp

# -------------------------------------------------------------------------------------------------|

# Note: List of modules that take a bit to import:
# Fixme: typer, rich, soundcard
# - imageio_ffmpeg
# - moderngl_window
# - transformers
# - torch
# - openai
# - gradio
# - requests
# - arrow

while True:
    with BrokenImports():
        import imgui
        import moderngl
        import torch
        import transformers
        import zmq
        break

# -------------------------------------------------------------------------------------------------|

# # Custom types
Image:     TypeAlias = PIL.Image.Image
Unchanged: TypeAlias = None
URL:       TypeAlias = str
Option               = Union
Range:     TypeAlias = range

# Units
Seconds:   TypeAlias = float
Hertz:     TypeAlias = float
Samples:   TypeAlias = int
Degrees:   TypeAlias = float
Radians:   TypeAlias = float

# Fix: typing.Self was implemented in Python 3.11
if sys.version_info < (3, 11):
    Self = TypeVar("Self")

# Recurring math constants
TAU     = (2 * PI)
SQRT2   = numpy.sqrt(2)
SQRT3   = numpy.sqrt(3)
SQRT_PI = numpy.sqrt(PI)
