import contextlib
import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, Self

import toml
from attr import Factory, define
from dotmap import DotMap
from typer import Argument, Context, Option

from Broken import (
    BROKEN,
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenProfiler,
    BrokenSingleton,
    BrokenTyper,
    Environment,
    Patch,
    PlatformEnum,
    Runtime,
    SystemEnum,
    Tools,
    __version__,
    combinations,
    flatten,
    log,
    multi_context,
    shell,
)

# ------------------------------------------------------------------------------------------------ #

class ProjectLanguage(BrokenEnum):
    Unknown = "unknown"
    Python  = "python"
    NodeJS  = "nodejs"
    Rust    = "rust"
    CPP     = "cpp"

# ------------------------------------------------------------------------------------------------ #

@define
class ProjectManager:
    path: Path
    name: str = "Unknown"
    cli: BrokenTyper = None

    # # Main entry point

    def main(self, ctx: Context) -> None:
        self.cli = BrokenTyper(help=False)
        self.cli.command(self.update,  help=True)
        self.cli.command(self.compile, help=True)
        self.cli.command(self.run,     help=False, context=True)
        with BrokenPath.pushd(self.path, echo=False):
            self.cli(*ctx.args)

    # # Initialization

    def __attrs_post_init__(self):
        self.name = self.path.name

    def __eq__(self, other: Self) -> bool:
        return self.path == other.path

    # # Utility Attributes

    @property
    def version(self) -> str:
        import arrow
        now = arrow.utcnow().format("YYYY.M.D")
        return self.config.setdefault("version", now)

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
    def _pretty_language(self) -> str:
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
                shell("uv", "lock", "--update-all")
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
                log.info(f"Hey! Just type '{self.name.lower()}' to run the project directly, it's faster 😉")
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
                BUILD_DIR = BROKEN.DIRECTORIES.REPO_BUILD/self.name
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

    def compile(self,
        target: Annotated[list[PlatformEnum],
            Option("--target", "-t",
            help="Target platforms to build binaries for"
        )] = [BrokenPlatform.Host],

        tarball: Annotated[bool,
            Option("--tarball",
            help="Create a compressed tarball archive for unix releases",
        )] = False,

        offline: Annotated[bool,
            Option("--offline",
            help="(Experimental) Create self-contained distributions without internet",
        )] = False,
    ) -> None:
        """
        📦 Release the Project as a distributable binary

        Note:
            - Requires mingw packages for Windows cross compilation from Linux
        """

        # Recurse on each target item
        if isinstance(target, list):
            for target in flatten(map(PlatformEnum.get_all, target)):
                ProjectManager.compile(**locals())
            return None

        # Filter invalid host -> target combinations of all targets
        if BrokenPlatform.OnLinux and (target.system == SystemEnum.MacOS):
            return log.skip(f"Linux can't [italic]easily[/] compile for {target.system}")
        elif BrokenPlatform.OnMacOS and (target.system != SystemEnum.MacOS):
            return log.skip("macOS can only [italic]easily[/] compile for itself")
        elif BrokenPlatform.OnWindows and (target.system != SystemEnum.Windows):
            return log.skip("Windows can only [italic]easily[/] compile for itself")
        elif (target == PlatformEnum.WindowsARM64):
            return log.skip("Windows on ARM is not widely supported")

        # Non-macOS ARM builds can be unstable/not tested, disable on CI
        if (target.arch.is_arm() and (target.system != SystemEnum.MacOS)):
            log.warning("ARM general support is only present in macOS")

        log.note("Building Project Release for", target)

        if self.is_python:
            BrokenManager.rust()
            BUILD_DIR = BROKEN.DIRECTORIES.REPO_BUILD/"Cargo"

            # Remove previous build cache for pyapp
            for path in BUILD_DIR.rglob("pyapp*"):
                BrokenPath.remove(path)

            # Write a releases env config file
            (RELEASE_ENV := BROKEN.RESOURCES.ROOT/"Release.env").write_text('\n'.join(
                f"{key}={value}" for key, value in dict(
                    # Placeholder
                ).items()
            ))

            # Build wheels, find main and extra ones
            WHEELS = BrokenManager().pypi(all=True)
            MAIN   = next(WHEELS.glob("broken_source*"))
            EXTRA  = set(WHEELS.glob("*.whl")) - {MAIN}

            # Pyapp configuration
            os.environ.update(dict(
                PYAPP_PROJECT_PATH=str(MAIN),
                PYAPP_EXTRA_WHEELS=";".join(map(str, EXTRA)),
                PYAPP_EXEC_MODULE=self.name,
                PYAPP_PYTHON_VERSION="3.13",
                PYAPP_PASS_LOCATION="1",
                PYAPP_UV_ENABLED="1",
            ))

            # Rust configuration and fixes
            os.environ.update({key: str(val) for key, val in dict(
                CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=shutil.which("aarch64-linux-gnu-gcc"),
            ).items() if val})

            # Cache Rust compilation across projects
            Environment.set("CARGO_HOME", BUILD_DIR)
            shell("rustup", "target", "add", target.triple)

            # Cargo warning: We're not 'installing' a utility
            BrokenPath.add_to_path(BUILD_DIR/"bin")

            if (_PYAPP_FORK := True):
                if not (fork := BROKEN.DIRECTORIES.REPO_BUILD/"PyApp").exists():
                    shell("git", "clone", "https://github.com/BrokenSource/PyApp", fork, "-b", "custom")

                # Remove previous embeddings if any
                for file in (fork/"src"/"embed").glob("*.whl"):
                    file.unlink()

                # Actually compile it
                if shell(
                    "cargo", "install",
                    "--path", fork, "--force",
                    "--root", BUILD_DIR,
                    "--target", target.triple,
                ).returncode != 0:
                    raise RuntimeError(log.error("Failed to compile PyApp"))
            else:
                if shell(
                    "cargo", "install",
                    "pyapp", "--force",
                    "--root", BUILD_DIR,
                    "--target", target.triple,
                ).returncode != 0:
                    raise RuntimeError(log.error("Failed to compile PyApp"))

            RELEASE_ENV.unlink()

            # Find the compiled binary
            binary = next((BUILD_DIR/"bin").glob("pyapp*"))
            log.info(f"Compiled Pyapp binary at ({binary})")
            BrokenPath.make_executable(binary)

            # Rename the compiled binary to the final release name
            release_path = BROKEN.DIRECTORIES.REPO_RELEASES / ''.join((
                f"{self.name.lower()}",
                f"-{target.value}",
                f"-v{BROKEN.VERSION}",
                f"{target.extension}",
            ))
            BrokenPath.copy(src=binary, dst=release_path)
            BrokenPath.make_executable(release_path)

            # Release a tar.gz to keep chmod +x attributes
            if tarball and ("windows" not in target.name):
                release_path = BrokenPath.gzip(release_path, remove=True)

            log.success(f"Built Project Release at ({release_path})")

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenManager(BrokenSingleton):
    projects: list[ProjectManager] = Factory(list)

    cli: BrokenTyper = Factory(lambda: BrokenTyper(description=(
        "🚀 Broken Source Software Monorepo development manager script\n\n"
        "• Tip: run \"broken (command) --help\" for options on commands or projects ✨\n\n"
    )))

    @property
    def python_projects(self) -> list[ProjectManager]:
        return list(filter(lambda project: project.is_python, self.projects))

    def __attrs_post_init__(self) -> None:
        self.find_projects(BROKEN.DIRECTORIES.REPO_PROJECTS)
        self.find_projects(BROKEN.DIRECTORIES.REPO_META)

        with self.cli.panel("🚀 Core"):
            self.cli.command(self.insiders)
            self.cli.command(self.clone)
            self.cli.command(self.rust)

        with self.cli.panel("📦 Development"):
            self.cli.command(self.compile_all, hidden=True)
            self.cli.command(self.docker)
            self.cli.command(self.website)
            self.cli.command(self.pypi)
            self.cli.command(self.upgrade)
            self.cli.command(self.clean)
            self.cli.command(self.sync)

        self.cli.command(self.tremeschin, hidden=True)

        for project in self.projects:
            self.cli.command(
                target=project.main,
                name=project.name.lower(),
                description=project._pretty_language,
                panel=f"🔥 Projects at [bold]({project.path.parent})[/]",
                hidden=("Projects/Others" in str(project.path)),
                context=True,
                help=False,
            )

    def find_projects(self, path: Path, *, _depth: int=0) -> None:
        if (_depth > 3):
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
            if (project := ProjectManager(directory)).is_known:
                self.projects.append(project)

    # ---------------------------------------------------------------------------------------------|
    # Meta Repositories

    def clone(self,
        repo:     Annotated[str,  Argument(help="URL of the Git Repository to Clone")],
        path:     Annotated[Path, Option("--path",     "-p", help="Path to clone the repository to")]=BROKEN.DIRECTORIES.REPO_META,
        recurse:  Annotated[bool, Option("--recurse",  "-r", help="Clone all submodules recursively")]=True,
        checkout: Annotated[str,  Option("--checkout", "-c", help="Checkout recursively branch or tag")]="main",
    ) -> Path:
        """🔗 Clone a project in the Meta directory"""
        from urllib.parse import urlparse

        # If the path isn't a repo, use the repository name
        if (path.exists()) and (not (Path(path)/".git").exists()):
            log.minor(f"Path {path} isn't a repository, appending the url name")
            path = (path/Path(urlparse(str(repo).removesuffix(".git")).path).stem)

        # Only attempt cloning if non-existent
        if (not path.exists()):
            with BrokenPath.pushd(path.parent, echo=False):
                shell("git", "clone", ("--recurse-submodules"*recurse), repo, path)

        # Not having .git is a failed clone
        if not (path/".git").exists():
            log.error(f"Invalid repository at ({path}), perhaps try removing it")
            exit(1)

        with BrokenPath.pushd(path, echo=False):
            shell("git", "submodule", "foreach", "--recursive", f"git checkout {checkout} || true")

        return path

    def insiders(self):
        """💎 Clone the Insiders repository (WIP, No content)"""
        self.clone("https://github.com/BrokenSource/Insiders", BROKEN.DIRECTORIES.INSIDERS)

    def tremeschin(self):
        Tremeschin = (BROKEN.DIRECTORIES.REPO_META/"Tremeschin")
        self.clone("https://github.com/Tremeschin/Personal", Tremeschin)
        self.clone("https://github.com/Tremeschin/Private",  Tremeschin/"Private")

    # ---------------------------------------------------------------------------------------------|
    # Core section

    def website(self, deploy: Annotated[bool, Option("--deploy", "-d", help="Deploy Unified Website to GitHub Pages")]=False) -> None:
        """📚 Serve or deploy the monorepo website"""
        if deploy:
            Environment.set("CODE_REFERENCE", 1)
            shell("mkdocs", "gh-deploy", "--force")
        else:
            shell("mkdocs", "serve")

    def compile_all(self) -> None:
        for project in self.projects:
            project.compile(
                target=[PlatformEnum._AllHost],
                tarball=True,
            )

    def pypi(self,
        publish: Annotated[bool, Option("--publish", "-p", help="Publish the wheel to PyPI")]=False,
        output:  Annotated[Path, Option("--output",  "-o", help="Output directory for wheels")]=BROKEN.DIRECTORIES.BUILD_WHEELS,
        all:     Annotated[bool, Option("--all",     "-a", help="Build all projects")]=False,
    ) -> Path:
        """🧀 Build all project wheels and publish to PyPI"""
        BrokenPath.recreate(output)
        shell("uv", "build", "--wheel", ("--all"*all), "--out-dir", output)
        shell("uv", "publish", f"{output}/*.whl", skip=(not publish))
        return Path(output)

    def docker(self,
        push:  Annotated[bool, Option("--push",  "-p", help="Push built images to GHCR")]=False,
        clean: Annotated[bool, Option("--clean", "-c", help="Remove local images after pushing")]=False,
    ) -> None:
        """🐳 Build and push docker images for all projects"""
        for build in combinations(
            base_image=["ubuntu:24.04"],
            flavor=["cpu", "cu121"],
        ):
            # Warn: Must use same env vars as in docker-compose.yml
            Environment.set("BASE_IMAGE", build.base_image)
            Environment.set("TORCH_FLAVOR", build.flavor)
            shell("docker", "compose", "build")

            # Assumes all dockerfiles were built by docker compose, fails ok otherwise
            for dockerfile in BROKEN.DIRECTORIES.REPO_DOCKER.glob("*.dockerfile"):
                image:  str = dockerfile.stem
                latest: str = f"{image}:latest"

                # Tag a latest and versioned flavored images, optional push
                for tag in (f"latest-{build.flavor}", f"{__version__}-{build.flavor}"):
                    final: str = f"ghcr.io/brokensource/{image}:{tag}"
                    shell("docker", "tag",  latest, final)
                    shell("docker", "push", final,  skip=(not push))
                    shell("docker", "rmi",  final,  skip=(not clean))

                # No need for generic latest image
                shell("docker", "rmi", latest)

    def upgrade(self) -> None:
        """📦 Temporary solution to bump pyproject versions"""
        import re

        import requests

        def update(
            pyproject: Path,
            data: list[str], *,
            dev: bool=False,
            group: str=None
        ) -> None:
            for dependency in data:
                try:
                    name, compare, version = re.split("(<|<=|!=|==|>=|>|~=|===)", dependency)

                    # Skip Dynamic versions and Equals
                    if (compare == ">=" and version=="0.0.0"):
                        continue
                    if (compare == "=="):
                        continue

                    # Get the latest version of the package on PyPI
                    with contextlib.suppress(KeyError):
                        latest = requests.get(f"https://pypi.org/pypi/{name}/json").json()["info"]["version"]

                        # Update the version in the pyproject.toml
                        pyproject.write_text(
                            pyproject.read_text().replace(
                                f"{name}{compare}{version}",
                                f"{name}{compare}{latest}"
                            )
                        )

                except ValueError:
                    continue

        def manage(path: Path):
            pyproject = (path/"pyproject.toml")
            data = DotMap(toml.loads(pyproject.read_text()))

            update(pyproject, data.project["dependencies"])
            update(pyproject, data.tool.uv["dev-dependencies"], dev=True)

            for (optional, items) in data.project["optional-dependencies"].items():
                update(pyproject, items, group=optional)

        for project in self.python_projects:
            manage(project.path)

        manage(BROKEN.DIRECTORIES.REPOSITORY)
        shell("uv", "sync", "--all-packages")

    @staticmethod
    def rust(
        toolchain:   Annotated[str,  Option("--toolchain",   "-t", help="(Any    ) Rust toolchain to use (stable, nightly)")]="stable",
        build_tools: Annotated[bool, Option("--build-tools", "-b", help="(Windows) Install Visual C++ Build Tools")]=True,
    ):
        """🦀 Installs rustup and a rust toolchain"""
        import requests

        # Actions has its own workflow setup
        if (Runtime.GitHub):
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
        if (BrokenPlatform.OnWindows and build_tools):
            log.warning("You must have Microsoft Visual C++ Build Tools installed to compile Rust projects")
            log.warning("• Broken will try installing it, you might need to restart your shell afterwards")
            shell("winget", "install", "-e", "--id", "Microsoft.VisualStudio.2022.BuildTools", "--override", (
                " --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
                " --add Microsoft.VisualStudio.Component.Windows10SDK"
                " --add Microsoft.VisualStudio.Component.Windows11SDK.22000"
                "--wait --passive"
            ))

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

    def clean(self) -> None:
        """🧹 Remove pycaches, common blob directories"""
        root = BROKEN.DIRECTORIES.REPOSITORY

        for path in root.rglob("__pycache__"):
            BrokenPath.remove(path)

        # Fixed known blob directories
        BrokenPath.remove(BROKEN.DIRECTORIES.REPO_RELEASES)
        BrokenPath.remove(BROKEN.DIRECTORIES.REPO_BUILD)
        BrokenPath.remove(root/".cache")

    def sync(self) -> None:
        """♻️  Synchronize common resources files across all projects"""
        root = BROKEN.DIRECTORIES.REPOSITORY

        for project in self.projects:
            if (project.path/".github"/".nosync").exists():
                continue
            for file in flatten(
                ((root/".github").glob(ext) for ext in ("*.md", "*.yml")),
                (root/".github"/"ISSUE_TEMPLATE").glob("*.yml"),
                (root/".github"/"hatch_build.py"),
            ):
                target = project.path/file.relative_to(root)
                BrokenPath.copy(src=file, dst=target)

# ------------------------------------------------------------------------------------------------ #

def main():
    with BrokenProfiler("BROKEN"):
        BrokenManager().cli(*sys.argv[1:])

if __name__ == "__main__":
    main()
