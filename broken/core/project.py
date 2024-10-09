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
from halo import Halo
from rich import print as rprint
from rich.align import Align
from rich.panel import Panel
from typer import Context

import broken
from broken import runtime
from broken.core import BrokenAttrs, actions, flatten, shell
from broken.core.logging import BrokenLogging, log
from broken.core.path import BrokenPath
from broken.core.profiler import BrokenProfiler
from broken.core.system import BrokenSystem
from broken.core.terminal import BrokenTerminal


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
    project: BrokenProject
    app_dirs: AppDirs = field(default=None)

    def __attrs_post_init__(self):
        args = (self.project.author.lower(), self.project.name.lower())
        args = (reversed(args) if (os.name == "nt") else args)
        self.app_dirs = AppDirs(*args)

    @property
    def package(self) -> Path:
        """
        When running from the Source Code:
            - The current project's __init__.py location

        When running from a Release:
            - Directory where the executable is located
        """
        if runtime.executable:
            return Path(sys.executable).parent.resolve()
        return Path(self.project.package).parent.resolve()

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
    def repository(self) -> Path:
        """Broken Source's Monorepo directory"""
        return self.package.parent

    @property
    def home(self) -> Path:
        """(Unix: /home/$USER), (Windows: C://Users//$USER)"""
        return Path.home()

    # # Common system directories

    @property
    def system_root(self) -> Path:
        """(Unix: /), (Windows: C://)"""
        return Path("/")

    @property
    def system_temp(self) -> Path:
        """(Unix: /tmp), (Windows: %TEMP%)"""
        return Path(tempfile.gettempdir())

    # # Broken monorepo specific, potentially useful

    @property
    def broken_releases(self) -> Path:
        return mkdir(self.repository/"release")

    @property
    def broken_build(self) -> Path:
        return mkdir(self.repository/"build")

    @property
    def broken_wineprefix(self) -> Path:
        return mkdir(self.broken_build/"wineprefix")

    @property
    def broken_wheels(self) -> Path:
        return (self.broken_build/"wheels")

    @property
    def broken_projects(self) -> Path:
        return mkdir(self.repository/"projects")

    @property
    def broken_hook(self) -> Path:
        return mkdir(self.projects/"hook")

    @property
    def broken_meta(self) -> Path:
        return mkdir(self.repository/"meta")

    @property
    def broken_fork(self) -> Path:
        return mkdir(self.broken_meta/"fork")

    @property
    def broken_private(self) -> Path:
        return (self.repository/"private")

    @property
    def broken_insiders(self) -> Path:
        return (self.repository/"insiders")

    # # Meta directories

    @property
    def website(self) -> Path:
        return mkdir(self.repository/"website")

    @property
    def examples(self) -> Path:
        return mkdir(self.repository/"examples")

    # # Workspace directories

    @property
    def workspace(self) -> Path:
        """Root for the current Project's Workspace"""
        author_name = (self.project.author.lower() + "/" + self.project.name.lower())

        if (path := os.getenv("WORKSPACE", None)):
            return mkdir(Path(path)/author_name)
        if (os.name == "nt"):
            return mkdir(BrokenPath.Windows.Documents()/author_name)

        return mkdir(Path(self.app_dirs.user_data_dir)/self.project.name)

    @property
    def config(self) -> Path:
        return mkdir(self.workspace/"config")

    @property
    def logs(self) -> Path:
        return mkdir(self.workspace/"logs")

    @property
    def cache(self) -> Path:
        return mkdir(self.workspace/"cache")

    @property
    def data(self) -> Path:
        return mkdir(self.workspace/"data")

    @property
    def projects(self) -> Path:
        return mkdir(self.workspace/"projects")

    @property
    def downloads(self) -> Path:
        return mkdir(self.workspace/"downloads")

    @property
    def externals(self) -> Path:
        """Third party dependencies"""
        return mkdir(self.workspace/"externals")

    @property
    def external_archives(self) -> Path:
        return mkdir(self.externals/"archives")

    @property
    def external_images(self) -> Path:
        return mkdir(self.externals/"images")

    @property
    def external_audio(self) -> Path:
        return mkdir(self.externals/"audio")

    @property
    def external_fonts(self) -> Path:
        return mkdir(self.externals/"fonts")

    @property
    def external_soundfonts(self) -> Path:
        return mkdir(self.externals/"soundfonts")

    @property
    def external_midis(self) -> Path:
        return mkdir(self.externals/"midis")

    @property
    def temp(self) -> Path:
        return mkdir(self.workspace/"temp")

    @property
    def dump(self) -> Path:
        return mkdir(self.workspace/"dump")

    @property
    def screenshots(self) -> Path:
        return mkdir(self.workspace/"screenshots")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Resources:
    """You shouldn't really use this class directly"""
    project: BrokenProject

    def __attrs_post_init__(self):
        if self.project.resources:

            # Fixme (#py39): Python 3.9 workaround; Spec-less packages
            if (sys.version_info < (3, 10)):
                spec = self.project.resources.__spec__
                spec.origin = spec.submodule_search_locations[0] + "/SpecLessPackagePy39Workaround"

            # Note: Importlib bundles the resources with the package wheel :) !
            self.__resources__ = importlib.resources.files(self.project.resources)

    __resources__: Path = None

    @property
    def root(self) -> Path:
        # Workaround: Convert a MultiplexedPath to Path
        return mkdir(self.__resources__/"workaround"/"..")

    def __div__(self, name: str) -> Path:
        return self.__resources__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Common section

    @property
    def images(self) -> Path:
        return mkdir(self.__resources__/"images")

    @property
    def audio(self) -> Path:
        return mkdir(self.__resources__/"audio")

    # # Branding section

    @property
    def icon_png(self) -> Path:
        return mkdir(self.images)/f"{self.project.name.lower()}.png"

    @property
    def icon_ico(self) -> Path:
        return mkdir(self.images)/f"{self.project.name.lower()}.ico"

    # # Shaders section

    @property
    def scenes(self) -> Path:
        return mkdir(self.__resources__/"scenes")

    @property
    def shaders(self) -> Path:
        return mkdir(self.__resources__/"shaders")

    @property
    def shaders_include(self) -> Path:
        return mkdir(self.shaders/"include")

    @property
    def fragment(self) -> Path:
        return mkdir(self.shaders/"fragment")

    @property
    def vertex(self) -> Path:
        return mkdir(self.shaders/"vertex")

    # # Generic

    @property
    def prompts(self) -> Path:
        return mkdir(self.__resources__/"prompts")

    @property
    def fonts(self) -> Path:
        return mkdir(self.__resources__/"fonts")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenProject:
    package: str
    """Send the importer's __init__.py's __file__ variable"""

    # App information
    name: str
    author: str
    about: str = "No description provided"

    # Standard Broken objects for a project
    directories: _Directories = None
    resources: _Resources = None
    version: str = None

    def __attrs_post_init__(self):
        self.directories = _Directories(project=self)
        self.resources = _Resources(project=self)
        self.package = Path(self.package)
        self.version = runtime.version
        BrokenLogging.set_project(self.name)

        # Replace once Broken.PROJECT with the first project
        # initialized that is not the main project itself
        if (project := getattr(broken, "PROJECT", None)):
            if (project is broken.BROKEN):
                if (BrokenSystem.Administrator and not runtime.docker):
                    log.warning("Running as [bold blink red]Administrator/Root[/] is not required and discouraged")
                self.pyapp_management()
                broken.project = self

        # Print version information and exit on "--version/-V"
        if (self.name != "Broken"):
            if (len(sys.argv) > 1) and (sys.argv[1] in ("--version", "-V")) and (not sys.argv[2:]):
                print(f"{self.name} {self.version} {BrokenSystem.CurrentTarget}")
                exit(0)

        # Convenience symlink the project's workspace
        runtime.source_code and BrokenPath.symlink(
            virtual=self.directories.repository/"workspace",
            real=self.directories.workspace,
            echo=False
        )

        # Load dotenv files in common directories
        for path in (x for x in flatten(
            [self.resources.root/"Release.env"]*runtime.release,
            self.directories.repository.glob("*.env"),
        ) if x.exists()):
            dotenv.load_dotenv(path, override=True)

    def chdir(self) -> Self:
        """Change directory to the project's root"""
        return os.chdir(self.package.parent.parent) or self

    def welcome(self):
        import pyfiglet

        # Build message
        ascii = pyfiglet.figlet_format(self.name)
        ascii = '\n'.join((x for x in ascii.split('\n') if x.strip()))

        # Print panel center-justified lines
        rprint(Panel(
            Align.center(ascii + "\n"),
            subtitle=' '.join((
                f"Made with ❤️ by {self.author},",
                f"Python {sys.version.split()[0]}"
            )),
        ))

    def pyapp_management(self) -> None:
        """One might send rolling releases or development betas of the same major version; whenever
        the current PyApp binary changes hash, we reinstall the virtual environment"""
        if not (executable := os.getenv("PYAPP", False)):
            return

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
            print("-"*shutil.get_terminal_size().columns)
            log.info(f"Detected different binary hash for this release version v{self.version} of the Project {self.name}")
            log.info(f"• Path: ({venv_path})")
            log.info("• Reinstalling the Virtual Environment alongside dependencies")

            if BrokenSystem.OnWindows:
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
                print("-"*shutil.get_terminal_size().columns)
                try:
                    sys.exit(shell(executable, sys.argv[1:]).returncode)
                except KeyboardInterrupt:
                    exit(0)

        # Note: Remove before unused version checking
        BrokenPath.remove(ntfs_workaround, echo=False)

        # Note: Skip further prompts if any arguments are passed
        if actions():
            return

        # Remove unused versions of the software
        def manage_unused(version: Path):
            tracker = (version/"last-run.txt")
            tracker.touch()
            retention = 7
            import arrow

            def update_tracker(shift: int=0):
                tracker.write_text(str(arrow.utcnow().shift(days=shift)))

            # Initialize old, empty or new trackers; this is also a "first run"
            # condition, take advantage to clean previous packages cache
            if (not tracker.read_text()):
                shell(sys.executable, "-m", "uv", "cache", "clean", "--quiet")
                return update_tracker()

            last_run = arrow.get(tracker.read_text() or arrow.utcnow())
            sleeping = last_run.humanize(only_distance=True, granularity=("day"))

            # Skip in-use versions not older than the limit
            if (arrow.utcnow() < last_run.shift(days=retention)):
                return

            # Note: Only update current version tracker when it's over to avoid
            # updating it every time, avoiding issues with multiple instances
            if (version == venv_path):
                return update_tracker()

            from rich.prompt import Prompt

            log.warning((
                f"The version [bold green]v{version.name}[/] of the projects "
                f"hasn't been used for {sleeping}!"
                f"\n• [bold blue]{version}[/]"
            ))

            try:
                answer = Prompt.ask(
                    prompt="\n:: Choose an action:",
                    choices=("keep", "delete"),
                    default="delete",
                )
                if (answer == "delete"):
                    print()
                    with Halo(f"Deleting unused version v{version.name}.."):
                        shutil.rmtree(version, ignore_errors=True)
                if (answer == "keep"):
                    return update_tracker(shift=retention)
            except KeyboardInterrupt:
                exit(0)

        for version in (x for x in venv_path.parent.glob("*") if x.is_dir()):
            manage_unused(version)

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenApp(ABC, BrokenAttrs):
    project: BrokenProject
    typer: BrokenTerminal = Factory(BrokenTerminal)

    def __post__(self):
        self.typer.release_repl()
        self.typer.description = self.project.about

        with BrokenProfiler(self.project.name):
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
            files.extend(self.project.directories.projects.rglob("*.py"))
            files.extend(self.project.directories.examples.rglob("*.py"))
            files.extend(Path.cwd().glob("*.py"))

        # Add commands of all files, exit if none was sucessfully added
        if (sum(map(lambda file: self.add_project(python=file, tag=tag), files)) == 0):
            log.warning(f"No {self.project.name} {tag}s found, searched in:")
            log.warning('\n'.join(map(lambda file: f"• {file}", files)))

    def regex(self, tag: str) -> re.Pattern:
        """Generates the self.regex for matching any valid Python class that contains "tag" on the
        inheritance substring, and its optional docstring on the next line"""
        return re.compile(
            r"^class\s+(\w+)\s*\(.*?(?:" + tag + r").*\):\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
            re.MULTILINE
        )

    def add_project(self, python: Path, tag: str="Project") -> bool:
        if not python.exists():
            return False

        def run(file: Path, name: str, code: str):
            def run(ctx: Context):
                # Note: Point of trust transfer to the file the user is running
                exec(compile(code, file, "exec"), (namespace := {}))
                namespace[name]().cli(*ctx.args)
            return run

        # Match all scenes and their optional docstrings
        for match in self.regex(tag).finditer(code := python.read_text("utf-8")):
            class_name, docstring = match.groups()
            self.typer.command(
                target=run(python, class_name, code),
                name=class_name.lower(),
                description=(docstring or "No description provided"),
                panel=f"📦 Projects at [bold]({python})[/]",
                context=True,
                help=False,
            )

        return bool(self.typer.commands)
