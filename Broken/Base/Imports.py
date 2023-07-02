import sys as system
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
    ...

@contextmanager
def BrokenImports():
    try:
        yield
    except (ModuleNotFoundError, ImportError) as error:
        # Module and its spec import error class
        import_error = BrokenImportError()

        # Patch system.modules for no re-importing
        system.modules[error.name] = import_error

        # "spec is not None" -> make it something, might break stuff
        system.modules[error.name].__spec__ = import_error

        # Make it available on local globals() else name not found
        globals()[error.name] = import_error

# -------------------------------------------------------------------------------------------------|

while True:
    with BrokenImports():
        import configparser
        import ctypes
        import datetime
        import hashlib
        import importlib
        import inspect
        import itertools
        import os
        import platform
        import random
        import re
        import shutil
        import subprocess
        import tempfile
        import zipfile
        from abc import ABC
        from abc import abstractmethod
        from contextlib import suppress
        from copy import deepcopy
        from dataclasses import dataclass
        from enum import Enum
        from functools import lru_cache
        from functools import wraps
        from io import BytesIO
        from math import *
        from os import PathLike
        from os import environ as env
        from os import getcwd as working_directory
        from pathlib import Path
        from shutil import which as find_binary
        from subprocess import PIPE
        from subprocess import Popen
        from subprocess import check_output
        from subprocess import run
        from sys import argv
        from threading import Thread
        from time import sleep
        from time import time as now
        from typing import Any
        from typing import Dict
        from typing import Iterable
        from typing import List
        from typing import Tuple
        from typing import Union
        from uuid import uuid4 as uuid

        import arrow
        import distro
        import forbiddenfruit
        import halo
        import loguru
        import moderngl
        import numpy
        import openai
        import PIL
        import PIL.Image
        import requests
        import requests_cache
        import rich
        import rich.prompt
        import toml
        import transformers
        import typer
        from aenum import extend_enum
        from appdirs import AppDirs
        from dotmap import DotMap
        from numpy import *
        from tqdm import tqdm

        break
