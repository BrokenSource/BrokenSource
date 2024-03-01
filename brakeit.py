#!/usr/bin/env python

# Warn: Remember to sync with Website on any changes

import itertools
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# -------------------------------------------------------------------------------------------------|
# Functions

# Flatten a list of lists, recursively
flatten = lambda stuff: [
    item for subitem in stuff for item in
    (flatten(subitem) if isinstance(subitem, (list, tuple)) else [subitem])
]

# Simple wrapper on subprocess.run to print and flatten commands
def shell(*args, echo: bool=True, Popen: bool=False, **kwargs):
    args = tuple(map(str, flatten(args)))
    print(f"• Running command {args}") if echo else None
    if Popen: return subprocess.Popen(args, **kwargs)
    return subprocess.run(args, **kwargs)

# -------------------------------------------------------------------------------------------------|

# Constants
INSTALL_MAX_ATTEMPTS = 3
TEMP_DIR = Path(tempfile.gettempdir())

# Binaries convenience
PYTHON = sys.executable
POETRY = [PYTHON, "-m", "poetry"]
PIP    = [PYTHON, "-m", "pip", "install", "--upgrade", "--no-warn-script-location"]

# --user no longer works, thanks
os.environ["PIP_BREAK_SYSTEM_PACKAGES"] = "1"

# Write annoying __pycache__ and .pyc on temporary directory, keeps development directories clean.
# On Linux, it's under /tmp - System RAM, brutally fast, also shouldn't take that much memory
os.environ["PYTHONPYCACHEPREFIX"] = str(TEMP_DIR/"__pycache__")

# Weird KDE wallet or GNOME wallet askings on Linux
if (os.name == "posix"):
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# -------------------------------------------------------------------------------------------------|
# Welcome! We might be on a curl install

print("\n🚀 Welcome to Brakeit, the Broken Source Development Environment Entry Script 💎\n")

PIPE_INSTALL_FLAG = "BRAKEIT_OK_NON_ATTY"

# If not running interactively, we might be on a pipe
if (not sys.stdin.isatty()) and (not os.environ.get(PIPE_INSTALL_FLAG, False)):
    print("• Detected non-interactive shell (pipe installation)")
    os.environ[PIPE_INSTALL_FLAG] = "1"
    cwd = Path.cwd()

    # Brakeit might be on the current directory
    if (brakeit := cwd/"brakeit").exists():
        shell(PYTHON, brakeit)

    # It might be on a BrokenSource directory
    elif (brakeit := cwd/"BrokenSource"/"brakeit").exists():
        shell(PYTHON, brakeit)

    # It might be on the parent directory
    elif (brakeit := cwd.parent/"brakeit").exists():
        shell(PYTHON, brakeit)

    # Ok to clone and run automatic installation
    else:
        shell("git", "clone", "https://github.com/BrokenSource/BrokenSource", "--recurse-submodules")
        os.chdir(cwd/"BrokenSource")
        shell(PYTHON, cwd/"BrokenSource/brakeit.py")

    exit(0)

# -------------------------------------------------------------------------------------------------|

# Path to this script
BRAKEIT = Path(__file__).absolute()

# Change directory to where the script is from, anywhere
os.chdir(BRAKEIT.parent)

# Make the script executable (runnable if on PATH)
if os.name != "nt":
    os.chmod(BRAKEIT, 0o755)

# -------------------------------------------------------------------------------------------------|

# Ensure pip is installed
for attempt in itertools.count(0):
    try:
        import pip
        break
    except ImportError:
        if attempt == INSTALL_MAX_ATTEMPTS:
            print(f"Attempted {INSTALL_MAX_ATTEMPTS} times to install pip, but it failed")
            print(f"1) Try restarting the shell, maybe it was installed and PATH wasn't updated")
            print( "2) Install it manually at (https://pip.pypa.io/en/stable/installation)")
            input("\nPress enter to continue, things might not work..")
            break
        print("Couldn't import pip, installing it...")
    except Exception as e:
        raise e

    # Fixme: Do we need a more complex solution?
    shell(PYTHON, "-m", "ensurepip", "--upgrade")

# -------------------------------------------------------------------------------------------------|

# Install poetry
for attempt in itertools.count(0):
    try:
        import poetry
        break
    except ImportError:
        if attempt == INSTALL_MAX_ATTEMPTS:
            print(f"Attempted {INSTALL_MAX_ATTEMPTS} times to install poetry, but it failed")
            print(f"1) Try restarting the shell, maybe it was installed and PATH wasn't updated")
            print( "2) Install it manually at (https://python-poetry.org/docs/#installation)")
            input("\nPress enter to continue, things might not work..")
            break
        print("Couldn't import Poetry, installing it...")

    # Fixme: Do we need a more complex solution?
    shell(PIP, "poetry")

# Enable execution of scripts if on PowerShell
if (os.name == "nt"):
    shell("powershell", "-Command",
        "Set-ExecutionPolicy", "RemoteSigned", "-Scope", "CurrentUser",
        echo=False, Popen=True
    )

# Create, install dependencies on virtual environment
if shell(POETRY, "install", echo=False).returncode != 0:
    print("Failed to install Python Virtual Environment and Dependencies")
    input("\nPress enter to continue, things might not work..")

# -------------------------------------------------------------------------------------------------|

# Get the virtual environment path
venv_path = Path(shell(POETRY, "env", "info", "-p", echo=False, capture_output=True).stdout.decode().strip())

try:
    # Bonus: Symlink .venvs -> Poetry venvs directory
    if (dot_venv := BRAKEIT.parent/".venvs").exists():
        dot_venv.unlink()
    dot_venv.symlink_to(venv_path.parent)
except Exception:
    print("Couldn't symlink .venvs to the virtual environment path, skipping")

# -------------------------------------------------------------------------------------------------|

if shell(POETRY, "run", "broken", "install", echo=False).returncode != 0:
    print("Failed to clone one or many essential public or private submodules, or install brakeit")
    input("\nPress enter to continue, things might not work..")

# Directly execute a command
if len(sys.argv) > 1:
    shell(POETRY, "run", sys.argv[1:], echo=False)
    exit(0)

# Interactive shell
if os.environ.get("BRAKEIT_NO_SHELL", False) != "1":
    if os.name == "nt":
        shell("powershell", "-NoLogo", "-NoExit", "-File", (venv_path/"Scripts"/"activate.ps1"), echo=False)
    else:
        shell(POETRY, "shell", echo=False)

# -------------------------------------------------------------------------------------------------|
