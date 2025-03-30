from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from attr import define, field
from platformdirs import PlatformDirs
from rich import print as rprint

import Broken
from Broken import BrokenLogging, Environment, Runtime, Tools, log
from Broken.Core import BrokenCache, arguments, list_get, shell
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

    # Refactored functionality
    DIRECTORIES: _Directories = None
    RESOURCES: _Resources = None

    def __attrs_post_init__(self):
        BrokenLogging.set_project(self.APP_NAME)

        # Print version information and quit if requested
        if (list_get(sys.argv, 1) in ("--version", "-V")):
            print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.Host.value}")
            sys.exit(0)

        # Create refactored classes
        self.DIRECTORIES = _Directories(PROJECT=self)
        self.RESOURCES = _Resources(PROJECT=self)

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
            __import__("dotenv").load_dotenv(path, override=True)

    def welcome(self) -> None:
        import pyfiglet # noqa
        from Broken import BrokenTorch
        from rich.align import Align
        from rich.panel import Panel
        torch = BrokenTorch.version()
        ascii = pyfiglet.figlet_format(self.APP_NAME)
        ascii = '\n'.join((x for x in ascii.split('\n') if x.strip()))
        rprint(Panel(
            Align.center(ascii + "\n"),
            subtitle=''.join((
                "[bold dim]📦 "
                f"Version {self.VERSION} ",
                f"• Python {sys.version.split()[0]} ",
                f"• Torch {torch.value} " if torch else "",
                "📦[/]",
            )),
        ))

    def _pyapp_management(self) -> None:

        # Skip if not executing within a binary release
        if not (executable := Environment.get("PYAPP")):
            return None

        # ---------------------------------------------------------------------------------------- #

        import hashlib
        venv_path = Path(Environment.get("VIRTUAL_ENV"))
        hash_file = (venv_path/f"version-{self.APP_NAME.lower()}.sha256")
        prev_hash = (hash_file.read_text() if hash_file.exists() else None)
        this_hash = hashlib.sha256(open(executable, "rb").read()).hexdigest()
        hash_file.write_text(this_hash)

        # Fixme (#ntfs): https://unix.stackexchange.com/questions/49299
        # Fixme (#ntfs): https://superuser.com/questions/488127
        ntfs_workaround = venv_path.with_name("0.0.0")

        # "If (not on the first run) and (hash differs)"
        if (prev_hash is not None) and (prev_hash != this_hash):
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

            with contextlib.suppress(Exception):
                with BrokenCache.package_info(self.APP_NAME.lower()) as package:
                    latest = Version(package.info.version)

                    # Newer version available
                    if (current < latest):
                        log.minor((
                            f"A newer version of the project [bold blue]v{latest}[/] is available! "
                            f"Get it at https://brokensrc.dev/get/releases/ (Current: v{current})"
                        ))

                    # Back to the future!
                    elif (current > latest):
                        log.error(f"[bold indian_red]For whatever reason, the current version [bold blue]v{self.VERSION}[/] is newer than the latest [bold blue]v{latest}[/][/]")
                        log.error(f"[bold indian_red]• This is fine if you're running a development or prerelease version, don't worry[/]")
                        log.error(f"[bold indian_red]• Otherwise, it was likely recalled for whatever reason, consider downgrading![/]")

        # Warn: Must not interrupt user if actions are being taken (argv)
        if Environment.flag("VERSION_CHECK", 1) and (not arguments()):
            with contextlib.suppress(Exception):
                check_new_version()

        # ---------------------------------------------------------------------------------------- #

        def manage_install(version: Path):
            from packaging.version import InvalidVersion, Version

            try:
                Version(version.name)
            except InvalidVersion:
                return None

            tracker = FileTracker(version/"version.tracker")
            tracker.retention.days = 7

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
                    from halo import Halo
                    with Halo(f"Deleting unused version v{version.name}.."):
                        shutil.rmtree(version, ignore_errors=True)
                if (answer == "keep"):
                    log.minor("Keeping the version for now, will check again later!")
                    return tracker.update()
            except KeyboardInterrupt:
                exit(0)

        # Warn: Must not interrupt user if actions are being taken (argv)
        if Environment.flag("UNUSED_CHECK", 1) and (not arguments()):
            for version in (x for x in venv_path.parent.glob("*") if x.is_dir()):
                with contextlib.suppress(Exception):
                    manage_install(version)

    def uninstall(self) -> None:
        ...

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Directories:
    PROJECT: BrokenProject
    APP_DIRS: PlatformDirs = None

    def __attrs_post_init__(self):
        args = (self.PROJECT.APP_AUTHOR, self.PROJECT.APP_NAME)
        args = (reversed(args) if (os.name == "nt") else args)
        self.APP_DIRS = PlatformDirs(*args)

    # # Unknown / new project directories

    def _new_directory(self, name: str, value: Path) -> Path:
        """Create a new directory property if Path is given, else set the value"""
        self.__dict__[name] = (value if not isinstance(value, Path) else value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self._new_directory(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self._new_directory(name, value)

    # # Base directories

    @property
    def SYSTEM_TEMP(self) -> Path:
        return (
            Path(tempfile.gettempdir()) /
            self.PROJECT.APP_AUTHOR /
            self.PROJECT.APP_NAME
        )

    @property
    def REPOSITORY(self) -> Path:
        return Path(self.PROJECT.PACKAGE).parent

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
    def BUILD_WHEELS(self) -> Path:
        return (self.REPO_BUILD/"Wheels")

    @property
    def BUILD_CARGO(self) -> Path:
        return (self.REPO_BUILD/"Cargo")

    # # Meta directories

    @property
    def REPO_META(self) -> Path:
        return (self.REPOSITORY/"Meta")

    @property
    def INSIDERS(self) -> Path:
        return (self.REPO_META/"Insiders")

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
        if (path := Environment.get("WORKSPACE")):
            return (
                Path(path) /
                self.PROJECT.APP_AUTHOR /
                self.PROJECT.APP_NAME
            )
        elif (os.name == "nt"):
            return Path(self.APP_DIRS.user_data_dir)
        return (
            Path(self.APP_DIRS.user_data_dir) /
            self.PROJECT.APP_NAME
        )

    @property
    def WORKSPACE_ROOT(self) -> Path:
        return self.WORKSPACE.parent

    @property
    def CONFIG(self) -> Path:
        return (self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        return (self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        return (self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        return (self.WORKSPACE/"Data")

    @property
    def PROJECTS(self) -> Path:
        return (self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        return (self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        return (self.WORKSPACE/"Downloads")

    @property
    def TEMP(self) -> Path:
        return (self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        return (self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        return (self.WORKSPACE/"Screenshots")

    # # Third party dependencies

    @property
    def EXTERNALS(self) -> Path:
        return (self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_MODELS(self) -> Path:
        return (self.EXTERNALS/"Models")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        return (self.EXTERNALS/"Archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        return (self.EXTERNALS/"Images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        return (self.EXTERNALS/"Audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        return (self.EXTERNALS/"Fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        return (self.EXTERNALS/"Soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        return (self.EXTERNALS/"Midis")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Resources:
    PROJECT: BrokenProject
    ROOT: Path = None
    """The path of the resources package"""

    def __attrs_post_init__(self):
        self.ROOT = (self.PROJECT.PACKAGE/"Resources")

    def __div__(self, name: str) -> Path:
        return (self.ROOT/name)

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Bundled items

    @property
    def EXAMPLES(self) -> Path:
        return (self.ROOT/"Examples")

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return (self.ROOT/"Images")

    @property
    def AUDIO(self) -> Path:
        return (self.ROOT/"Audio")

    @property
    def FONTS(self) -> Path:
        return (self.ROOT/"Fonts")

    @property
    def TEMPLATES(self) -> Path:
        return (self.ROOT/"Templates")

    # # Branding section

    @property
    def ICON_PNG(self) -> Path:
        return (self.IMAGES)/f"{self.PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        return (self.IMAGES)/f"{self.PROJECT.APP_NAME}.ico"

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        return (self.ROOT/"Scenes")

    @property
    def SHADERS(self) -> Path:
        return (self.ROOT/"Shaders")

    @property
    def SHADERS_INCLUDE(self) -> Path:
        return (self.SHADERS/"Include")

    @property
    def FRAGMENT(self) -> Path:
        return (self.SHADERS/"Fragment")

    @property
    def VERTEX(self) -> Path:
        return (self.SHADERS/"Vertex")
