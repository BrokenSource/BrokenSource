import os
from contextlib import contextmanager

from . import *

# Numpy's blas broken multiprocessing on matmul
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
os.environ["OMP_NUM_THREADS"] = "1"

# https://github.com/pytorch/vision/issues/1899#issuecomment-598200938
# Patch torch.jit requiring inspect.getsource
if BROKEN_PYINSTALLER:
    try:
        import torch.jit
        patch = lambda object, **kwargs: object
        torch.jit.script_method = patch
        torch.jit.script = patch
    except (ModuleNotFoundError, ImportError):
        pass

    # Close Pyinstaller splash screen
    import pyi_splash
    pyi_splash.close()

# -------------------------------------------------------------------------------------------------|

class BrokenImportError:
    LAST_ERROR = None
    ...

@contextmanager
def BrokenImports():
    """
    Ignore import errors inside this context, replaces the module with BrokenImportError class

    Usage:
    | while True:
    |     with BrokenImports():
    |         import A
    |         import B
    |         import C
    |         break
    """
    try:
        yield

    except (ModuleNotFoundError, ImportError) as error:

        # Same error as last time, raise it (import loop?)
        if BrokenImportError.LAST_ERROR == str(error):
            raise error
        BrokenImportError.LAST_ERROR = str(error)

        # Create a fake module
        import_error = BrokenImportError()
        sys.modules[error.name] = import_error
        sys.modules[error.name].__spec__ = import_error
        globals()[error.name] = import_error

    except Exception as error:
        raise error

# -------------------------------------------------------------------------------------------------|

# Note: List of modules that take a bit import:
# Fixme: typer, rich, soundcard
# - imageio_ffmpeg
# - moderngl_window
# - requests
# - arrow

while True:
    with BrokenImports():
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
        import operator
        import os
        import pickle
        import platform
        import random
        import re
        import shutil
        import subprocess
        import tempfile
        import time
        import types
        import uuid
        import warnings
        import zipfile
        from abc import ABC, abstractmethod
        from dataclasses import dataclass
        from enum import Enum
        from functools import cache
        from io import BytesIO
        from os import PathLike
        from pathlib import Path
        from shutil import which as find_binary
        from subprocess import DEVNULL, PIPE, Popen, check_output, run
        from sys import argv
        from threading import Thread
        from time import time as now
        from typing import *

        import aenum
        import attrs
        import audioread
        import diffusers
        import diskcache
        import distro
        import dotenv
        import forbiddenfruit
        import glfw
        import gradio
        import halo
        import imgui
        import intervaltree
        import loguru
        import moderngl
        import numpy
        import openai
        import opensimplex
        import PIL
        import PIL.Image
        import quaternion
        import rich.prompt
        import schedule
        import soundcard
        import toml
        import torch
        import transformers
        import typer
        from appdirs import AppDirs
        from dotmap import DotMap
        from tqdm import tqdm

        break

# -------------------------------------------------------------------------------------------------|

numpy.set_printoptions(precision=5, suppress=True)

# # Custom types, some Rust inspiration

# PIL.Image is a module, PIL.Image.Image is the class
PilImage = PIL.Image.Image

# Stuff that accepts "anything that can be converted to X"
URL = str

# def divide(a, b) -> Option[float, ZeroDivisionError]:
Option = Union

# self.__class__ -> "Self" class
Self = Any

# Values might not be updated
# def load(a: type=Unchanged): ...
Unchanged = None
