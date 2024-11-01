from __future__ import annotations

import contextlib
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
from halo import Halo
from rich import print as rprint
from rich.align import Align
from rich.panel import Panel
from typer import Context

import Broken
from Broken import Runtime
from Broken.Core import (
    BrokenAttrs,
    EasyTracker,
    arguments,
    flatten,
    recache,
    shell,
)
from Broken.Core.BrokenLogging import BrokenLogging, log
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import BrokenPlatform
from Broken.Core.BrokenProfiler import BrokenProfiler
from Broken.Core.BrokenTyper import BrokenTyper


def mkdir(path: Path, resolve: bool=True) -> Path:
    """Make a directory and return it"""
    path = Path(path).resolve() if resolve else Path(path)
    if not path.exists():
        log.info(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path


@define(slots=False)
class _Directories:
    """You shouldn't really use this class directly"""
    PROJECT: BrokenProject
    APP_DIRS: AppDirs = field(default=None)

    def __attrs_post_init__(self):
        args = (self.PROJECT.APP_AUTHOR, self.PROJECT.APP_NAME)
        args = (reversed(args) if (os.name == "nt") else args)
        self.APP_DIRS = AppDirs(*args)

    @property
    def PACKAGE(self) -> Path:
        """
        When running from the Source Code:
            - The current project's __init__.py location

        When running from a Release:
            - Directory where the executable is located
        """
        if Runtime.Binary:
            return Path(sys.executable).parent.resolve()
        return Path(self.PROJECT.PACKAGE).resolve()

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
        return self.PACKAGE.parent

    @property
    def SYSTEM_TEMP(self) -> Path:
        """(Unix: /tmp), (Windows: %TEMP%)"""
        return Path(tempfile.gettempdir())

    # # Broken monorepo specific, potentially useful

    @property
    def BROKEN_RELEASES(self) -> Path:
        return mkdir(self.REPOSITORY/"Release")

    @property
    def BROKEN_BUILD(self) -> Path:
        return (self.REPOSITORY/"Build")

    @property
    def BROKEN_WINEPREFIX(self) -> Path:
        return (self.BROKEN_BUILD/"Wineprefix")

    @property
    def BROKEN_WHEELS(self) -> Path:
        return (self.BROKEN_BUILD/"Wheels")

    @property
    def BROKEN_PROJECTS(self) -> Path:
        return mkdir(self.REPOSITORY/"Projects")

    @property
    def BROKEN_META(self) -> Path:
        return mkdir(self.REPOSITORY/"Meta")

    @property
    def BROKEN_INSIDERS(self) -> Path:
        return (self.BROKEN_META/"Insiders")

    # # Meta directories

    @property
    def WEBSITE(self) -> Path:
        return mkdir(self.REPOSITORY/"Website")

    @property
    def EXAMPLES(self) -> Path:
        return mkdir(self.REPOSITORY/"Examples")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        """Root for the current Project's Workspace"""
        if (path := os.getenv("WORKSPACE")):
            return mkdir(Path(path)/self.PROJECT.APP_AUTHOR/self.PROJECT.APP_NAME)
        if (os.name == "nt"):
            return mkdir(BrokenPath.Windows.Documents()/self.PROJECT.APP_AUTHOR/self.PROJECT.APP_NAME)
        return mkdir(Path(self.APP_DIRS.user_data_dir)/self.PROJECT.APP_NAME)

    @property
    def CONFIG(self) -> Path:
        return mkdir(self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        return mkdir(self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        return mkdir(self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        return mkdir(self.WORKSPACE/"Data")

    @property
    def PROJECTS(self) -> Path:
        return mkdir(self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        return mkdir(self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        return mkdir(self.WORKSPACE/"Downloads")

    @property
    def EXTERNALS(self) -> Path:
        """Third party dependencies"""
        return mkdir(self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        return mkdir(self.EXTERNALS/"Archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        return mkdir(self.EXTERNALS/"Images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        return mkdir(self.EXTERNALS/"Audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        return mkdir(self.EXTERNALS/"Fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        return mkdir(self.EXTERNALS/"Soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        return mkdir(self.EXTERNALS/"Midis")

    @property
    def TEMP(self) -> Path:
        return mkdir(self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        return mkdir(self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        return mkdir(self.WORKSPACE/"Screenshots")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Resources:
    PROJECT: BrokenProject

    def __attrs_post_init__(self):
        if self.PROJECT.RESOURCES:

            # Fixme (#py39): Python 3.9 workaround; Spec-less packages
            if (sys.version_info < (3, 10)):
                spec = self.PROJECT.RESOURCES.__spec__
                spec.origin = spec.submodule_search_locations[0] + "/SpecLessPackagePy39Workaround"

            # Note: Importlib bundles the resources with the package wheel!
            self.__RESOURCES__ = importlib.resources.files(self.PROJECT.RESOURCES)

    __RESOURCES__: Path = None

    @property
    def ROOT(self) -> Path:
        # Workaround: Convert a MultiplexedPath to Path
        return mkdir(self.__RESOURCES__/"workaround"/"..")

    def __div__(self, name: str) -> Path:
        return self.__RESOURCES__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return mkdir(self.__RESOURCES__/"Images")

    @property
    def AUDIO(self) -> Path:
        return mkdir(self.__RESOURCES__/"Audio")

    # # Branding section

    @property
    def ICON_PNG(self) -> Path:
        return mkdir(self.IMAGES)/f"{self.PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        return mkdir(self.IMAGES)/f"{self.PROJECT.APP_NAME}.ico"

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

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenProject:
    PACKAGE: Path = field(converter=lambda x: Path(x).parent)
    """Send the importer's __init__.py's __file__ variable"""

    # App information
    APP_NAME: str
    APP_AUTHOR: str
    VERSION: str = None
    ABOUT: str = "No description provided"

    # Standard Broken objects for a project
    DIRECTORIES: _Directories = None
    RESOURCES: _Resources = None

    def __attrs_post_init__(self):
        self.DIRECTORIES = _Directories(PROJECT=self)
        self.RESOURCES = _Resources(PROJECT=self)
        self.VERSION = Runtime.Version
        BrokenLogging.set_project(self.APP_NAME)

        # Replace Broken.PROJECT with the first initialized project
        if (project := getattr(Broken, "PROJECT", None)):
            if (project is Broken.BROKEN):
                if (BrokenPlatform.Administrator and not Runtime.Docker):
                    log.warning("Running as [bold blink red]Administrator or Root[/] is discouraged unless necessary!")
                self._pyapp_management()
                Broken.PROJECT = self

        # Print version information and exit on "--version/-V"
        if (self.APP_NAME != "Broken"):
            if (len(sys.argv) > 1) and (sys.argv[1] in ("--version", "-V")):
                print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.CurrentTarget}")
                exit(0)

        # Convenience symlink the project's workspace
        if Runtime.Source and (os.getenv("WORKSPACE_SYMLINK", "0") == "1"):
            BrokenPath.symlink(
                virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
                real=self.DIRECTORIES.WORKSPACE, echo=False
            )

        # Load dotenv files in common directories
        for path in (x for x in flatten(
            [self.RESOURCES.ROOT/"Release.env"]*Runtime.Binary,
            self.DIRECTORIES.REPOSITORY.glob("*.env"),
        ) if x.exists()):
            dotenv.load_dotenv(path, override=True)

    def chdir(self) -> Self:
        """Change directory to the project's root"""
        return os.chdir(self.PACKAGE.parent.parent) or self

    def welcome(self):
        import pyfiglet
        ascii = pyfiglet.figlet_format(self.APP_NAME)
        ascii = '\n'.join((x for x in ascii.split('\n') if x.strip()))
        rprint(Panel(
            Align.center(ascii + "\n"),
            subtitle=''.join((
                f"[bold dim]📦 Version {self.VERSION} • ",
                f"Python {sys.version.split()[0]} 📦[/]"
            )),
        ))

    def _pyapp_management(self) -> None:

        # Skip if not executing within a binary release
        if not (executable := os.getenv("PYAPP", False)):
            return None

        # ---------------------------------------------------------------------------------------- #

        import hashlib
        venv_path = Path(os.getenv("VIRTUAL_ENV"))
        hash_file = (venv_path/"version.sha256")
        this_hash = hashlib.sha256(open(executable, "rb").read()).hexdigest()
        old_hash  = (hash_file.read_text() if hash_file.exists() else None)
        hash_file.write_text(this_hash)

        # Fixme (#ntfs): https://superuser.com/questions/488127
        # Fixme (#ntfs): https://unix.stackexchange.com/questions/49299
        ntfs_workaround = venv_path.with_name("0.0.0")

        # "If (not on the first run) and (hash differs)"
        if (old_hash is not None) and (old_hash != this_hash):
            print("-"*shutil.get_terminal_size().columns + "\n")
            log.info(f"Detected different hash for this release version [bold blue]v{self.VERSION}[/], reinstalling..")
            log.info(f"• {venv_path}")

            if BrokenPlatform.OnWindows:
                BrokenPath.remove(ntfs_workaround)
                venv_path.rename(ntfs_workaround)
                try:
                    rprint("\n[bold orange3 blink](Warning)[/] Please, reopen this executable to continue! Press Enter to exit..", end='')
                    input()
                except KeyboardInterrupt:
                    pass
                exit(0)
            else:
                shell(executable, "self", "restore", stdout=subprocess.DEVNULL)
                print("\n" + "-"*shutil.get_terminal_size().columns + "\n")
                try:
                    sys.exit(shell(executable, sys.argv[1:], echo=False).returncode)
                except KeyboardInterrupt:
                    exit(0)

        # Note: Remove before unused version checking
        BrokenPath.remove(ntfs_workaround, echo=False)

        # ---------------------------------------------------------------------------------------- #

        if (not arguments()):
            self.welcome()

        def check_new_version():
            from packaging.version import Version

            # Skip development binaries, as they aren't on PyPI
            if (current := Version(self.VERSION)).is_prerelease:
                return None

            with recache(
                cache_name=(venv_path/"version.check"),
                expire_after=(3600),
            ) as requests:
                import json

                with contextlib.suppress(Exception):
                    _api   = f"https://pypi.org/pypi/{self.APP_NAME.lower()}/json"
                    latest = Version(json.loads(requests.get(_api).text)["info"]["version"])

                # Newer version available
                if (current < latest):
                    log.minor((
                        f"A newer version [bold blue]v{latest}[/] "
                        f"than the current [bold blue]v{current}[/] is available! "
                        "Get it at https://brokensrc.dev/get/releases/"
                    ))

                # Back to the future!
                elif (current > latest):
                    log.error(f"[bold indian_red]For whatever reason, the current version [bold blue]v{self.VERSION}[/] is newer than the latest [bold blue]v{latest}[/][/]")
                    log.error("[bold indian_red]• This is fine if you're running a development or pre-release version, don't worry;[/]")
                    log.error("[bold indian_red]• Otherwise it was likely recalled for whatever reason, consider downgrading it![/]")

        if (os.getenv("VERSION_CHECK", "1") == "1") and (not arguments()):
            with contextlib.suppress(Exception):
                check_new_version()

        # ---------------------------------------------------------------------------------------- #

        def manage_unused(version: Path):
            tracker = EasyTracker(version/"version.tracker")
            tracker.retention.days = 7

            if (tracker.first):
                shell(sys.executable, "-m", "uv", "cache",
                    "prune", "--quiet", echo=False)

            # Skip in-use versions
            if (not tracker.trigger()):
                return None

            # Late-update current tracker
            if (version == venv_path):
                return tracker.update()

            from rich.prompt import Prompt

            log.warning((
                f"The version [bold green]v{version.name}[/] of the projects "
                f"hasn't been used for {tracker.sleeping}, unninstall it to save space!"
                f"\n[bold bright_black]• Data at: {version}[/]"
            ))

            try:
                answer = Prompt.ask(
                    prompt="\n:: Choose an action:",
                    choices=("keep", "delete"),
                    default="delete",
                )
                print()
                if (answer == "delete"):
                    with Halo(f"Deleting unused version v{version.name}.."):
                        shutil.rmtree(version, ignore_errors=True)
                if (answer == "keep"):
                    log.minor("Keeping the version for now, will check again later!")
                    return tracker.update()
            except KeyboardInterrupt:
                exit(0)

        # Note: Avoid interactive prompts if running with arguments
        if (os.getenv("UNUSED_CHECK", "1") == "1") and (not arguments()):
            for version in (x for x in venv_path.parent.glob("*") if x.is_dir()):
                with contextlib.suppress(Exception):
                    manage_unused(version)

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenApp(ABC, BrokenAttrs):
    PROJECT: BrokenProject
    typer: BrokenTyper = Factory(BrokenTyper)

    def __post__(self):
        self.typer.release_repl()
        self.typer.description = self.PROJECT.ABOUT

        with BrokenProfiler(self.PROJECT.APP_NAME):
            self.main()

    @abstractmethod
    def main(self) -> None:
        pass

    def find_projects(self, tag: str="Project") -> None:
        """Find Python files in common directories (direct call, cwd) that any class inherits from
        something that contains the substring of `tag` and add as a command to this Typer app"""
        files = deque()

        # Note: Safe get argv[1], pop if valid, else a null path
        if (direct := Path(dict(enumerate(sys.argv)).get(1, "\0"))).exists():
            direct = Path(sys.argv.pop(1))

        # Scan files
        if (direct.suffix == ".py"):
            files.append(direct)
        elif direct.is_dir():
            files.extend(direct.glob("*.py"))
        else:
            files.extend(self.PROJECT.DIRECTORIES.PROJECTS.rglob("*.py"))
            files.extend(self.PROJECT.DIRECTORIES.EXAMPLES.rglob("*.py"))
            files.extend(Path.cwd().glob("*.py"))

        # Add commands of all files, exit if none was sucessfully added
        if (sum(map(lambda file: self.add_project(python=file, tag=tag), files)) == 0):
            log.warning(f"No {self.PROJECT.APP_NAME} {tag}s found, searched in:")
            log.warning('\n'.join(map(lambda file: f"• {file}", files)))

    def _regex(self, tag: str) -> re.Pattern:
        """Generates the self.regex for matching any valid Python class that contains "tag" on the
        inheritance substring, and its optional docstring on the next line"""
        return re.compile(
            r"^class\s+(\w+)\s*\(.*?(?:" + tag + r").*\):\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
            re.MULTILINE
        )

    def add_project(self, python: Path, tag: str="Project") -> bool:
        if (not python.exists()):
            return False

        def run(file: Path, name: str, code: str):
            def run(ctx: Context):
                # Note: Point of trust transfer to the file the user is running
                exec(compile(code, file, "exec"), (namespace := {}))
                namespace[name]().cli(*ctx.args)
            return run

        # Match all scenes and their optional docstrings
        matches = list(self._regex(tag).finditer(code := python.read_text("utf-8")))

        # Add a command for each match
        for match in matches:
            class_name, docstring = match.groups()
            self.typer.command(
                target=run(python, class_name, code),
                name=class_name.lower(),
                description=(docstring or "No description provided"),
                panel=f"📦 {tag}s at ({python})",
                context=True,
                help=False,
            )

        return bool(matches)
