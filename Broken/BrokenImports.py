import sys
from contextlib import contextmanager

from . import *

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
    LAST_ERROR = None
    ...

@contextmanager
def BrokenImports():
    try:
        yield
    except (ModuleNotFoundError, ImportError) as error:

        # ERROR: Same error as last time, raise it (import loop?)
        if BrokenImportError.LAST_ERROR == str(error):
            raise error

        # Save last error (see above)
        BrokenImportError.LAST_ERROR = str(error)

        # Module and its spec import error class
        import_error = BrokenImportError()

        # Patch system.modules for no re-importing
        sys.modules[error.name] = import_error

        # "spec is not None" -> make it something, might break stuff
        sys.modules[error.name].__spec__ = import_error

        # Make it available on local globals() else name not found
        globals()[error.name] = import_error

    except Exception as error:
        raise error

# -------------------------------------------------------------------------------------------------|

while True:
    with BrokenImports():
        import ast
        import configparser
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
        from contextlib import suppress
        from dataclasses import dataclass
        from enum import Enum
        from importlib import resources as get_resource
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
        import arrow
        import attrs
        import audioread
        import diffusers
        import diskcache
        import distro
        import forbiddenfruit
        import glfw
        import gradio
        import halo
        import imageio_ffmpeg
        import imgui
        import intervaltree
        import loguru
        import moderngl
        import moderngl_window
        import moderngl_window.integrations.imgui
        import numpy
        import openai
        import PIL
        import PIL.Image
        import pkg_resources
        import quaternion
        import requests
        import requests_cache
        import rich
        import rich.prompt
        import schedule
        import soundcard
        import thefuzz
        import toml
        import torch
        import transformers
        import typer
        import yaml
        from appdirs import AppDirs
        from dotmap import DotMap
        from tqdm import tqdm
        break

numpy.set_printoptions(precision=5, suppress=True)

# Numpy's blas broken multiprocessing on matmul
# https://github.com/numpy/numpy/issues/18669#issuecomment-820510379
os.environ["OMP_NUM_THREADS"] = "1"

# -------------------------------------------------------------------------------------------------|

# # Custom types, some Rust inspiration

# PIL.Image is a module, PIL.Image.Image is the class
PilImage  = PIL.Image.Image

# Stuff that accepts "anything that can be converted to X"
URL       = str

# def divide(a, b) -> Option[float, ZeroDivisionError]:
Option = Union

# self.__class__ -> "Self" class
Self   = Any

# Values might not be updated
# def load(a: type=Unchanged): ...
Unchanged = None
