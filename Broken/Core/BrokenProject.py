from __future__ import annotations

import importlib.metadata
import importlib.resources
import os
import re
import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Self

import dotenv
from appdirs import AppDirs
from attr import Factory, define, field
from rich import print as rprint
from rich.align import Align
from rich.panel import Panel
from typer import Context

import Broken
from Broken import (
    BrokenLogging,
    BrokenPath,
    BrokenPlatform,
    BrokenProfiler,
    apply,
    log,
    shell,
)
from Broken.Core.BrokenTyper import BrokenTyper
from Broken.Core.BrokenUtils import BrokenAttrs


def mkdir(path: Path, resolve: bool=True) -> Path:
    """Make a directory and return it"""
    path = Path(path).resolve() if resolve else Path(path)
    if not path.exists():
        log.info(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path

@define(slots=False)
class _BrokenProjectDirectories:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # App basic information
    APP_DIRS: AppDirs = field(default=None)

    def __attrs_post_init__(self):
        args = (self.BROKEN_PROJECT.APP_AUTHOR, self.BROKEN_PROJECT.APP_NAME)
        self.APP_DIRS = AppDirs(*reversed(args) if (os.name == "nt") else args)

    @property
    def PACKAGE(self) -> Path:
        """
        When running from the Source Code:
            - The current project's __init__.py location

        When running from a Release:
            - Directory where the executable is located
        """
        if Broken.RELEASE:
            return Path(sys.executable).parent.resolve()

        return Path(self.BROKEN_PROJECT.PACKAGE).parent.resolve()

    # # Convenience properties

    @property
    def APP_NAME(self) -> str:
        return self.BROKEN_PROJECT.APP_NAME

    @property
    def APP_AUTHOR(self) -> str:
        return self.BROKEN_PROJECT.APP_AUTHOR

    # # Unknown / new project directories

    def __set__(self, name: str, value: Path) -> Path:
        """Create a new directory property if Path is given, else set the value"""
        self.__dict__[name] = value if not isinstance(value, Path) else mkdir(value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    # # Base directories

    @property
    def REPOSITORY(self) -> Path:
        """Broken Source's Monorepo directory"""
        return mkdir(self.PACKAGE.parent)

    @property
    def HOME(self) -> Path:
        """(Unix: /home/$USER), (Windows: C://Users//$USER)"""
        return mkdir(Path.home())

    # # Common system directories

    @property
    def SYSTEM_ROOT(self) -> Path:
        """(Unix: /), (Windows: C://)"""
        return mkdir("/")

    @property
    def SYSTEM_TEMP(self) -> Path:
        """(Unix: /tmp), (Windows: C://Windows//Temp)"""
        return mkdir(tempfile.gettempdir())

    # # Broken monorepo specific, potentially useful

    @property
    def BROKEN_RELEASES(self) -> Path:
        return mkdir(self.REPOSITORY/"Release")

    @property
    def BROKEN_BUILD(self) -> Path:
        return mkdir(self.REPOSITORY/"Build")

    @property
    def BROKEN_WINEPREFIX(self) -> Path:
        return mkdir(self.BROKEN_BUILD/"Wineprefix")

    @property
    def BROKEN_WHEELS(self) -> Path:
        return mkdir(self.BROKEN_BUILD/"Wheels")

    @property
    def BROKEN_PROJECTS(self) -> Path:
        return mkdir(self.REPOSITORY/"Projects")

    @property
    def BROKEN_HOOK(self) -> Path:
        return mkdir(self.PROJECTS/"Hook")

    @property
    def BROKEN_META(self) -> Path:
        return mkdir(self.REPOSITORY/"Meta")

    @property
    def BROKEN_FORK(self) -> Path:
        return mkdir(self.BROKEN_META/"Fork")

    @property
    def BROKEN_PRIVATE(self) -> Path:
        return mkdir(self.REPOSITORY/"Private")

    # # Meta directories - Broken monorepo specific

    @property
    def WEBSITE(self) -> Path:
        return mkdir(self.REPOSITORY/"Website")

    @property
    def PAPERS(self) -> Path:
        return mkdir(self.META/"Papers")

    @property
    def TEMPLATES(self) -> Path:
        return mkdir(self.META/"Templates")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        """Root for the current Project's Workspace"""
        if (path := os.environ.get("WORKSPACE", None)):
            return mkdir(Path(path)/self.APP_AUTHOR/self.APP_NAME)
        if (os.name == "nt"):
            return mkdir(Path(self.APP_DIRS.user_data_dir))
        else:
            return mkdir(Path(self.APP_DIRS.user_data_dir)/self.APP_NAME)

    @property
    def CONFIG(self) -> Path:
        """General config directory"""
        return mkdir(self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        """General logs directory"""
        return mkdir(self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        """General cache directory"""
        return mkdir(self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        """General Data directory"""
        return mkdir(self.WORKSPACE/"Data")

    @property
    def MOCK(self) -> Path:
        """Mock directory for testing"""
        return mkdir(self.WORKSPACE/"Mock")

    @property
    def PROJECTS(self) -> Path:
        """Projects directory (e.g. Video Editor or IDEs)"""
        return mkdir(self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        """Output directory if it makes more sense than .DATA or .PROJECTS"""
        return mkdir(self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        """Downloads directory"""
        return mkdir(self.WORKSPACE/"Downloads")

    @property
    def EXTERNALS(self) -> Path:
        """Third party dependencies"""
        return mkdir(self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        """Third party archives"""
        return mkdir(self.EXTERNALS/"Archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        """Third party images"""
        return mkdir(self.EXTERNALS/"Images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        """Third party audio"""
        return mkdir(self.EXTERNALS/"Audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        """Third party fonts"""
        return mkdir(self.EXTERNALS/"Fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        """Third party soundfonts"""
        return mkdir(self.EXTERNALS/"Soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        """Third party midis"""
        return mkdir(self.EXTERNALS/"Midis")

    @property
    def TEMP(self) -> Path:
        """Temporary directory for working files"""
        return mkdir(self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        """Dump directory for debugging (e.g. Shaders)"""
        return mkdir(self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        """Screenshots directory"""
        return mkdir(self.WORKSPACE/"Screenshots")

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class _BrokenProjectResources:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # # Internal states

    __RESOURCES__: Path = field(default=None)

    def __attrs_post_init__(self):
        if self.BROKEN_PROJECT.RESOURCES:

            # Fixme (#spec): Python 3.9 workaround; Spec-less packages
            if (sys.version_info < (3, 10)):
                spec = self.BROKEN_PROJECT.RESOURCES.__spec__
                spec.origin = spec.submodule_search_locations[0] + "/SpecLessPackagePy39Workaround"

            self.__RESOURCES__ = importlib.resources.files(self.BROKEN_PROJECT.RESOURCES)

    def __div__(self, name: str) -> Path:
        return self.__RESOURCES__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    @property
    def WHEELS(self) -> Path:
        return mkdir(self.__RESOURCES__/"Wheels")

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return mkdir(self.__RESOURCES__/"Images")

    @property
    def AUDIO(self) -> Path:
        return mkdir(self.__RESOURCES__/"Audio")

    # # Branding section

    @property
    def ICON(self) -> Path:
        """Application icon in PNG format"""
        return mkdir(self.IMAGES)/f"{self.BROKEN_PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        """Application icon in ICO format"""
        return mkdir(self.IMAGES)/f"{self.BROKEN_PROJECT.APP_NAME}.ico"

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        return mkdir(self.__RESOURCES__/"Scenes")

    @property
    def SHADERS(self) -> Path:
        return mkdir(self.__RESOURCES__/"Shaders")

    @property
    def SHADERS_INCLUDE(self) -> Path:
        return mkdir(self.SHADERS/"Include")

    @property
    def FRAGMENT(self) -> Path:
        return mkdir(self.SHADERS/"Fragment")

    @property
    def VERTEX(self) -> Path:
        return mkdir(self.SHADERS/"Vertex")

    # # Generic

    @property
    def PROMPTS(self) -> Path:
        return mkdir(self.__RESOURCES__/"Prompts")

    @property
    def FONTS(self) -> Path:
        return mkdir(self.__RESOURCES__/"Fonts")

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class BrokenProject:
    # Note: Send the importer's __init__.py's __file__ variable
    PACKAGE: str

    # App information
    APP_NAME:   str = field(default="Broken")
    APP_AUTHOR: str = field(default="BrokenSource")

    # Standard Broken objects for a project
    DIRECTORIES: _BrokenProjectDirectories = None
    RESOURCES:   _BrokenProjectResources   = None
    VERSION:     str                       = None

    def __attrs_post_init__(self):
        self.DIRECTORIES = _BrokenProjectDirectories(BROKEN_PROJECT=self)
        self.RESOURCES   = _BrokenProjectResources  (BROKEN_PROJECT=self)
        self.PACKAGE     = Path(self.PACKAGE)
        self.VERSION     = Broken.VERSION
        BrokenLogging.set_project(self.APP_NAME)

        # Replace Broken.PROJECT once with the first project
        # initialized that is not the main project itself
        if (project := getattr(Broken, "PROJECT", None)):
            if (project is Broken.BROKEN):
                self.pyapp_new_binary_restore_hook()
                Broken.PROJECT = self

        # Print version information and exit on "--version/-V"
        if (self.APP_NAME != "Broken"):
            if (len(sys.argv) > 1) and (sys.argv[1] in ("--version", "-V")) and (not sys.argv[2:]):
                print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.CurrentTarget}")
                exit(0)

        # Convenience: Symlink Workspace to projects data directory
        if Broken.DEVELOPMENT:
            BrokenPath.symlink(
                virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
                real=self.DIRECTORIES.WORKSPACE,
                echo=False
            )

        # Load .env files from the project
        for env in self.DIRECTORIES.REPOSITORY.glob("*.env"):
            dotenv.load_dotenv(env)

    def chdir(self) -> Self:
        """Change directory to the project's root"""
        return os.chdir(self.PACKAGE.parent.parent) or self

    def welcome(self):
        """Pretty Welcome Message!"""
        import pyfiglet

        # Build message
        ascii = pyfiglet.figlet_format(self.APP_NAME)
        ascii = '\n'.join((x for x in ascii.split('\n') if x.strip()))

        # Print panel center-justified lines
        rprint(Panel(
            Align.center(ascii + "\n"),
            subtitle=' '.join((
                f"Made with ❤️ by {self.APP_AUTHOR},",
                f"Python {sys.version.split()[0]}"
            )),
        ))

    def pyapp_new_binary_restore_hook(self) -> None:
        """One might send rolling releases or development betas of the same major version; whenever
        the current PyApp binary changes hash, we reinstall the virtual environment"""
        if not (pyapp_binary := os.environ.get("PYAPP", False)):
            return

        import hashlib
        venv_path = Path(os.environ["VIRTUAL_ENV"])
        hash_file = venv_path.parent/f"{self.APP_NAME.lower()}-{self.VERSION}.sha256"
        this_hash = hashlib.sha256(open(pyapp_binary, "rb").read()).hexdigest()
        old_hash  = (hash_file.read_text() if hash_file.exists() else None)
        hash_file.write_text(this_hash)

        # "If either hash differs and not on the first run"
        if (old_hash is not None) and (old_hash != this_hash):
            print("-"*shutil.get_terminal_size().columns)
            log.info(f"Detected different binary hash for this release version {self.VERSION} of the Project {self.APP_NAME}")
            log.info(f"• Path: ({venv_path})")
            log.info("• Reinstalling the Virtual Environment alongside dependencies")

            # Fixme (#ntfs): 🤓 https://superuser.com/questions/488127"
            # Fixme (#ntfs): 💪 https://unix.stackexchange.com/questions/49299
            if BrokenPlatform.OnWindows:
                previous = venv_path.with_name("0.0.0")
                BrokenPath.remove(previous)
                venv_path.rename(previous)
                input("\nPlease, reopen this Executable due technical reasons of Windows NTFS. Press Enter to exit.\n")
                exit(0)
            else:
                shell(pyapp_binary, os.environ["PYAPP_COMMAND_NAME"], "restore", stdout=subprocess.DEVNULL)
                print("-"*shutil.get_terminal_size().columns)
                sys.exit(shell(pyapp_binary, sys.argv[1:]).returncode)

# -------------------------------------------------------------------------------------------------|

@define
class BrokenApp(ABC, BrokenAttrs):
    PROJECT: BrokenProject
    typer: BrokenTyper = Factory(BrokenTyper)

    def __post__(self):

        # Windows users have a tendency to not run stuff on a terminal...
        self.typer.repl = (Broken.RELEASE and BrokenPlatform.OnWindows)

        with BrokenProfiler(self.PROJECT.APP_NAME):
            self.main()

    @abstractmethod
    def main(self) -> None:
        pass

    def find_projects(self, tag: str="Project") -> None:
        """Find Python files in common directories (direct call, cwd) that any class inherits from
        something that contains the substring of `tag` and add as a command to this Typer app"""
        files = deque()

        # Note: Safe get argv[1], pop if valid, else a dne path
        if (direct := Path(dict(enumerate(sys.argv)).get(1, "\0"))).exists():
            direct = Path(sys.argv.pop(1))

        # Scan files
        if (direct.suffix == ".py"):
            files.append(direct)
        elif direct.is_dir():
            files.extend(direct.glob("*.py"))
        else:
            files.extend(self.PROJECT.DIRECTORIES.PROJECTS.rglob("*.py"))
            files.extend(self.PROJECT.RESOURCES.SCENES.rglob("*.py"))
            files.extend(Path.cwd().glob("*.py"))

        # Add commands of all files, exit if none was sucessfully added
        if (sum(map(lambda file: self.add_project(file, tag), files)) == 0):
            log.warning(f"No {self.PROJECT.APP_NAME} Projects found, searched in:")
            log.warning('\n'.join(map(lambda file: f"• {file}", files)))
            exit(1)

    def regex(self, tag: str) -> re.Pattern:
        """Generates the self.regex for matching any valid Python class that contains "tag" on the
        inheritance, and its optional docstring on the next line"""
        return re.compile(
            r"^class\s+(\w+)\s*\(.*?(?:" + tag + r").*\):\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
            re.MULTILINE
        )

    def add_project(self, python: Path, tag: str="Project") -> bool:
        if not python.exists():
            return False

        def run(file, name, code):
            def run(ctx: Context):
                # Note: Point of trust transfer to the file the user is running
                exec(compile(code, file, "exec"), (namespace := {}))
                namespace[name]().cli(*ctx.args)
            return run

        # Match all scenes and their optional docstrings
        for match in self.regex(tag).finditer(code := python.read_text(encoding="utf-8")):
            class_name, docstring = match.groups()
            self.typer.command(
                target=run(python, class_name, code),
                name=class_name.lower(),
                help=(docstring or "No description provided"),
                panel=f"📦 Projects at [bold]({python})[/bold]",
                add_help_option=False,
                context=True,
            )

        return bool(self.typer.commands)
