from __future__ import annotations

from Broken import *


def main():
    BrokenUtils.expand_sys_argv_relative_paths()
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
    broken_typer: typer.Typer = None

    # # Main entry point

    def cli(self, ctx: typer.Context) -> None:
        self.broken_typer = BrokenTyper(help_option=False)
        self.broken_typer.command(self.poetry, add_help_option=False)
        self.broken_typer.command(self.poe,    add_help_option=False)
        self.broken_typer.command(self.update, add_help_option=False)
        self.broken_typer.command(self.run,    add_help_option=False, default=True)
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

    def poetry(self, ctx: typer.Context) -> None:
        """Run poetry command"""
        shell("poetry", *ctx.args)

    def poe(self, ctx: typer.Context) -> None:
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
                log.info(f"Updating version of file [{file}]")
                file.write_text('\n'.join(
                    [line if not line.startswith("version") else f'version = "{self.version}"'
                    for line in file.read_text().split("\n")]
                ))

            # Update version in all files
            up_date(self.path/"Cargo.toml")
            up_date(self.path/"pyproject.toml")

    def run(self,
        ctx:       typer.Context,
        reinstall: Annotated[bool, typer.Option("--reinstall", help="Delete and reinstall Poetry dependencies")]=False,
        infinite:  Annotated[bool, typer.Option("--infinite",  help="Press Enter after each run to run again")]=False,
        clear:     Annotated[bool, typer.Option("--clear",     help="Clear terminal before running")]=False,
        debug:     Annotated[bool, typer.Option("--debug",     help="Debug mode for Rust projects")]=False,
        echo:      Annotated[bool, typer.Option("--echo",      help="Echo command")]=False,
    ) -> None:

        # Set environment variable for the project name
        os.environ["BROKEN_CURRENT_PROJECT_NAME"] = self.name

        # For all arguments in ctx.args, if it's a file, replace it with its path
        # This also fixes files references on the nested poetry command rebasing to its path
        for i, arg in enumerate(ctx.args):
            if (fix := BrokenPath.true_path(arg)).exists():
                ctx.args[i] = fix

        while True:
            BrokenPlatform.clear_terminal(do=clear, echo=False)

            # Python projects
            if self.is_python:
                venv = self.__install_venv__(reinstall=reinstall)
                try:
                    status = shell("poetry", "run", self.name.lower(), ctx.args, echo=echo)
                except KeyboardInterrupt:
                    log.success(f"Project [{self.name}] finished with KeyboardInterrupt")
                    break
                except Exception as e:
                    raise e

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
                log.warning(f"Detected bad return status for the Project [{self.name}]")

                if self.is_python:
                    log.warning(f"- Virtual environment path: [{venv}]")

                # Prompt user for action
                answer = rich.prompt.Prompt.ask(
                    f"• Choose action: (r)einstall venv and retry, (e)xit, (enter) to retry",
                    choices=["r", "e", ""],
                    default="retry"
                )
                if answer == "r":
                    reinstall = True
                elif answer == "retry":
                    pass

            elif infinite:
                log.success(f"Project [{self.name}] finished successfully")
                if not rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True):
                    break

            else:
                break

    # # Python shenanigans

    def __install_venv__(self, reinstall: bool=False) -> Path:
        """Install and get a virtual environment path for Python project"""

        # Unset virtualenv else the nested poetry will use it
        os.environ.pop("VIRTUAL_ENV", None)

        while True:
            venv = shell("poetry", "env", "info", "--path", echo=False, capture_output=True)

            # Virtualenv is not created if command errors or if it's empty
            if (venv.returncode == 1) or (not venv.stdout.strip()):
                log.info(f"Installing virtual environment for {self.name} project")
                shell("poetry", "install")
                continue

            # Get and return virtualenv path
            venv = Path(venv.stdout.decode("utf-8").strip())

            # Reinstall virtualenv if requested
            if reinstall:
                reinstall = False
                BrokenPath.remove(venv)
                BrokenPath.remove(self.path/"poetry.lock")
                continue

            return venv

# -------------------------------------------------------------------------------------------------|

@define
class BrokenCLI:
    projects:     list[BrokenProjectCLI] = field(factory=list)
    directories:  BrokenDirectories      = None
    broken_typer: BrokenTyper            = None

    def __attrs_post_init__(self) -> None:
        self.find_projects(BROKEN.DIRECTORIES.BROKEN_PROJECTS)
        self.find_projects(BROKEN.DIRECTORIES.BROKEN_META)
        self.find_projects(Path.cwd())

    def find_projects(self, path: Path) -> None:
        for directory in path.iterdir():

            if directory.is_file():
                continue

            # Avoid hidden directories
            if any(directory.name.startswith(x) for x in (".", "_")):
                continue

            # Avoid recursion
            if directory == BROKEN.DIRECTORIES.PACKAGE:
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
            "©️  Broken Source Software and its authors, AGPLv3-only License."
        ))

        with self.broken_typer.panel("📦 Installation"):
            self.broken_typer.command(self.install)
            self.broken_typer.command(self.link)
            self.broken_typer.command(self.submodules)

        with self.broken_typer.panel("🛡️ Core"):
            self.broken_typer.command(self.clean)
            self.broken_typer.command(self.updateall)
            self.broken_typer.command(self.release)

        with self.broken_typer.panel("⚠️ Experimental"):
            self.broken_typer.command(self.pillow, hidden=True)
            self.broken_typer.command(self.wheel, hidden=True)

        for project in self.projects:
            self.broken_typer.command(
                callable=project.cli,
                name=project.name.lower(),
                help=project.description_pretty_language,
                panel=f"🔥 Projects at [bold]({project.path.parent})[/bold]",
                add_help_option=False,
            )

        self.broken_typer(sys.argv[1:])

    # # Installation commands

    def submodules(self,
        # Basic
        root: Path=typer.Option(BROKEN.DIRECTORIES.REPOSITORY, "--root", "-r", help="Root path to search for Submodules"),
        auth: bool=typer.Option(False, "--auth", "-a", help="Prompt Username and Password privately for Private clones"),

        # Direct authentication
        username: str=typer.Option(None, "--username", "-u", help="Username to use for git clone"),
        password: str=typer.Option(None, "--password", "-p", help="Password to use for git clone"),

        # Utilities
        pull: bool=typer.Option(False, "--pull", "-P", help="Pull submodules"),
    ):
        """
        Safely init and clone submodules, skip private submodules
        """
        root = BrokenPath.true_path(root)

        # Read .gitmodules if it exists
        if not (gitmodules := root/".gitmodules").exists():
            return

        # Init submodules
        with BrokenPath.pushd(root, echo=False):
            shell("git", "submodule", "init")
            shell("git", "pull", do=pull)

        # Ask credentials
        if auth:
            username = typer.prompt("Git Username")
            password = typer.prompt("Git Password", hide_input=True)

        # Updated if authenticated
        auth = auth or bool(username and password)

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
                log.minor(f"Submodule private ({path})")
                continue

            # Clone with authentication
            url = url.replace("https://", f"https://{username}:{password}@") if auth else url

            # Init and clone the submodules
            if list(path.iterdir()):
                log.info(f"Submodule exists  ({path})")
                self.submodules(root=path, username=username, password=password)
                continue

            # Clone the submodule
            with BrokenPath.pushd(path, echo=False):

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
                shell("git", "pull", do=pull)

                log.success(f"Submodule cloned  ({path})")

            self.submodules(path, username=username, password=password)

    def link(self, path: Path):
        """Brokenfy a Project or Folder of Projects - Be managed by Broken"""
        BrokenPath.symlink(virtual=BROKEN.DIRECTORIES.BROKEN_HOOK/path.name, real=path)

    def install(self):
        self.__scripts__()
        self.__shortcut__()
        log.info("Running Broken at", BROKEN.DIRECTORIES.REPOSITORY)
        log.note(f"Next time, to enter the Broken development environment, run (python ./brakeit) again!")

    def __shortcut__(self):
        if BrokenPlatform.OnUnix:

            # Symlink Broken Shared Directory to current root
            BrokenPath.symlink(virtual=BROKEN.DIRECTORIES.BROKEN_SHARED, real=BROKEN.DIRECTORIES.REPOSITORY)

            # Symlink `brakeit` on local bin and make it executable
            BrokenPath.make_executable(BrokenPath.symlink(
                virtual=BROKEN.DIRECTORIES.HOME/".local/bin/brakeit",
                real=BROKEN.DIRECTORIES.BROKEN_SHARED/"brakeit"
            ))

            # Create Linux .desktop file
            if BrokenPlatform.OnLinux:
                desktop = BROKEN.DIRECTORIES.HOME/".local/share/applications/Broken.desktop"
                desktop.write_text('\n'.join([
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=Broken Shell",
                    f"Exec={BROKEN.DIRECTORIES.BROKEN_SHARED/'brakeit'}",
                    f"Icon={BROKEN.DIRECTORIES.PACKAGE/'Resources'/'Broken.png'}",
                    "Comment=Broken Shell Development Environment",
                    "Terminal=true",
                    "Categories=Development",
                ]))
                log.info(f"Created .desktop file [{desktop}]")

        elif BrokenPlatform.OnWindows:
            log.skip("Shortcut for Windows is not implemented yet")
        else:
            log.error(f"Unknown Platform [{BrokenPlatform.Name}]")
            return

    def __scripts__(self):
        """Creates direct called scripts for every Broken command on venv/bin, [$ broken command -> $ command]"""

        # Get Broken virtualenv path
        folder = "Scripts" if BrokenPlatform.OnWindows else "bin"
        bin_path = BrokenProjectCLI(BROKEN.DIRECTORIES.PACKAGE).__install_venv__()/folder
        log.info(f"Installing scripts on ({bin_path})")

        # Watermark to tag files are Broken made
        WATERMARK = "This file was automatically generated by Broken CLI, do not edit"

        # Remove old script files (commands can be removed or renamed)
        for file in bin_path.glob("*"):
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

    def clean(self,
        isort: bool=True,
        pycache: bool=True,
        build: bool=False,
        releases: bool=False,
        all: bool=False
    ) -> None:
        """Sorts imports, cleans .pyc files and __pycache__ directories"""

        # Sort imports, ignore "Releases" folder
        if all or isort:
            shell("isort", BROKEN.DIRECTORIES.PACKAGE,
                "--force-single-line-imports",
                "--skip", BROKEN.DIRECTORIES.BROKEN_RELEASES,
                "--skip", BROKEN.DIRECTORIES.BROKEN_BUILD,
            )

        # Remove all .pyc files and __pycache__ folders
        if all or pycache:
            delete  = list(BROKEN.DIRECTORIES.PACKAGE.glob("**/*.pyc"))
            delete += list(BROKEN.DIRECTORIES.PACKAGE.glob("**/__pycache__"))

            for path in delete:
                BrokenPath.remove(path)

        # Remove build and releases folders if requested
        if all or build:    BrokenPath.remove(BROKEN.DIRECTORIES.BROKEN_BUILD)
        if all or releases: BrokenPath.remove(BROKEN.DIRECTORIES.BROKEN_RELEASES)

    def updateall(self) -> None:
        """Updates all projects"""
        for project in self.projects:
            project.update()

    def release(self) -> None:
        log.todo("Reimplement release command")

    # # Experimental

    def wheel(self):
        """Builds a Python wheel for Broken"""
        BrokenPath.mkdir(BROKEN.DIRECTORIES.BROKEN_BUILD)
        dist = BrokenPath.resetdir(BROKEN.DIRECTORIES.PACKAGE/"dist")

        # Make Python Wheel
        shell("poetry", "build", "--format", "wheel", f"--directory={BROKEN.DIRECTORIES.BROKEN_BUILD}")

        # Get the wheel file, move to Build dir
        wheel = next(dist.glob("*.whl"))
        wheel = BrokenPath.move(wheel, BROKEN.DIRECTORIES.BROKEN_BUILD/wheel.name)
        BrokenPath.remove(dist)

        log.info(f"Python wheel built at {wheel}")

    def pillow(self):
        """Use Pillow-SIMD. Requires AVX2 CPU and dependencies"""
        shell(PIP, "uninstall", "pillow-simd", "-y")
        os.environ["CC"] = "cc -mavx2"
        shell(PIP, "install", "-U", "--force-reinstall", "pillow-simd")
