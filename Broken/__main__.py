from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Annotated
from typing import List
from typing import Self

import toml
import typer
from attr import Factory
from attr import define
from dotmap import DotMap
from typer import Argument
from typer import Context
from typer import Option
from typer import Typer

import Broken
from Broken.Base import BrokenPath
from Broken.Base import BrokenPlatform
from Broken.Base import BrokenProfiler
from Broken.Base import BrokenTorch
from Broken.Base import BrokenTyper
from Broken.Base import TorchFlavor
from Broken.Base import flatten
from Broken.Base import shell
from Broken.BrokenEnum import BrokenEnum
from Broken.Logging import log
from Broken.Spinner import BrokenSpinner


def main():
    with BrokenProfiler("BROKEN"):
        broken = BrokenCLI()
        broken.cli()

if __name__ == "__main__":
    main()

# -------------------------------------------------------------------------------------------------|

class ProjectLanguage(BrokenEnum):
    Python  = "python"
    Rust    = "rust"
    CPP     = "cpp"
    Unknown = "unknown"

@define
class BrokenProjectCLI:
    path: Path
    name: str = "Unknown"
    broken_typer: Typer = None

    # # Main entry point

    def cli(self, ctx: Context) -> None:
        self.broken_typer = BrokenTyper(help_option=False)
        self.broken_typer.command(self.update,  add_help_option=True)
        self.broken_typer.command(self.release, add_help_option=True)
        self.broken_typer.command(self.run,     add_help_option=False, default=True)
        with BrokenPath.pushd(self.path, echo=False):
            self.broken_typer(ctx.args)

    # # Initialization

    def __attrs_post_init__(self):
        self.name = self.path.name

    def __eq__(self, other: Self) -> bool:
        return self.path == other.path

    # # Utility Attributes

    @property
    def lname(self) -> str:
        """Lowercase name"""
        return self.name.lower()

    @property
    def version(self) -> str:
        import arrow
        return self.config.setdefault("version", arrow.utcnow().format("YYYY.M.D"))

    @property
    def description(self) -> str:
        description = ""

        # Read Python's pyproject.toml
        if (config := self.path/"pyproject.toml").exists():
            description = (
                toml.loads(config.read_text())
                .get("project", {})
                .get("description", "")
            )

        # Read Rust's Cargo.toml
        elif (config := self.path/"Cargo.toml").exists():
            description = (
                toml.loads(config.read_text())
                .get("package", {})
                .get("description", "")
            )

        return description

    @property
    def languages(self) -> set[ProjectLanguage]:
        languages = set()

        # Best attempts to detect language
        if (self.path/"pyproject.toml").exists():
            languages.add(ProjectLanguage.Python)
        elif (self.path/"Cargo.toml").exists():
            languages.add(ProjectLanguage.Rust)
        elif (self.path/"meson.build").exists():
            languages.add(ProjectLanguage.CPP)
        else:
            languages.add(ProjectLanguage.Unknown)

        return languages

    @property
    def pyproject(self) -> DotMap:
        return DotMap(toml.loads((self.path/"pyproject.toml").read_text()))

    @property
    def cargo_toml(self) -> DotMap:
        return DotMap(toml.loads((self.path/"Cargo.toml").read_text()))

    @property
    def description_pretty_language(self) -> str:
        if self.is_python: return f"🐍 (Python) {self.description}"
        if self.is_rust:   return f"🦀 (Rust  ) {self.description}"
        if self.is_cpp:    return f"🌀 (C/C++ ) {self.description}"
        return self.description

    # Shorthands for project language

    @property
    def is_known(self) -> bool:
        return ProjectLanguage.Unknown not in self.languages

    @property
    def is_python(self) -> bool:
        return ProjectLanguage.Python in self.languages

    @property
    def is_rust(self) -> bool:
        return ProjectLanguage.Rust in self.languages

    @property
    def is_cpp(self) -> bool:
        return ProjectLanguage.CPP in self.languages

    # # Commands

    def update(self, dependencies: bool=True, version: bool=True) -> None:

        # # Dependencies
        if dependencies:
            if self.is_python:
                shell("rye", "lock", "--update-all")
            if self.is_rust:
                shell("cargo", "update")
            if self.is_cpp:
                log.error("C++ projects are not supported yet")

        # # Date
        if version:
            def up_date(file: Path) -> None:
                """Find "version=" line and set it to "version = {date}"", write back to file"""
                if not file.exists(): return
                log.info(f"Updating version of file ({file})")
                file.write_text('\n'.join(
                    [line if not line.startswith("version") else f'version = "{self.version}"'
                    for line in file.read_text().split("\n")]
                ))

            # Update version in all files
            up_date(self.path/"Cargo.toml")
            up_date(self.path/"pyproject.toml")

    def run(self,
        ctx:       Context,
        infinite:  Annotated[bool, Option("--infinite",  help="Press Enter after each run to run again")]=False,
        clear:     Annotated[bool, Option("--clear",     help="Clear terminal before running")]=False,
        debug:     Annotated[bool, Option("--debug",     help="Debug mode for Rust projects")]=False,
    ) -> None:

        while BrokenPlatform.clear_terminal(do=clear, echo=False) or True:
            if self.is_python:
                log.info(f"Hey! Just type '{self.name.lower()}' to run the project with Rye, it's faster 😉")
                return

            if self.is_rust:
                raise RuntimeError(log.error("Rust projects are not supported yet"))
                _status = shell(
                    "cargo", "run",
                    "--bin", self.name,
                    ["--profile", "release"] if not debug else [],
                    "--features", self.rust_features,
                    "--", ctx.args
                )

            if self.is_cpp:
                raise RuntimeError(log.error("C++ projects are not supported yet"))

            if not infinite:
                break

            import rich.prompt
            log.success(f"Project ({self.name}) finished successfully")
            if not rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True):
                break

    # # Python shenanigans

    def release(self,
        target: Annotated[List[BrokenPlatform.Targets], Option("--target", help="Target platform to build for")]=[BrokenPlatform.CurrentTarget],
        torch:  Annotated[bool, Option("--torch", help="Build for all PyTorch flavors")]=False,
    ) -> List[Path]:
        """Release the Project as a distributable binary"""

        # Recurse on all Torch flavors
        if isinstance(torch, bool) and torch:
            for torch_flavor in TorchFlavor:
                self.release(target=target, torch=torch_flavor)
            return

        # Recurse on each target item
        if isinstance(target, list) and True:
            for item in target:
                self.release(target=item, torch=torch)
            return

        # ROCm Windows doesn't exist yet
        if ("windows" in target.name) and (torch == TorchFlavor.ROCM):
            return

        if self.is_python:
            BrokenCLI.rust()
            BrokenTorch.write_flavor(self.path/self.name/"Resources", torch)
            BUILD_DIR = Broken.BROKEN.DIRECTORIES.BROKEN_BUILD

            # Build all path dependencies for a project recursively, return their path
            def convoluted_wheels(path: Path, projects: List[Path]=None) -> List[Path]:
                with BrokenPath.pushd(path := BrokenPath(path)):

                    # Avoid rebuilding the same project or recurse
                    if path not in (projects := projects or list()):
                        log.info(f"Building project at ({path})")
                        projects.append(path)
                    else:
                        return

                    # Load pyproject dictionary
                    pyproject = DotMap(toml.loads((path/"pyproject.toml").read_text()))

                    # Iterate on all dependencies, find only 'path=' ones
                    for name, dependency in pyproject.tool.poetry["dev-dependencies"].items():
                        if isinstance(dependency, str):
                            continue
                        if not dependency.path:
                            continue
                        convoluted_wheels(path=dependency.path, projects=projects)

                    # Remove previous builds
                    BrokenPath.remove(path/"dist")

                    # Build the current project
                    if ("tool.poetry" in pyproject):
                        shell("poetry", "build", "--format", "wheel")
                    else:
                        shell(sys.executable, "-m", "build", "--wheel")

                return projects

            # Build all projects wheels. Main project is the first returned
            path_projects = convoluted_wheels(self.path)
            wheels = [next(project.glob("dist/*.whl")) for project in path_projects]

            # Remove previous build cache for pyapp but no other crate
            for path in BUILD_DIR.rglob("*"):
                if ("pyapp" in path.name):
                    BrokenPath.remove(path)

            # Pyapp configuration
            os.environ.update(dict(
                PYAPP_PROJECT_PATH=str(wheels[0]),
                PYAPP_LOCAL_WHEELS=(";".join(str(x) for x in wheels[1:])),
                PYAPP_EXEC_SPEC=f"{self.name}.__main__:main",
                PYAPP_PYTHON_VERSION="3.11",
                PYAPP_PASS_LOCATION="1",
            ))

            # Cache Rust compilation across projects
            os.environ["CARGO_TARGET_DIR"] = str(BUILD_DIR)
            shell("rustup", "target", "add", target.rust)

            # Build the final binary
            if (_OFFICIAL := False):
                if shell("cargo", "install",
                    "pyapp", "--force",
                    "--root", BUILD_DIR,
                    "--target", target.rust
                ).returncode != 0:
                    log.error("Failed to compile PyAPP")
                    exit(1)
            elif (_FORKED := True):
                with BrokenPath.pushd(Broken.BROKEN.DIRECTORIES.BROKEN_FORK/"PyAPP"):
                    if shell("cargo", "install",
                        "--path", ".",
                        "--force",
                        "--root", BUILD_DIR,
                        "--target", target.rust
                    ).returncode != 0:
                        log.error("Failed to compile PyAPP")
                        exit(1)
            else:
                raise RuntimeError("No Pyapp build method selected")

            # Remove build wheel artifacts
            for project in path_projects:
                BrokenPath.remove(project/"dist")
                BrokenTorch.remove_flavor(project)

            # Find the compiled binary
            binary = next((BUILD_DIR/"bin").glob("pyapp*"))
            log.info(f"Compiled Pyapp binary at ({binary})")
            BrokenPath.make_executable(binary)

            # Rename project binary according to the Broken naming convention
            version = wheels[0].name.split("-")[1]
            release_path = Broken.BROKEN.DIRECTORIES.BROKEN_RELEASES / ''.join((
                f"{self.name.lower()}-",
                (f"{torch.name.lower()}-" if torch else ""),
                f"{target.name}-",
                f"{target.architecture}-",
                f"{version}",
                f"{target.extension}",
            ))
            BrokenPath.remove(release_path)
            binary.rename(release_path)

            # Create a sha265sum file for integrity verification
            sha256sum = BrokenPath.sha256sum(release_path)
            release_path.with_suffix(".sha256").write_text(sha256sum)
            log.info(f"• SHA256: {sha256sum}")
            log.success(f"Built project at ({Broken.BROKEN.DIRECTORIES.BROKEN_RELEASES/release_path})")
            return release_path

# -------------------------------------------------------------------------------------------------|

@define
class BrokenCLI:
    projects:     list[BrokenProjectCLI] = Factory(list)
    broken_typer: BrokenTyper            = None

    def __attrs_post_init__(self) -> None:
        with BrokenSpinner("Finding Projects"):
            self.find_projects(Broken.BROKEN.DIRECTORIES.BROKEN_PROJECTS)
            self.find_projects(Broken.BROKEN.DIRECTORIES.BROKEN_META)

    def find_projects(self, path: Path, *, _depth: int=0) -> None:
        if _depth > 4:
            return
        if not path.exists():
            return

        IGNORED_DIRECTORIES = (".", "_", "modernglw", "workspace", "pyapp")

        for directory in path.iterdir():

            # Avoid hidden directories and workspace
            if any(directory.name.lower().startswith(x) for x in IGNORED_DIRECTORIES):
                continue

            # Must be a directory
            if directory.is_file():
                continue

            # Avoid recursion
            if BrokenPath(directory) == Broken.BROKEN.DIRECTORIES.REPOSITORY:
                continue

            # Resolve symlinks recursively
            if directory.is_symlink() or directory.is_dir():
                self.find_projects(path=BrokenPath(directory), _depth=_depth+1)

            if (project := BrokenProjectCLI(directory)).is_known:
                self.projects.append(project)

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.broken_typer = BrokenTyper(description=(
            "🚀 Broken Source Software Monorepo manager script\n\n"
            "• Tip: run \"broken (command) --help\" for options on commands or projects ✨\n\n"
            "©️ Broken Source Software, AGPL-3.0-only License."
        ))

        with self.broken_typer.panel("📦 Installation"):
            self.broken_typer.command(self.install)
            self.broken_typer.command(self.uninstall)
            self.broken_typer.command(self.submodules, hidden=True)
            self.broken_typer.command(self.shortcut)

        with self.broken_typer.panel("🛡️ Core"):
            self.broken_typer.command(self.clean)
            self.broken_typer.command(self.sync)
            self.broken_typer.command(self.rust)
            self.broken_typer.command(self.link)
            self.broken_typer.command(self.tremeschin, hidden=True)

        with self.broken_typer.panel("⚠️ Experimental"):
            self.broken_typer.command(self.pillow, hidden=True)

        for project in self.projects:
            self.broken_typer.command(
                callable=project.cli,
                name=project.name.lower(),
                help=project.description_pretty_language,
                panel=f"🔥 Projects at [bold]({project.path.parent})[/bold]",
                add_help_option=False,
                hidden=("Projects/Others" in str(project.path)),
            )

        self.broken_typer(sys.argv[1:])

    # ---------------------------------------------------------------------------------------------|
    # Private

    def tremeschin(self):
        for username, repository, name in (
            ("Tremeschin", "GitHub", "Tremeschin"),
            ("Tremeschin", "Archium", "Archium"),
            ("Tremeschin", "Clipyst", "Clipyst"),
        ):
            url  = f"https://github.com/{username}/{repository}"
            path = Broken.BROKEN.DIRECTORIES.BROKEN_PRIVATE/name
            shell("git", "clone", url, path, "--recurse-submodules")

    # ---------------------------------------------------------------------------------------------|
    # Core section

    def clean(self,
        isort: bool=True,
        pycache: bool=True,
        build: bool=False,
        releases: bool=False,
        wheels: bool=False,
        all: bool=False
    ) -> None:
        """🧹 Sorts imports, cleans .pyc files and __pycache__ directories"""
        ROOT = Broken.BROKEN.DIRECTORIES.REPOSITORY

        # Sort imports, ignore "Releases" folder
        if all or isort:
            shell("isort", ROOT,
                "--force-single-line-imports",
                "--skip", ROOT/".venvs",
                "--skip", Broken.BROKEN.DIRECTORIES.BROKEN_RELEASES,
                "--skip", Broken.BROKEN.DIRECTORIES.BROKEN_BUILD,
            )

        # Remove all .pyc files and __pycache__ folders
        if all or pycache:
            for path in ROOT.rglob("__pycache__"):
                BrokenPath.remove(path)
            for path in ROOT.rglob("*.pyc"):
                BrokenPath.remove(path)

        # Remove all .whl files
        if all or wheels:
            for path in ROOT.rglob("*.whl"):
                BrokenPath.remove(path)

        # Remove build and releases folders if requested
        if all or build:    BrokenPath.remove(Broken.BROKEN.DIRECTORIES.BROKEN_BUILD)
        if all or releases: BrokenPath.remove(Broken.BROKEN.DIRECTORIES.BROKEN_RELEASES)

    def link(self, path: Annotated[Path, Argument(help="Path to Symlink under (Projects/Hook/$name) and be added to Broken's CLI")]) -> None:
        """📌 Add a {Directory of Project(s)} to be Managed by Broken"""
        BrokenPath.symlink(virtual=Broken.BROKEN.DIRECTORIES.BROKEN_HOOK/path.name, real=path)

    @staticmethod
    def rust(
        toolchain:   Annotated[str,  Option("--toolchain",   "-t", help="(Any    ) Rust toolchain to use (stable, nightly)")]="stable",
        build_tools: Annotated[bool, Option("--build-tools", "-b", help="(Windows) Install Visual C++ Build Tools")]=True,
    ):
        """🦀 Installs Build Dependencies and a Rust Toolchain"""
        import requests

        # Install rustup based on platform
        if not shutil.which("rustup"):
            log.info("Rustup wasn't found, will install it")
            if BrokenPlatform.OnWindows:
                shell("winget", "install", "-e", "--id", "Rustlang.Rustup")
            elif BrokenPlatform.OnUnix:
                shell("sh", "-c", requests.get("https://sh.rustup.rs").text, "-y", echo=False)

            # If rustup isn't found, ask user to restart shell
            BrokenPath.add_to_path(Path.home()/".cargo"/"bin")

            if not BrokenPath.which("rustup"):
                log.note("Rustup was likely installed but wasn't found adding '~/.cargo/bin' to Path")
                log.note("• Maybe you changed the CARGO_HOME or RUSTUP_HOME environment variables")
                log.note("• Please restart your shell for Rust toolchain to be on PATH")
                exit(0)

        # Install Visual C++ Build Tools on Windows
        if BrokenPlatform.OnWindows and build_tools:
            log.note("You must install Microsoft Visual C++ Build Tools, we will try, else install manually")
            shell((
                'winget install Microsoft.VisualStudio.2022.BuildTools --override '
                '"--wait --passive'
                    ' --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64'
                    ' --add Microsoft.VisualStudio.Component.Windows10SDK'
                    ' --add Microsoft.VisualStudio.Component.Windows11SDK.22000'
                '"'
            ), shell=True)

        class RustToolchain(BrokenEnum):
            Stable  = "stable"
            Nightly = "nightly"

        toolchain = RustToolchain.get(toolchain).value

        # Install or select the correct toolchain
        for line in shell("rustup", "toolchain", "list", output=True, echo=False).split("\n"):
            if ("no installed" in line) or (("default" in line) and (line.split("-")[0] != toolchain)):
                log.info(f"Defaulting Rust toolchain to ({toolchain})")
                shell("rustup", "default", toolchain)
        else:
            log.info(f"Rust toolchain is already the default ({toolchain})")

    def sync(self) -> None:
        """♻️  Synchronize common Resources Files across all Projects"""
        root = Broken.BROKEN.DIRECTORIES.REPOSITORY

        for project in self.projects:
            for file in flatten(
                (root/"poetry.toml"),
                (root/".gitignore"),
                (root/".github"/"Funding.yml"),
                (root/".github"/"ISSUE_TEMPLATE").glob("*.md"),
            ):
                target = project.path/file.relative_to(root)
                BrokenPath.copy(src=file, dst=target)

    # ---------------------------------------------------------------------------------------------|
    # Installation section

    def install(self):
        """➕ Default installation, runs {submodules}, {scripts} and {shortcut if Windows} in sequence"""
        Broken.BROKEN.welcome()
        if BrokenPlatform.OnWindows:
            self.shortcut()
        log.note(f"Running Broken at ({Broken.BROKEN.DIRECTORIES.REPOSITORY})")
        log.note("• Tip: Avoid 'poetry run (broken | project)', prefer 'broken', it's faster 😉")
        log.note("• Tip: Next Time, run 'python ./brakeit.py'" + BrokenPlatform.OnWindows*" or click the Desktop App Icon")
        log.note("• Now run 'broken' for the full command list")
        print()

    LINUX_DESKTOP_FILE = Broken.BROKEN.DIRECTORIES.HOME/".local/share/applications/Brakeit.desktop"

    def shortcut(self):
        """🧭 Creates a Desktop App Shortcut to run the current {brakeit.py}"""
        if BrokenPlatform.OnLinux:
            log.info(f"Creating Desktop file at ({BrokenCLI.LINUX_DESKTOP_FILE})")
            BrokenCLI.LINUX_DESKTOP_FILE.write_text('\n'.join((
                "[Desktop Entry]",
                "Type=Application",
                "Name=Brakeit",
                f"Exec={Broken.BROKEN.DIRECTORIES.BROKEN_BRAKEIT}",
                f"Icon={Broken.BROKEN.RESOURCES.ICON}",
                "Comment=Brakeit Bootstrapper",
                "Terminal=true",
                "Categories=Development",
            )))

        # Workaround: Do not print KeyError of `pyshortcuts.windows.get_conda_active_env`
        elif BrokenPlatform.OnWindows:
            os.environ["CONDA_DEFAULT_ENV"] = "base"
            import pyshortcuts
            pyshortcuts.make_shortcut(
                script=str(Broken.BROKEN.DIRECTORIES.BROKEN_BRAKEIT),
                name="Brakeit",
                description="Broken Source Software Development Environment Entry Script",
                icon=str(Broken.BROKEN.RESOURCES.ICON_ICO),
            )
        else:
            log.error(f"Unknown Platform ({BrokenPlatform.Name})")
            return

    def submodules(self,
        root:     Annotated[Path, Option("--root",     "-r", help="(Basic) Root path to search for Submodules")]=Broken.BROKEN.DIRECTORIES.REPOSITORY,
        auth:     Annotated[bool, Option("--auth",     "-a", help="(Basic) Prompt Username and Password privately for Private clones")]=False,
        username: Annotated[str,  Option("--username", "-u", help="(Auth ) Username to use for git clone")]=None,
        password: Annotated[str,  Option("--password", "-p", help="(Auth ) Password to use for git clone")]=None,
        pull:     Annotated[bool, Option("--pull",           help="(Git  ) Run git pull on all submodules")]=False,
        force:    Annotated[bool, Option("--force",    "-f", help="(Git  ) Force pull (overrides local changes)")]=False,
    ):
        """🔽 Safely init and clone submodules, skip private ones, optional authentication"""

        # --------------------------------------| Pathing

        root = BrokenPath(root)

        # Read .gitmodules if it exists
        if not (gitmodules := root/".gitmodules").exists():
            return

        # Init submodules
        with BrokenPath.pushd(root, echo=False):
            shell("git", "submodule", "init")
            shell("git", "pull", "--quiet", "--force"*force, do=pull)

        # --------------------------------------| Authentication

        # Maybe get username and password from env
        username = os.environ.get("GIT_USERNAME", None)
        password = os.environ.get("GIT_PASSWORD", None)

        # Ask for authentication if requested but not provided yet
        if auth and not (username and password):
            username = username or typer.prompt("Git Username")
            password = password or typer.prompt("Git Password", hide_input=True)

        # Update credentials on env vars (it might have been just prompted)
        os.environ["GIT_USERNAME"] = username or ""
        os.environ["GIT_PASSWORD"] = password or ""

        # `auth` now means if we have credentials
        auth = auth or bool(username and password)

        # --------------------------------------| Reading dot file
        # Read .gitmodules
        import configparser
        config = configparser.ConfigParser()
        config.read(gitmodules)

        # Get all submodules
        for section in config.sections():
            submodule = config[section]

            # Build the absolute path
            path = root/submodule["path"]
            url  = submodule["url"]

            # Skip private submodule
            if submodule.get("private", False) and not auth:
                log.skip(f"Submodule is private ({path})")
                continue

            # Clone with authentication
            url = url.replace("https://", f"https://{username}:{password}@") if auth else url

            # Clone the submodule
            with BrokenPath.pushd(path, echo=False):

                # Fixme: Any better way to check if a submodule is healthy?
                if not list(path.iterdir()):

                    # Set the url to clone this repository with authentication
                    shell("git", "remote", "set-url", "origin", url)

                    # Fetch the submodule's content with the credentials provided
                    if shell("git", "fetch").returncode != 0:
                        log.warning(f"Failed to Fetch Submodule ({path})")
                        log.warning("• You can safely ignore this if you don't need this submodule")
                        log.warning("• You might not have permissions to this repository")
                        log.warning("• You might have provided wrong credentials")
                        continue

                    # Init and update submodule we know we have access to
                    # Switch to main branch, as detached head is clumsy
                    shell("git", "submodule", "update", "--init", path)
                    shell("git", "checkout", "Master")
                    log.success(f"Submodule cloned  ({path})")

                # Pull changes after initial clone
                shell("git", "pull", "--quiet", "--force"*force, do=pull)

            self.submodules(path, username=username, password=password)

    def uninstall(self):
        """➖ Selectively removes Data or Artifacts created by Projects outside of the Repository"""
        log.warning("Selectively Uninstalling Broken Source Convenience and Projects Data")

        if BrokenPlatform.OnLinux and BrokenCLI.LINUX_DESKTOP_FILE.exists():
            log.minor("Now deleting Linux dot Desktop Shortcut file")
            BrokenPath.remove(BrokenCLI.LINUX_DESKTOP_FILE, echo=False, confirm=True)

        # Remove all known projects stuff
        for project in self.projects:
            log.note()
            log.note(f"Project: {project.name}")
            log.note(f"• Path: {project.path}")

            # Follow Project's Workspace folder
            if (workspace := BrokenPath(project.path/"Workspace", valid=True)):
                log.minor("Now removing the Project Workspace directory")
                BrokenPath.remove(workspace, echo=False, confirm=True)

        # Finally, remove the root venv
        if (venv := BrokenPath(Broken.BROKEN.DIRECTORIES.REPOSITORY/".venv", valid=True)):
            log.minor("Now removing the Repository Virtual Environment")
            BrokenPath.remove(venv, echo=False, confirm=True)

    # # Experimental

    def pillow(self):
        """Use Pillow-SIMD for faster Image processing"""
        os.environ["CC"] = "cc -mavx2"
        shell("pip", "install", "-U", "--force-reinstall", "pillow-simd")
