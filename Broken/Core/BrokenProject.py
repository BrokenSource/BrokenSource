from __future__ import annotations

import contextlib
import importlib.metadata
import importlib.resources
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Self

import dotenv
from appdirs import AppDirs
from attr import define, field
from halo import Halo
from rich import print as rprint
from rich.align import Align
from rich.panel import Panel

import Broken
from Broken import Environment, Runtime
from Broken.Core import (
    BrokenCache,
    arguments,
    list_get,
    shell,
)
from Broken.Core.BrokenLogging import BrokenLogging, log
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import BrokenPlatform
from Broken.Core.BrokenTrackers import FileTracker

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenProject:
    PACKAGE: Path = field(converter=lambda x: Path(x).parent)
    """Send the importer's __init__.py's __file__ variable"""

    # App information
    APP_NAME: str
    APP_AUTHOR: str
    VERSION: str = Runtime.Version
    ABOUT: str = "No description provided"

    # Standard Broken objects for a project
    DIRECTORIES: _Directories = None
    RESOURCES: _Resources = None

    def __attrs_post_init__(self):
        self.DIRECTORIES = _Directories(PROJECT=self)
        self.RESOURCES = _Resources(PROJECT=self)
        BrokenLogging.set_project(self.APP_NAME)

        # Print version information on "--version/-V"
        if (list_get(sys.argv, 1) in ("--version", "-V")):
            print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.Host.value}")
            sys.exit(0)

        # Replace Broken.PROJECT with the first initialized project
        if (project := getattr(Broken, "PROJECT", None)):
            if (project is Broken.BROKEN):
                if (BrokenPlatform.Root and not Runtime.Docker):
                    log.warning("Running as [bold blink red]Administrator or Root[/] is discouraged unless necessary!")
                self._pyapp_management()
                Broken.PROJECT = self

        # Convenience symlink the project's workspace
        if Runtime.Source and Environment.flag("WORKSPACE_SYMLINK", 0):
            BrokenPath.symlink(
                virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
                real=self.DIRECTORIES.WORKSPACE, echo=False
            )

        # Load dotenv files in common directories
        for path in self.DIRECTORIES.REPOSITORY.glob("*.env"):
            dotenv.load_dotenv(path, override=True)

    def chdir(self) -> Self:
        """Change directory to the project's root"""
        return os.chdir(self.PACKAGE.parent.parent) or self

    def welcome(self) -> None:
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
        if not (executable := Environment.get("PYAPP")):
            return None

        # ---------------------------------------------------------------------------------------- #

        import hashlib
        venv_path = Path(Environment.get("VIRTUAL_ENV"))
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

            with BrokenCache.requests(
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
                        f"A newer version of the project [bold blue]v{latest}[/] is available! "
                        f"Get it at https://brokensrc.dev/get/releases/ (Current: v{current})"
                    ))

                # Back to the future!
                elif (current > latest):
                    log.error(f"[bold indian_red]For whatever reason, the current version [bold blue]v{self.VERSION}[/] is newer than the latest [bold blue]v{latest}[/][/]")
                    log.error("[bold indian_red]• This is fine if you're running a development or pre-release version, don't worry;[/]")
                    log.error("[bold indian_red]• Otherwise, it was likely recalled for whatever reason, consider downgrading![/]")

        # Warn: Must not interrupt user if actions are being taken (argv)
        if Environment.flag("VERSION_CHECK", 1) and (not arguments()):
            with contextlib.suppress(Exception):
                check_new_version()

        # ---------------------------------------------------------------------------------------- #

        def manage_install(version: Path):
            tracker = FileTracker(version/"version.tracker")
            tracker.retention.days = 7

            # Running a new version, prune previous cache
            if (tracker.first):
                shell(sys.executable, "-m", "uv", "cache", "prune", "--quiet")

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
                f"\n[bold bright_black]• Files at: {version}[/]"
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
        if Environment.flag("UNUSED_CHECK", 1) and (not arguments()):
            for version in (x for x in venv_path.parent.glob("*") if x.is_dir()):
                with contextlib.suppress(Exception):
                    manage_install(version)

    def uninstall(self) -> None:
        ...

# ------------------------------------------------------------------------------------------------ #

def mkdir(path: Path, resolve: bool=True) -> Path:
    """Make a directory and return it"""
    path = Path(path).resolve() if resolve else Path(path)
    if not path.exists():
        log.info(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path

@define(slots=False)
class _Directories:
    PROJECT: BrokenProject
    APP_DIRS: AppDirs = None

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
        self.__dict__[name] = (value if not isinstance(value, Path) else mkdir(value))

    def __setattr__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    # # Base directories

    @property
    def REPOSITORY(self) -> Path:
        """The current project repository's root"""
        return self.PACKAGE.parent

    @property
    def SYSTEM_TEMP(self) -> Path:
        return (Path(tempfile.gettempdir())/self.PROJECT.APP_AUTHOR/self.PROJECT.APP_NAME)

    # # Repository specific

    @property
    def REPO_RELEASES(self) -> Path:
        return (self.REPOSITORY/"Release")

    @property
    def REPO_BUILD(self) -> Path:
        return (self.REPOSITORY/"Build")

    @property
    def REPO_DOCKER(self) -> Path:
        return (self.REPOSITORY/"Docker")

    @property
    def BUILD_WINEPREFIX(self) -> Path:
        return (self.REPO_BUILD/"Wineprefix")

    @property
    def BUILD_WHEELS(self) -> Path:
        return (self.REPO_BUILD/"Wheels")

    @property
    def REPO_META(self) -> Path:
        return (self.REPOSITORY/"Meta")

    @property
    def INSIDERS(self) -> Path:
        return (self.REPO_META/"Insiders")

    # # Meta directories

    @property
    def REPO_WEBSITE(self) -> Path:
        return (self.REPOSITORY/"Website")

    @property
    def REPO_EXAMPLES(self) -> Path:
        return (self.REPOSITORY/"Examples")

    @property
    def REPO_PROJECTS(self) -> Path:
        return (self.REPOSITORY/"Projects")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        """Workspace root of the current project"""
        if (path := Environment.get("WORKSPACE")):
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
    def TEMP(self) -> Path:
        return mkdir(self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        return mkdir(self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        return mkdir(self.WORKSPACE/"Screenshots")

    # # Third party dependencies

    @property
    def EXTERNALS(self) -> Path:
        return mkdir(self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_MODELS(self) -> Path:
        return mkdir(self.EXTERNALS/"Models")

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

        if (not self.__RESOURCES__):
            raise FileNotFoundError("Resources aren't being bundled with the package!")

        # Workaround: Convert a MultiplexedPath to Path
        return mkdir(self.__RESOURCES__/"workaround"/"..")

    def __div__(self, name: str) -> Path:
        return (self.__RESOURCES__/name)

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return mkdir(self.ROOT/"Images")

    @property
    def AUDIO(self) -> Path:
        return mkdir(self.ROOT/"Audio")

    @property
    def FONTS(self) -> Path:
        return mkdir(self.ROOT/"Fonts")

    @property
    def TEMPLATES(self) -> Path:
        return mkdir(self.ROOT/"Templates")

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
        return mkdir(self.ROOT/"Scenes")

    @property
    def SHADERS(self) -> Path:
        return mkdir(self.ROOT/"Shaders")

    @property
    def SHADERS_INCLUDE(self) -> Path:
        return mkdir(self.SHADERS/"Include")

    @property
    def FRAGMENT(self) -> Path:
        return mkdir(self.SHADERS/"Fragment")

    @property
    def VERTEX(self) -> Path:
        return mkdir(self.SHADERS/"Vertex")
