#!/usr/bin/env python
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
def shell(*args, echo: bool=True, **kwargs):
    args = tuple(flatten(args))
    print(f"• Running command {args}") if echo else None
    return subprocess.run(args, **kwargs)

# -------------------------------------------------------------------------------------------------|

# Constants
INSTALL_MAX_ATTEMPTS = 3
TEMP_DIR = Path(tempfile.gettempdir())

# Binaries convenience
PYTHON = sys.executable
POETRY = [PYTHON, "-m", "poetry"]
PIP    = [PYTHON, "-m", "pip"]

# --user no longer works, thanks
os.environ["PIP_BREAK_SYSTEM_PACKAGES"] = "1"

# Write annoying __pycache__ and .pyc on temporary directory, keeps development directories clean.
# On Linux, it's under /tmp - System RAM, brutally fast, also shouldn't take that much memory
os.environ["PYTHONPYCACHEPREFIX"] = str(TEMP_DIR/"__pycache__")

# Weird KDE wallet or GNOME wallet askings on Linux
if os.name == "posix":
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# -------------------------------------------------------------------------------------------------|
# Welcome! We might be on a curl install

print("🚀 Welcome to Brakeit, the Broken Source Development Environment Bootstrapper Script 💎")

PIPE_INSTALL = "BRAKEIT_OK_NON_ATTY"

# If not running interactively, we might be on a pipe
if (not sys.stdin.isatty()) and (not os.environ.get(PIPE_INSTALL, False)):
    print("• Detected non-interactive shell, using automatic installation mode")
    os.environ[PIPE_INSTALL] = "1"
    cwd = Path.cwd()

    # Install dependencies on Windows
    if (os.name == "nt"):

        # User might not have winget
        try:
            if not shutil.which("winget"):
                shell("powershell", "-Command", "Add-AppxPackage",
                    "-RegisterByFamilyName", "-MainPackage",
                    "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe"
                )
        except Exception:
            print("Failed to find or install winget, this might cause problems")

        # User might not have git
        try:
            if not shutil.which("git"):
                shell("winget", "install", "-e", "--id", "Git.Git", "--source", "winget")
        except Exception:
            print("Failed to find or install git, this might cause problems")

    # Brakeit might be on the current directory
    if (brakeit := cwd/"brakeit").exists():
        os.chdir(brakeit.parent)
        shell(PYTHON, brakeit)

    # It might be on a BrokenSource directory
    elif (brakeit := cwd/"BrokenSource"/"brakeit").exists():
        os.chdir(brakeit.parent)
        shell(PYTHON, brakeit)

    # It might be on the parent directory
    elif (brakeit := cwd.parent/"brakeit").exists():
        os.chdir(brakeit.parent)
        shell(PYTHON, brakeit)

    # Ok to clone and run automatic installation
    else:
        shell("git", "clone", "https://github.com/BrokenSource/BrokenSource")
        os.chdir(cwd/"BrokenSource")
        shell(PYTHON, cwd/"BrokenSource/brakeit.py")

    exit(0)

# -------------------------------------------------------------------------------------------------|

# Path to this script
BRAKEIT = Path(__file__).absolute()

# Change directory to where the script is from anywhere
os.chdir(BRAKEIT.parent)

# Make the script executable (runnable if on PATH)
if os.name in ["posix", "mac"]:
    os.chmod(BRAKEIT, 0o755)

# -------------------------------------------------------------------------------------------------|

# Ensure pip is installed
for attempt in itertools.count(0):
    try:
        import pip
        break
    except ImportError:
        if attempt == INSTALL_MAX_ATTEMPTS:
            print("Failed to install pip using ensurepip")
            input("\nPress enter to continue, things might not work..")
            break
        print("Couldn't import pip, installing it...")
    except Exception as e:
        raise e

    # Fixme: Do we need a more complex solution?
    shell(PYTHON, "-m", "ensurepip", "--upgrade")

# Upgrade pip
shell(PIP, "install", "--upgrade", "pip")

# -------------------------------------------------------------------------------------------------|

# Install poetry
for attempt in itertools.count(0):

    # Couldn't install poetry or not available on Path
    if attempt == INSTALL_MAX_ATTEMPTS:
        print(f"Attempted {INSTALL_MAX_ATTEMPTS} times to install poetry, but it failed")
        print(f"1) Try restarting the shell, maybe it was installed and PATH wasn't updated")
        print( "2) Install it manually at (https://python-poetry.org/docs/#installation)")
        input("\nPress enter to continue, things might not work..")
        break

    # Call poetry --version, command might exit status 1 if it's not installed
    status = shell(POETRY, "--version", capture_output=True)

    # Poetry is installed, break
    if status.returncode == 0:
        break

    # Install poetry and try again
    shell(PIP, "install", "--user", "poetry", "--no-warn-script-location")

# Avoid connection pool is full on many-core systems
shell(POETRY, "config", "installer.max-workers", "10")

# Create, install dependencies on virtual environment
if shell(POETRY, "install").returncode != 0:
    print("Failed to install Python Virtual Environment and Dependencies")
    input("Press enter to continue...")

# -------------------------------------------------------------------------------------------------|

# # Hot patch Poetry to allow for expanduser and symlinks on path dependencies
# Note: This shouldn't break this repo, as relative paths are used, is a fix for private infra

# Find the virtual environment path
venv_path = Path(shell(POETRY, "env", "info", "-p", capture_output=True).stdout.decode().strip())

# Find and patch the file, fail safe
if (path_dependency := next(venv_path.glob("**/*/path_dependency.py"))):
    path_dependency.write_text(
        path_dependency.read_text().replace(
            "self._path = path\n",
            "self._path = (path := path.expanduser())\n"
        )
    )

# -------------------------------------------------------------------------------------------------|

# Bonus: Symlink the venv path to the current directory
# Do that on the installer script as `poetry env info -p` is slow
# Note: This is not a crucial step
try:
    # Remove previous symlink if exists
    if (dot_venv := BRAKEIT.parent/".venvs").exists():
        dot_venv.unlink()

    # Actually symlink .venvs -> Poetry venvs directory
    dot_venv.symlink_to(venv_path.parent)

except Exception:
    print("Couldn't symlink .venvs to the virtual environment path, skipping")

# -------------------------------------------------------------------------------------------------|

# Enable execution of scripts if on PowerShell
if os.name == "nt":
    if shell("powershell", "-Command", "Set-ExecutionPolicy", "RemoteSigned", "-Scope", "CurrentUser").returncode != 0:
        print("Failed to enable execution of scripts for PowerShell, it might fail to activate Virtual Environments")

# -------------------------------------------------------------------------------------------------|

# Welcome ✨
shell(POETRY, "run", "broken", "welcome", echo=False)

# Install scripts, desktop files and submodules (+ignore private infra)
if shell(POETRY, "run", "broken", "submodules", echo=False).returncode != 0:
    print("Failed to clone one or many essential or not public submodules")
    input("Press enter to continue...")
shell(POETRY, "run", "broken", "install", echo=False)

# Enter virtual environment
shell(POETRY, "shell", echo=False)