#!/usr/bin/env python

import itertools
import os
import subprocess
import sys
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

# Binaries convenience
PYTHON = sys.executable
POETRY = [PYTHON, "-m", "poetry"]
PIP    = [PYTHON, "-m", "pip", "install", "--upgrade", "--no-warn-script-location"]

# --user no longer works, thanks
os.environ["PIP_BREAK_SYSTEM_PACKAGES"] = "1"

# Weird KDE wallet or GNOME wallet askings on Linux
if (os.name == "posix"):
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# -------------------------------------------------------------------------------------------------|
# Welcome! We might be on a curl install

PIPE_INSTALL_FLAG = "BRAKEIT_OK_NON_ATTY"

# If not running interactively, we are on a pipe
if (not sys.stdin.isatty()) and (not os.environ.get(PIPE_INSTALL_FLAG, False)):
    print("• Detected non-interactive shell (pipe installation)")
    os.environ[PIPE_INSTALL_FLAG] = "1"
    cwd = Path.cwd()

    # Try finding `brakeit.py` on nearby directories
    if (brakeit := cwd/"brakeit.py").exists():
        shell(PYTHON, brakeit)
    elif (brakeit := cwd/"BrokenSource"/"brakeit.py").exists():
        shell(PYTHON, brakeit)
    elif (brakeit := cwd.parent/"brakeit.py").exists():
        shell(PYTHON, brakeit)
    else:
        shell("git", "clone", "https://github.com/BrokenSource/BrokenSource", "--recurse-submodules", "--jobs", "4")
        os.chdir(cwd/"BrokenSource")
        shell(PYTHON, cwd/"BrokenSource"/"brakeit.py")

    exit(0)

# -------------------------------------------------------------------------------------------------|

print("\n🚀 Welcome to Brakeit, the Broken Source Development Environment Entry Script 💎\n")

# Change directory to where the script is
BRAKEIT = Path(__file__).absolute()
os.chdir(BRAKEIT.parent)

# -------------------------------------------------------------------------------------------------|

# Ensure pip is installed
for attempt in itertools.count(0):
    try:
        import pip
        break
    except ImportError:
        if attempt == INSTALL_MAX_ATTEMPTS:
            print("\n:: Error\n\n")
            print(f"Attempted {INSTALL_MAX_ATTEMPTS} times to install pip, but it failed")
            print(f"1) Try restarting the shell, maybe it was installed and PATH wasn't updated")
            print( "2) Install it manually at (https://pip.pypa.io/en/stable/installation)")
            input("\nPress enter to continue, things might not work..")
            break
    except Exception as e:
        raise e

    # Try with official get-pip.py
    if (attempt == 0):
        import requests
        try:
            exec(requests.get("https://bootstrap.pypa.io/get-pip.py").text)
        except requests.RequestException:
            print("\n:: Error\n\n")
            print("Failed to download (https://bootstrap.pypa.io/get-pip.py) for installing pip")
            print("1) Check your internet connection or the URL if you can access it")
            print("2) Run the install script again, if next with ensurepip fails")
            input("\nPress enter to continue..")
        except SystemExit:
            pass

    # Fixme: I wanted this to be the first option but it's not respecting the annoying flag
    # Fixme: PIP_BREAK_SYSTEM_PACKAGES, I've never seen anyone 'breaking their system' btw
    # Try with built-in ensurepip if any
    else:
        try:
            import ensurepip
            if (attempt == 1):
                shell(PYTHON, "-m", "ensurepip")
            elif (attempt == 2):
                shell(PYTHON, "-m", "ensurepip", "--user")
        except ImportError:
            pass

# -------------------------------------------------------------------------------------------------|

# Ensure poetry is installed
for attempt in itertools.count(0):
    try:
        if shell(POETRY, "--version", echo=False).returncode == 0:
            break
        import poetry
        break
    except ImportError:
        if attempt == INSTALL_MAX_ATTEMPTS:
            print("\n:: Error\n\n")
            print(f"Attempted {INSTALL_MAX_ATTEMPTS} times to install poetry, but it failed")
            print(f"1) Try restarting the shell, maybe it was installed and PATH wasn't updated")
            print( "2) Install it manually at (https://python-poetry.org/docs/#installation)")
            input("\nPress enter to continue, things might not work..")
            break
        print("Couldn't import Poetry, installing it...")

    # Fixme: Do we need a more complex solution?
    shell(PIP, "poetry")

# -------------------------------------------------------------------------------------------------|

# Enable execution of scripts if on PowerShell
if (os.name == "nt"):
    shell("powershell", "-Command",
        "Set-ExecutionPolicy", "RemoteSigned", "-Scope", "CurrentUser",
        echo=False, Popen=True
    )

# Create, install dependencies on virtual environment
if shell(POETRY, "install", echo=False).returncode != 0:
    print("Failed to install Python Virtual Environment and Dependencies with Poetry")
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
    print("Couldn't symlink .venvs to Poetry's Virtual Environments cache path, skipping")

# -------------------------------------------------------------------------------------------------|

# Directly execute a command
if len(sys.argv) > 1:
    shell(POETRY, "run", sys.argv[1:], echo=False)
    exit(0)

# Create direct scripts, shortcut and tips, should be safe
shell(POETRY, "run", "broken", "install", echo=False)

# Interactive shell
if os.environ.get("BRAKEIT_NO_SHELL", False) != "1":
    if os.name == "nt":
        shell("powershell", "-NoLogo", "-NoExit", "-File", (venv_path/"Scripts"/"activate.ps1"), echo=False)
    else:
        shell(POETRY, "shell", echo=False)

# -------------------------------------------------------------------------------------------------|
