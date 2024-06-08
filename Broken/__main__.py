from __future__ import annotations

import contextlib
import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, Generator, List, Self

import click
import toml
from attr import Factory, define
from dotmap import DotMap
from loguru import logger as log
from typer import Argument, Context, Option, Typer

import Broken
from Broken import (
    BROKEN,
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenProfiler,
    BrokenTorch,
    BrokenTyper,
    TorchFlavor,
    denum,
    flatten,
    shell,
)


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

        # We should only target MACOS flavor for MacOS
        if (torch == TorchFlavor.MACOS) and ("macos" not in target.name):
            return

        if self.is_python:
            BrokenCLI.rust()
            BUILD_DIR = Broken.BROKEN.DIRECTORIES.BROKEN_BUILD/"Rust"

            # Build the monorepo wheel, which includes all projects
            with BrokenPath.pushd(Broken.BROKEN.DIRECTORIES.REPOSITORY):
                wheel = BrokenCLI.pypi()

            # Remove previous build cache for pyapp but no other crate
            for path in BUILD_DIR.rglob("*"):
                if ("pyapp" in path.name):
                    BrokenPath.remove(path)

            # Pyapp configuration
            os.environ.update(dict(
                PYAPP_PROJECT_PATH=str(wheel),
                PYAPP_EXEC_SPEC=f"{self.name}.__main__:main",
                PYAPP_PYTHON_VERSION="3.11",
                PYAPP_PASS_LOCATION="1",
                PYAPP_UV_ENABLED="1",
                # Fixme (#pyapp): De-spaghetti when we can send env vars
                PYAPP_SELF_COMMAND=denum(TorchFlavor.get(torch)) or "self",
            ))

            # Cache Rust compilation across projects
            os.environ["CARGO_TARGET_DIR"] = str(BUILD_DIR)
            shell("rustup", "target", "add", target.rust)

            # We're not 'installing' a utility, remove warning
            BrokenPath.add_to_path(BUILD_DIR/"bin")

            # Build the final binary
            if shell("cargo", "install",
                "pyapp", "--force",
                "--root", BUILD_DIR,
                "--target", target.rust
            ).returncode != 0:
                log.error("Failed to compile PyAPP")
                exit(1)

            # Find the compiled binary
            binary = next((BUILD_DIR/"bin").glob("pyapp*"))
            log.info(f"Compiled Pyapp binary at ({binary})")
            BrokenPath.make_executable(binary)

            # Rename project binary according to the Broken naming convention
            for version in ("latest", wheel.name.split("-")[1]):
                release_path = Broken.BROKEN.DIRECTORIES.BROKEN_RELEASES / ''.join((
                    f"{self.name.lower()}-",
                    (f"{torch.name.lower()}-" if torch else ""),
                    f"{target.name}-",
                    f"{target.architecture}-",
                    f"{version}",
                    f"{target.extension}",
                ))
                BrokenPath.copy(src=binary, dst=release_path)
                log.success(f"Built Project Release at ({release_path})")

            return release_path

# -------------------------------------------------------------------------------------------------|

@define
class BrokenCLI:
    projects:     list[BrokenProjectCLI] = Factory(list)
    broken_typer: BrokenTyper            = None

    def __attrs_post_init__(self) -> None:
        self.find_projects(Broken.BROKEN.DIRECTORIES.BROKEN_PROJECTS)
        self.find_projects(Broken.BROKEN.DIRECTORIES.BROKEN_META)

    def find_projects(self, path: Path, *, _depth: int=0) -> None:
        if _depth > 4:
            return
        if not path.exists():
            return

        IGNORED_DIRECTORIES = (".", "_", "modernglw", "workspace", "pyapp")

        for directory in path.iterdir():

            # Avoid hidden, workspace, recursion
            if any(directory.name.lower().startswith(x) for x in IGNORED_DIRECTORIES):
                continue
            if directory.is_file():
                continue
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
            "©️ Broken Source Software, AGPL-3.0 License"
        ))

        with self.broken_typer.panel("📦 Development"):
            self.broken_typer.command(self.website)
            self.broken_typer.command(self.pypi)
            self.broken_typer.command(self.sync)
            self.broken_typer.command(self.rust)
            self.broken_typer.command(self.link)
            self.broken_typer.command(self.tremeschin, hidden=True)
            self.broken_typer.command(self.ryedeps, hidden=True)

        for project in self.projects:
            self.broken_typer.command(
                target=project.cli,
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

    def ryedeps(self) -> None:
        """📦 Rye doesn't have a command to bump versions, but (re)adding dependencies does it"""
        import re

        pyproject = DotMap(toml.loads((BROKEN.DIRECTORIES.REPOSITORY/"pyproject.toml").read_text()))

        def update_dependencies(data: List[str], *, dev: bool=False, optional: str=None) -> None:
            for dependency in data:
                name, compare, version = re.split("(<|<=|!=|==|>=|>|~=|===)", dependency)
                if (compare == "=="):
                    continue
                shell("rye", "add", name, "--dev"*dev, ["--optional", optional] if optional else None, "--no-sync")

        update_dependencies(pyproject.project.dependencies)
        update_dependencies(pyproject.tool.rye["dev-dependencies"], dev=True)
        for (optional, items) in pyproject.project["optional-dependencies"].items():
            update_dependencies(items, optional=optional)
        shell("rye", "sync")

    def website(self, deploy: Annotated[bool, Option("--deploy", "-d", help="Deploy Unified Website to GitHub Pages")]=False) -> None:
        """📚 Generate or Deploy the Unified Broken Source Software Website"""
        GITHUB_PAGE = "git@github.com:BrokenSource/brokensource.github.io.git"
        if deploy:
            shell("mkdocs", "gh-deploy", "--force", "--remote-name", GITHUB_PAGE)
        else:
            shell("mkdocs", "serve")

    @staticmethod
    def pypi(
        publish: Annotated[bool, Option("--publish", "-p", help="Publish the wheel to PyPI")]=False,
        test:    Annotated[bool, Option("--test",    "-t", help="Upload to TestPyPI")]=False,
    ) -> Path:
        """🧀 Build all Projects and Publish to PyPI"""
        DIR = BrokenPath.resetdir(Broken.BROKEN.DIRECTORIES.BROKEN_WHEELS)
        shell("rye", "build", "--wheel", "--out", DIR)
        wheel = next(DIR.glob("*.whl"))

        if publish:
            if (not click.confirm(f"• Confirm publishing wheel ({wheel})")):
                return
            shell(
                "rye", "publish",
                "--repository", ("testpypi" if test else "pypi"),
                "--username", os.environ.get("PYPI_USERNAME"),
                "--token", os.environ.get("PYPI_TOKEN"),
                wheel,
                echo=False
            )

        return wheel

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
                log.warning("Rustup was likely installed but wasn't found adding '~/.cargo/bin' to Path")
                log.warning("• Maybe you changed the CARGO_HOME or RUSTUP_HOME environment variables")
                log.warning("• Please restart your shell for Rust toolchain to be on PATH")
                exit(0)

        # Install Visual C++ Build Tools on Windows
        if BrokenPlatform.OnWindows and build_tools:
            log.warning("You must install Microsoft Visual C++ Build Tools, we will try, else install manually")
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
                (root/".github"/"funding.yml"),
                (root/".github"/"ISSUE_TEMPLATE").glob("*.md"),
            ):
                target = project.path/file.relative_to(root)
                BrokenPath.copy(src=file, dst=target)

# -------------------------------------------------------------------------------------------------|

def main():
    with BrokenProfiler("BROKEN"):
        broken = BrokenCLI()
        broken.cli()

if __name__ == "__main__":
    main()
