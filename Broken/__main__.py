import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, List, Self, Set

import toml
from attr import Factory, define
from dotmap import DotMap
from typer import Argument, Context, Option, Typer

import Broken
from Broken import (
    BROKEN,
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenProfiler,
    BrokenSingleton,
    BrokenTyper,
    Patch,
    Stack,
    TorchFlavor,
    denum,
    flatten,
    log,
    shell,
)


class ProjectLanguage(BrokenEnum):
    Unknown = "unknown"
    Python  = "python"
    NodeJS  = "nodejs"
    Rust    = "rust"
    CPP     = "cpp"

@define
class ProjectCLI:
    path: Path
    name: str = "Unknown"
    typer: Typer = None

    # # Main entry point

    def cli(self, ctx: Context) -> None:
        self.typer = BrokenTyper(help=False)
        self.typer.command(self.update,  help=True)
        self.typer.command(self.release, help=True)
        self.typer.command(self.run,     help=False, context=True)
        with BrokenPath.pushd(self.path, echo=False):
            self.typer(ctx.args)

    # # Initialization

    def __attrs_post_init__(self):
        self.name = self.path.name

    def __eq__(self, other: Self) -> bool:
        return self.path == other.path

    # # Utility Attributes

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
    def languages(self) -> Set[ProjectLanguage]:
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
        if self.is_nodejs: return f"🟢 (NodeJS) {self.description}"
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
    def is_nodejs(self) -> bool:
        return ProjectLanguage.NodeJS in self.languages
    @property
    def is_rust(self) -> bool:
        return ProjectLanguage.Rust in self.languages
    @property
    def is_cpp(self) -> bool:
        return ProjectLanguage.CPP in self.languages

    # # Commands

    def update(self, dependencies: bool=True) -> None:
        """✨ Update this project's dependencies"""
        if dependencies:
            if self.is_python:
                raise NotImplementedError("Standalone Python projects are not supported yet")
                shell("rye", "lock", "--update-all")
            if self.is_nodejs:
                shell("pnpm", "update")
            if self.is_rust:
                shell("cargo", "update")
            if self.is_cpp:
                log.error("C++ projects are not supported yet")

    def run(self, ctx: Context,
        loop:  Annotated[bool, Option("--loop",  help="Press Enter after each run to run again")]=False,
        clear: Annotated[bool, Option("--clear", help="Clear terminal before running")]=False,
        debug: Annotated[bool, Option("--debug", help="Debug mode for Rust projects")]=False,
    ) -> None:
        """🔥 Run this project with all arguments that follow"""

        while True:
            BrokenPlatform.clear_terminal() if clear else None

            if self.is_python:
                log.info(f"Hey! Just type '{self.name.lower()}' to run the project with Rye, it's faster 😉")
                return

            elif self.is_rust:
                raise RuntimeError(log.error("Rust projects are not supported yet"))
                _status = shell(
                    "cargo", "run",
                    "--bin", self.name,
                    ["--profile", "release"] if not debug else [],
                    "--features", self.rust_features,
                    "--", ctx.args
                )

            elif self.is_cpp:
                BUILD_DIR = BROKEN.DIRECTORIES.BROKEN_BUILD/self.name
                if shell("meson", BUILD_DIR, "--reconfigure", "--buildtype", "release").returncode != 0:
                    exit(log.error(f"Could not build project ({self.name})") or 1)
                if shell("ninja", "-C", BUILD_DIR).returncode != 0:
                    exit(log.error(f"Could not build project ({self.name})") or 1)
                binary = next(BUILD_DIR.glob(f"{self.name.lower()}"))
                shell(binary, ctx.args)

            if not loop:
                break

            import rich.prompt
            log.success(f"Project ({self.name}) finished successfully")
            if not rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True):
                break

    # # Python shenanigans

    def release(self,
        target: Annotated[List[BrokenPlatform.Targets], Option("--target", help="Target platform to build for")]=[BrokenPlatform.CurrentTarget],
        torch:  Annotated[bool, Option("--torch", help="Build for all allowed PyTorch flavors in the target platform")]=False,
    ) -> None:
        """
        📦 Release the Project as a distributable binary

        Note:
            - Requires mingw packages for Windows cross compilation from Linux
        """

        # Recurse on all Torch flavors
        if isinstance(torch, bool) and torch:
            for torch in TorchFlavor:
                ProjectCLI.release(**locals())
            return None

        # Recurse on each target item
        if isinstance(target, list) and 1:
            for target in target:
                ProjectCLI.release(**locals())
            return None

        # Avoid bad pytorch combinations (Windows + ROCM) (Non macOS => macOS)
        if (torch) and (torch == TorchFlavor.MACOS) != ("macos"     in target.name): return
        if (torch) and (torch == TorchFlavor.ROCM) and ("linux" not in target.name): return

        if self.is_python:
            BrokenManager.rust()
            BUILD_DIR = BROKEN.DIRECTORIES.BROKEN_BUILD/"Cargo"

            # Remove previous build cache for pyapp but no other crate
            for path in BUILD_DIR.rglob("*"):
                if ("pyapp" in path.name):
                    BrokenPath.remove(path)

            # Write a releases env config file
            (RELEASE_ENV := BROKEN.RESOURCES.ROOT/"Release.env").write_text('\n'.join(
                f"{key}={value}" for key, value in dict(
                    TORCH_FLAVOR=denum(TorchFlavor.get(torch)),
                ).items()
            ))

            # Pyapp configuration
            os.environ.update(dict(
                PYAPP_PROJECT_PATH=str(next(BrokenManager().pypi(_pyapp=True).glob("*.whl"))),
                PYAPP_EXEC_SPEC=f"{self.name}.__main__:main",
                PYAPP_PYTHON_VERSION="3.11",
                PYAPP_PASS_LOCATION="1",
                PYAPP_UV_ENABLED="1",
            ))

            # Cache Rust compilation across projects
            os.environ["CARGO_TARGET_DIR"] = str(BUILD_DIR)
            shell("rustup", "target", "add", target.rust)

            # Cargo warning: We're not 'installing' a utility
            BrokenPath.add_to_path(BUILD_DIR/"bin")

            if shell("cargo", "install",
                "pyapp", "--force",
                "--root", BUILD_DIR,
                "--target", target.rust
            ).returncode != 0:
                log.error("Failed to compile PyAPP")
                exit(1)

            RELEASE_ENV.unlink()

            # Find the compiled binary
            binary = next((BUILD_DIR/"bin").glob("pyapp*"))
            log.info(f"Compiled Pyapp binary at ({binary})")
            BrokenPath.make_executable(binary)

            # Rename project binary according to the Broken naming convention
            for version in ("latest", BROKEN.VERSION):
                release_path = BROKEN.DIRECTORIES.BROKEN_RELEASES / ''.join((
                    f"{self.name.lower()}",
                    f"-{torch.name.lower()}".replace("-macos", "") if torch else "",
                    f"-{target.name}",
                    f"-{target.architecture}",
                    f"-{version}",
                    f"{target.extension}",
                ))
                BrokenPath.copy(src=binary, dst=release_path)
                BrokenPath.make_executable(release_path)
                log.success(f"Built Project Release at ({release_path})")

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenManager(BrokenSingleton):
    projects: list[ProjectCLI] = Factory(list)
    broken_typer: BrokenTyper = None

    @property
    def python_projects(self) -> list[ProjectCLI]:
        return list(filter(lambda project: project.is_python, self.projects))

    def __attrs_post_init__(self) -> None:
        self.find_projects(BROKEN.DIRECTORIES.BROKEN_INSIDERS)
        self.find_projects(BROKEN.DIRECTORIES.BROKEN_PROJECTS)
        self.find_projects(BROKEN.DIRECTORIES.BROKEN_PRIVATE)

    def find_projects(self, path: Path, *, _depth: int=0) -> None:
        if _depth > 1:
            return
        if not path.exists():
            return

        IGNORED_DIRECTORIES = (".", "_", "workspace", "pyapp")

        # Note: Avoid hidden, workspace, recursion
        for directory in path.iterdir():
            if BrokenPath.get(directory) == BROKEN.DIRECTORIES.REPOSITORY:
                continue
            if directory.is_symlink() or directory.is_dir():
                self.find_projects(path=BrokenPath.get(directory), _depth=_depth+1)
            if directory.is_file():
                continue
            if any(directory.name.lower().startswith(x) for x in IGNORED_DIRECTORIES):
                continue
            if (project := ProjectCLI(directory)).is_known:
                self.projects.append(project)

    def cli(self) -> None:
        self.broken_typer = BrokenTyper(description=(
            "🚀 Broken Source Software Monorepo development manager script\n\n"
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
            self.broken_typer.command(self.ryeup, hidden=True)

        with self.broken_typer.panel("🚀 Core"):
            self.broken_typer.command(self.insiders, hidden=True)

        for project in self.projects:
            self.broken_typer.command(
                target=project.cli,
                name=project.name.lower(),
                description=project.description_pretty_language,
                panel=f"🔥 Projects at [bold]({project.path.parent})[reset]",
                hidden=("Projects/Others" in str(project.path)),
                context=True,
                help=False,
            )

        self.broken_typer(sys.argv[1:])

    # ---------------------------------------------------------------------------------------------|
    # Repositories

    def tremeschin(self):
        url, path = ("https://github.com/Tremeschin/Private", BROKEN.DIRECTORIES.BROKEN_PRIVATE)
        shell("git", "clone", url, path, "--recurse-submodules")

    def insiders(self):
        """💎 Clone the Insiders repository (WIP, Not Available)"""
        url, path = ("https://github.com/BrokenSource/Insiders", BROKEN.DIRECTORIES.BROKEN_INSIDERS)
        shell("git", "clone", url, path, "--recurse-submodules")

    # ---------------------------------------------------------------------------------------------|
    # Core section

    def website(self, deploy: Annotated[bool, Option("--deploy", "-d", help="Deploy Unified Website to GitHub Pages")]=False) -> None:
        """📚 Generate or Deploy the Unified Broken Source Software Website"""
        if deploy:
            os.environ.update(CODE_REFERENCE="1")
            shell("mkdocs", "gh-deploy", "--force")
        else:
            shell("mkdocs", "serve")

    def pypi(self,
        publish: Annotated[bool, Option("--publish", "-p", help="Publish the wheel to PyPI")]=False,
        test:    Annotated[bool, Option("--test",    "-t", help="Upload to Test PyPI instead of PyPI")]=False,
        output:  Annotated[Path, Option("--output",  "-o", help="Output directory for wheels")]=BROKEN.DIRECTORIES.BROKEN_WHEELS,
        _pyapp: bool=False,
    ) -> Path:
        """🧀 Build all Projects and Publish to PyPI"""
        from Broken.Version import __version__ as version
        BrokenPath.recreate(output)

        # Files that will be patched
        pyprojects = flatten(
            BROKEN.DIRECTORIES.REPOSITORY/"pyproject.toml",
            (project.path/"pyproject.toml" for project in self.projects),
        )

        # What to temporarily replace
        replaces = {
            "#<pyapp>": ("" if _pyapp else "#"),
            '"Private/': '# "Private/', # Ignore private projects
            '"0.0.0"': f'"{version}"',  # Write current version
            '>=0.0.0': f"=={version}",  # Pin broken projects version
            '~=': '==',                 # Pin dependencies version
        }

        # We patch to include all projects on binary releases
        packages = (("--package", "broken-source") if _pyapp else "--all")

        with Stack(Patch(file=pyproject, replaces=replaces) for pyproject in pyprojects):
            shell("rye", "build", "--wheel", "--out", output, packages)
            shell("rye", "publish", "--yes",
                "--repository", ("testpypi" if test else "pypi"),
                "--token", os.getenv("PYPI_TOKEN"),
                "--username", "__token__",
                f"{output}/*.whl", echo=False,
                skip=(not bool(publish)),
            )

        return Path(output)

    def ryeup(self) -> None:
        """📦 Rye doesn't have a command to bump versions, but (re)adding dependencies does it"""
        import re

        def update(data: List[str], *, dev: bool=False, optional: str=None) -> None:
            for dependency in data:
                try:
                    name, compare, version = re.split("(<|<=|!=|==|>=|>|~=|===)", dependency)

                    # Skip Dynamic versions and Equals
                    if (compare == ">=" and version=="0.0.0"):
                        continue
                    if (compare == "=="):
                        continue

                    shell("rye", "add", "--no-sync", name, "--pin", "~=",
                        "--dev"*dev, ("--optional", optional)*bool(optional))
                except ValueError:
                    continue

        def manage(path: Path):
            with BrokenPath.pushd(path):
                pyproject = DotMap(toml.loads((path/"pyproject.toml").read_text()))
                update(pyproject.project["dependencies"])
                update(pyproject.tool.rye["dev-dependencies"], dev=True)
                for (optional, items) in pyproject.project["optional-dependencies"].items():
                    update(items, optional=optional)

        for project in filter(lambda project: project.is_python, self.projects):
            manage(project.path)

        manage(BROKEN.DIRECTORIES.REPOSITORY)
        shell("rye", "sync")

    @staticmethod
    def rust(
        toolchain:   Annotated[str,  Option("--toolchain",   "-t", help="(Any    ) Rust toolchain to use (stable, nightly)")]="stable",
        build_tools: Annotated[bool, Option("--build-tools", "-b", help="(Windows) Install Visual C++ Build Tools")]=True,
    ):
        """🦀 Installs Rustup and a Rust Toolchain"""
        import requests

        # Skip if we're on a GitHub Action
        if (Broken.GITHUB_CI):
            return

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


    def link(self, path: Annotated[Path, Argument(help="Path to Symlink under (Projects/Hook/$name) and be added to Broken's CLI")]) -> None:
        """📌 Add a {Directory of Project(s)} to be Managed by Broken"""
        BrokenPath.symlink(virtual=BROKEN.DIRECTORIES.BROKEN_HOOK/path.name, real=path)

    def sync(self) -> None:
        """♻️  Synchronize common Resources Files across all Projects"""
        root = BROKEN.DIRECTORIES.REPOSITORY

        for project in self.projects:
            for file in flatten(
                ((root/".github").glob(ext) for ext in ("*.md", "*.yml")),
                (root/".github"/"ISSUE_TEMPLATE").glob("*.yml"),
            ):
                target = project.path/file.relative_to(root)
                BrokenPath.copy(src=file, dst=target)

# ------------------------------------------------------------------------------------------------ #

def main():
    with BrokenProfiler("BROKEN"):
        broken = BrokenManager()
        broken.cli()

if __name__ == "__main__":
    main()
