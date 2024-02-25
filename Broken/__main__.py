from __future__ import annotations

from Broken import *


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
    broken_typer: TyperApp = None

    # # Main entry point

    def cli(self, ctx: TyperContext) -> None:
        self.broken_typer = BrokenTyper(help_option=False)
        self.broken_typer.command(self.poetry,  add_help_option=False)
        self.broken_typer.command(self.poe,     add_help_option=True)
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
        return self.config.setdefault("version", arrow.utcnow().format("YYYY.M.D"))

    @property
    def description(self) -> str:
        description = ""

        # Read Python's pyproject.toml
        if (config := self.path/"pyproject.toml").exists():
            description = (
                toml.loads(config.read_text())
                .get("tool", {})
                .get("poetry", {})
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

    def poetry(self, ctx: TyperContext) -> None:
        """Run poetry command"""
        shell("poetry", *ctx.args)

    def poe(self, ctx: TyperContext) -> None:
        """Run poethepoet command"""
        shell("poe", *ctx.args)

    def update(self, dependencies: bool=True, version: bool=True) -> None:

        # # Dependencies
        if dependencies:
            if self.is_python:
                shell("poetry", "update")
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
        ctx:       TyperContext,
        reinstall: Annotated[bool, TyperOption("--reinstall", help="Delete and reinstall Poetry dependencies")]=False,
        infinite:  Annotated[bool, TyperOption("--infinite",  help="Press Enter after each run to run again")]=False,
        clear:     Annotated[bool, TyperOption("--clear",     help="Clear terminal before running")]=False,
        debug:     Annotated[bool, TyperOption("--debug",     help="Debug mode for Rust projects")]=False,
        echo:      Annotated[bool, TyperOption("--echo",      help="Echo command")]=False,
    ) -> None:

        while True:
            BrokenPlatform.clear_terminal(do=clear, echo=False)

            # Python projects
            if self.is_python:
                venv = self.get_virtualenv(reinstall=reinstall)
                try:
                    status = shell(
                        (venv/BrokenPlatform.PyScripts/("main"+BrokenPlatform.PyScriptExtension)),
                        ctx.args, echo=echo
                    )
                except KeyboardInterrupt:
                    log.success(f"Project ({self.name}) finished with KeyboardInterrupt")
                    break
                except FileNotFoundError:
                    log.warning(f"Potential partial installation detected for the Project ({self.name}), a installation retry is recommended {{(r) option}}")
                    status = DotMap(returncode=1, args=ctx.args)

            # Rust projects
            if self.is_rust:
                status = shell(
                    "cargo", "run",
                    "--bin", self.name,
                    ["--profile", "release"] if not debug else [],
                    "--features", self.rust_features,
                    "--", ctx.args
                )

            # C++ projects
            if self.is_cpp:
                log.error("C++ projects are not supported yet")

            # Avoid reinstalling on future runs
            reinstall = False

            # Detect bad return status, reinstall virtualenv and retry once
            if (status.returncode != 0) and (not reinstall):
                log.warning(f"Detected bad Return Status ({status.returncode}) for the Project ({self.name}) at ({self.path})")
                if self.is_python:
                    log.warning(f"• Python Virtual Environment: ({venv})")
                log.warning(f"• Arguments: {tuple(status.args)}", echo=bool(status.args))

                # Prompt user for action
                import rich.prompt
                answer = rich.prompt.Prompt.ask(
                    "• Action: Run {poetry (i)nstall}, {poetry (l)ock}, {(r)einstall venv}, {(e)xit} or {(enter) nothing}, then retry",
                    choices=["r", "e", "p", "l", ""],
                    default="retry"
                )
                if answer == "r":
                    reinstall = True
                elif answer == "e":
                    break
                elif answer == "i":
                    shell("poetry", "install")
                elif answer == "l":
                    shell("poetry", "lock")
                elif answer == "retry":
                    pass

            elif infinite:
                import rich.prompt
                log.success(f"Project ({self.name}) finished successfully")
                if not rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True):
                    break

            else:
                break

    # # Python shenanigans

    def get_virtualenv(self, install: bool=True, reinstall: bool=False) -> Optional[Path]:
        """Install and get a virtual environment path for Python project"""

        # Unset virtualenv else the nested poetry will use it
        old_venv = BrokenPath(os.environ.pop("VIRTUAL_ENV", None))

        with BrokenPath.pushd(self.path, echo=False):
            while True:
                venv = shell("poetry", "env", "info", "--path", echo=False, capture_output=True)

                # Install if virtualenv is not found
                if (venv.returncode != 0):
                    if install:
                        log.info(f"Installing virtual environment for Project ({self.name})")
                        shell("poetry", "install")
                    else:
                        log.minor(f"Virtual environment doesn't exist for Project ({self.name})")
                        return None
                    continue

                # Convert to Path
                venv_path = Path(venv.stdout.decode().strip())

                if not install:
                    log.info(f"Found virtual environment for Project at ({venv_path})")
                    return venv_path

                # Reinstall virtualenv if requested
                if reinstall:
                    reinstall = False
                    BrokenPath.remove(venv_path)
                    BrokenPath.remove(self.path/"poetry.lock")
                    continue

                # Optimization: Direct symlink to the main script (bypasses poetry run and Broken)
                if BrokenPlatform.OnLinux and (old_venv is not None):
                    direct = f"{self.name.lower()}er"
                    log.note(f"• Tip: For faster startup times but less integration, you can run $ {direct}")
                    BrokenPath.symlink(
                        virtual=(old_venv/BrokenPlatform.PyScripts/direct),
                        real=(venv_path/BrokenPlatform.PyScripts/"main"),
                    )

                return venv_path

    def release(self,
        target: Annotated[BrokenPlatform.Targets, TyperOption("--target", "-t", help="Target platform to build for")]=BrokenPlatform.CurrentTarget,
    ):
        """Release the Project as a distributable binary"""
        if self.is_python:
            BrokenCLI.rust()

            # Build all path dependencies for a project recursively, return their path
            def convoluted_wheels(path: Path, projects: List[Path]=None) -> List[Path]:
                with BrokenPath.pushd(path := BrokenPath(path)):
                    log.info(f"Building project at ({path})")

                    # Initialize empty set and add current project
                    projects = projects or list()
                    if path in projects:
                        return
                    projects.append(path)

                    # Load pyproject dictionary
                    pyproject = DotMap(toml.loads((path/"pyproject.toml").read_text()))

                    # Iterate on all path dependencies
                    for name, dependency in pyproject.tool.poetry["dev-dependencies"].items():

                        # Find only path= dependencies
                        if isinstance(dependency, str):
                            continue
                        if not dependency.path:
                            continue

                        # Recurse on the other project
                        convoluted_wheels(path=dependency.path, projects=projects)

                    # Remove previous builds
                    BrokenPath.remove(path/"dist")

                    # Hack: Move all built wheels to the Resources folder
                    if self.path == path:
                        log.info(f"Moving wheels to Resources folder")
                        for wheel in [next(project.glob("dist/*.whl")) for project in projects[1:]]:
                            BrokenPath.copy(src=wheel, dst=BrokenPath.remove(self.path/self.name/"Resources"/"Wheels")/wheel.name)

                    # Build the current project
                    shell("poetry", "build", "--format", "wheel")

                return projects

            # Build all projects wheels. Main project is the first returned
            wheels = [next(project.glob("dist/*.whl")) for project in convoluted_wheels(self.path)]

            for i, wheel in enumerate(wheels):
                log.info(f"{i}: Using project wheel at ({wheel})")

            # Pyapp configuration
            os.environ.update(dict(
                PYAPP_PROJECT_PATH=str(wheels[0]),
                PYAPP_EXEC_SPEC=f"{self.name}.__main__:main",
                PYAPP_PYTHON_VERSION="3.11",
                PYAPP_PASS_LOCATION="1",
            ))

            # Remove previous build cache for pyapp but no other crate
            for path in [x for x in BROKEN.DIRECTORIES.BROKEN_BUILD.glob("**") if "pyapp" in x.name]:
                BrokenPath.remove(path)

            # Cache Rust compilation across projects
            os.environ["CARGO_TARGET_DIR"] = str(BROKEN.DIRECTORIES.BROKEN_BUILD)

            # Build the final binary
            shell("cargo", "install", "pyapp", "--force", "--root", BROKEN.DIRECTORIES.BROKEN_BUILD)
            binary = next((BROKEN.DIRECTORIES.BROKEN_BUILD/"bin").glob("pyapp*"))
            log.info(f"Compiled Pyapp binary at ({binary})")
            BrokenPath.make_executable(binary)

            # Remove build wheel artifacts
            for wheel in wheels:
                BrokenPath.remove(wheel.parent)
            BrokenPath.remove(self.path/self.name/"Resources"/"Wheels")

            # Rename project binary according to the Broken naming convention
            version = wheels[0].name.split("-")[1]
            release_name = BROKEN.DIRECTORIES.BROKEN_RELEASES / (
                f"{self.name.lower()}-"
                f"{BrokenPlatform.Name}-"
                f"{BrokenPlatform.Architecture}-"
                f"{version}"
                f"{BrokenPlatform.Extension}"
            )
            BrokenPath.remove(release_name)
            binary.rename(release_name)

            # Create a sha265sum file for integrity verification
            sha256sum = BrokenUtils.sha256sum(release_name)
            release_name.with_suffix(".sha256").write_text(sha256sum)
            log.info(f"Release SHA256: {sha256sum}")

            log.success(f"Built project at ({BROKEN.DIRECTORIES.BROKEN_RELEASES/release_name})")

# -------------------------------------------------------------------------------------------------|

@define
class BrokenCLI:
    projects:     list[BrokenProjectCLI] = Factory(list)
    directories:  BrokenDirectories      = None
    broken_typer: BrokenTyper            = None

    def __attrs_post_init__(self) -> None:
        with Halo(text="Finding Projects"):
            self.find_projects(BROKEN.DIRECTORIES.BROKEN_PROJECTS)
            self.find_projects(BROKEN.DIRECTORIES.BROKEN_META)

    def find_projects(self, path: Path) -> None:
        for directory in path.iterdir():

            # Don't follow workspace
            if (directory.name.lower() == "workspace"):
                break

            # Avoid hidden directories
            if any(directory.name.startswith(x) for x in (".", "_")):
                continue

            # Must be a directory
            if directory.is_file():
                continue

            directory = BrokenPath(directory)

            # Avoid recursion
            if directory == BROKEN.DIRECTORIES.REPOSITORY:
                continue

            # Resolve symlinks recursively
            if directory.is_symlink() or directory.is_dir():
                self.find_projects(path=directory.resolve())

            if (project := BrokenProjectCLI(directory)).is_known:
                self.projects.append(project)

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.broken_typer = BrokenTyper(description=(
            "🚀 Broken Source Software Monorepo manager script\n\n"
            "• Tip: run \"broken (command) --help\" for options on commands or projects ✨\n\n"
            "©️ Broken Source Software, AGPLv3-only License."
        ))

        with self.broken_typer.panel("📦 Installation"):
            self.broken_typer.command(self.install)
            self.broken_typer.command(self.uninstall)
            self.broken_typer.command(self.submodules)
            self.broken_typer.command(self.scripts)
            self.broken_typer.command(self.shortcut)

        with self.broken_typer.panel("🛡️ Core"):
            self.broken_typer.command(self.clean)
            self.broken_typer.command(self.sync)
            self.broken_typer.command(self.rust)
            self.broken_typer.command(self.link)
            self.broken_typer.command(self.mock, hidden=True)

        with self.broken_typer.panel("⚠️ Experimental"):
            self.broken_typer.command(self.pillow, hidden=True)

        for project in self.projects:
            self.broken_typer.command(
                callable=project.cli,
                name=project.name.lower(),
                help=project.description_pretty_language,
                panel=f"🔥 Projects at [bold]({project.path.parent})[/bold]",
                add_help_option=False,
            )

        self.broken_typer(sys.argv[1:])

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

        # Sort imports, ignore "Releases" folder
        if all or isort:
            shell("isort", BROKEN.DIRECTORIES.REPOSITORY,
                "--force-single-line-imports",
                "--skip", BROKEN.DIRECTORIES.REPOSITORY/".venvs",
                "--skip", BROKEN.DIRECTORIES.BROKEN_RELEASES,
                "--skip", BROKEN.DIRECTORIES.BROKEN_BUILD,
            )

        # Remove all .pyc files and __pycache__ folders
        if all or pycache:
            delete  = list(BROKEN.DIRECTORIES.REPOSITORY.glob("**/*.pyc"))
            delete += list(BROKEN.DIRECTORIES.REPOSITORY.glob("**/__pycache__"))
            for path in delete:
                BrokenPath.remove(path)

        # Remove all .whl files
        if all or wheels:
            delete = list(BROKEN.DIRECTORIES.REPOSITORY.glob("**/*.whl"))
            for path in delete:
                BrokenPath.remove(path)

        # Remove build and releases folders if requested
        if all or build:    BrokenPath.remove(BROKEN.DIRECTORIES.BROKEN_BUILD)
        if all or releases: BrokenPath.remove(BROKEN.DIRECTORIES.BROKEN_RELEASES)

    def link(self, path: Path):
        """📌 Link a {Directory} or {Directory of Projects} to be Managed by Broken"""
        BrokenPath.symlink(virtual=BROKEN.DIRECTORIES.BROKEN_HOOK/path.name, real=path)

    @staticmethod
    def rust(
        toolchain:   Annotated[str,  TyperOption("--toolchain",   "-t", help="(Any    ) Rust toolchain to use (stable, nightly)")]="stable",
        build_tools: Annotated[bool, TyperOption("--build-tools", "-b", help="(Windows) Install Visual C++ Build Tools")]=True,
    ):
        """🦀 Installs Build Dependencies and a Rust Toolchain"""

        # Install rustup based on platform
        if not shutil.which("rustup"):
            if BrokenPlatform.OnWindows:
                shell("winget", "install", "-e", "--id", "Rustlang.Rustup")
            elif BrokenPlatform.OnUnix:
                shell("sh", "-c", requests.get("https://sh.rustup.rs").text, "-y", echo=False)
            log.note(f"Please restart your shell for Rust toolchain to be on PATH")
            log.note(f"• If this didn't work, have rustup available externally")
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
        root = BROKEN.DIRECTORIES.REPOSITORY

        for project in self.projects:
            for file in BrokenUtils.flatten(
                (root/"poetry.toml"),
                (root/".gitignore"),
                (root/".github"/"Funding.yml"),
                (root/".github"/"ISSUE_TEMPLATE").glob("*.md"),
            ):
                target = project.path/file.relative_to(root)
                BrokenPath.copy(src=file, dst=target)

        # Brakeit on the Website
        BrokenPath.copy(root/"brakeit.py", BROKEN.DIRECTORIES.WEBSITE/"public"/"get.py")

    # ---------------------------------------------------------------------------------------------|
    # Installation section

    def install(self):
        """➕ Default installation, runs {submodules}, {scripts} and {shortcut if Windows} in sequence"""
        BROKEN.welcome()
        self.submodules()
        self.scripts()
        if BrokenPlatform.OnWindows:
            self.shortcut()
        log.note(f"Running BrokenSource Monorepo at directory ({BROKEN.DIRECTORIES.REPOSITORY})")
        log.note("• Tip: To enter the Development Environment again, run {python ./brakeit.py}" + BrokenPlatform.OnWindows*" or click the Desktop App Icon")
        log.note("• Tip: Avoid {poetry run (broken | project)}, prefer {broken}, it's faster 😉")
        log.note("• Now run {broken} for the full command list")
        print()

    def scripts(self):
        """⚡️ Write short scripts for starting Projects, ($ broken command -> $ command)"""

        # Get Broken virtualenv path
        bin_path = Path(os.environ["VIRTUAL_ENV"])/BrokenPlatform.PyScripts
        log.info(f"Installing scripts on ({bin_path})")

        # Watermark to tag files are Broken made
        WATERMARK = "This file was automatically generated by Broken CLI, do not edit"

        # Remove old script files (commands can be removed or renamed)
        for file in bin_path.glob("*"):
            if file.is_symlink():
                continue
            try:
                if WATERMARK in file.read_text():
                    BrokenPath.remove(file, echo=False)
            except UnicodeDecodeError:
                pass
            except Exception as e:
                raise e

        for project in self.projects:
            script = bin_path/project.lname

            if BrokenPlatform.OnUnix:
                script.write_text('\n'.join([
                    f"#!/bin/bash",
                    f"# {WATERMARK}",
                    f"broken {project.lname} $@",
                ]))

            elif BrokenPlatform.OnWindows:
                script = script.with_suffix(".bat")
                script.write_text('\n'.join([
                    f"@echo off",
                    f":: {WATERMARK}",
                    f"broken {project.lname} %*",
                ]))

            BrokenPath.make_executable(script, echo=False)

    LINUX_DESKTOP_FILE = BROKEN.DIRECTORIES.HOME/".local/share/applications/Broken.desktop"

    def shortcut(self):
        """🧿 Creates a Desktop App Shortcut to run the current {brakeit.py}"""
        if BrokenPlatform.OnUnix:
            if BrokenPlatform.OnLinux:
                log.info(f"Creating Desktop file at ({BrokenCLI.LINUX_DESKTOP_FILE})")
                BrokenCLI.LINUX_DESKTOP_FILE.write_text('\n'.join((
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=Brakeit",
                    f"Exec={BROKEN.DIRECTORIES.BROKEN_BRAKEIT}",
                    f"Icon={BROKEN.RESOURCES.ICON}",
                    "Comment=Brakeit Bootstrapper",
                    "Terminal=true",
                    "Categories=Development",
                )))

        # Workaround: Do not print KeyError of `pyshortcuts.windows.get_conda_active_env`
        elif BrokenPlatform.OnWindows:
            os.environ["CONDA_DEFAULT_ENV"] = "base"
            import pyshortcuts
            pyshortcuts.make_shortcut(
                script=str(BROKEN.DIRECTORIES.BROKEN_BRAKEIT),
                name="Brakeit",
                description="Broken Source Software Development Environment Entry Script",
                icon=str(BROKEN.RESOURCES.ICON_ICO),
            )
        else:
            log.error(f"Unknown Platform ({BrokenPlatform.Name})")
            return

    def submodules(self,
        root:     Annotated[Path, TyperOption("--root",     "-r", help="(Basic ) Root path to search for Submodules")]=BROKEN.DIRECTORIES.REPOSITORY,
        auth:     Annotated[bool, TyperOption("--auth",     "-a", help="(Basic ) Prompt Username and Password privately for Private clones")]=False,
        username: Annotated[str,  TyperOption("--username", "-u", help="(Auth  ) Username to use for git clone")]=None,
        password: Annotated[str,  TyperOption("--password", "-p", help="(Auth  ) Password to use for git clone")]=None,
        pull:     Annotated[bool, TyperOption("--pull",           help="(Git   ) Run git pull on all submodules")]=False,
        force:    Annotated[bool, TyperOption("--force",    "-f", help="(Git   ) Force pull (overrides local changes)")]=False,
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
                    shell("git", "submodule", "update", "--init", path)

                    # Checkout main branch, as detached head is clumsy
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

            if (venv := project.get_virtualenv(install=False)):
                log.minor("Now removing the Poetry's Python Virtual environment")
                BrokenPath.remove(venv, echo=False, confirm=True)

            # Follow Project's Workspace folder
            if (workspace := BrokenPath(project.path/"Workspace", valid=True)):
                log.minor("Now removing the Project Workspace directory")
                BrokenPath.remove(workspace, echo=False, confirm=True)

    # # Experimental

    def pillow(self):
        """Use Pillow-SIMD for faster Image processing"""
        os.environ["CC"] = f"cc -mavx2"
        shell("pip", "install", "-U", "--force-reinstall", "pillow-simd")

    def mock(self):
        import Broken.Mock
