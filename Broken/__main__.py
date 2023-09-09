from Broken import *

# -------------------------------------------------------------------------------------------------|

find = lambda name: BrokenPath.get_binary(name, echo=False)

# Find binaries absolute path
PYTHON      = sys.executable
POETRY      = [PYTHON, "-m", "poetry"]
PIP         = [PYTHON, "-m", "pip"]
NUITKA      = [PYTHON, "-m", "nuitka"]
PYINSTALLER = find("pyinstaller")
BASH        = find("bash") if (not BrokenPlatform.OnWindows) else None
WINETRICKS  = find("winetricks")
PACMAN      = find("pacman")
RUSTUP      = find("rustup")
CARGO       = find("cargo")
CHMOD       = find("chmod")
SUDO        = find("sudo")
WINE        = find("wine")
APT         = find("apt")
GIT         = find("git")
UPX         = find("upx")

# Development tools
ISORT   = find("isort")
PYCLEAN = find("pyclean")

# -------------------------------------------------------------------------------------------------|
# Releases related

# Rust toolchain ("nightly" or "stable")
RUSTUP_TOOLCHAIN = os.environ.get("RUSTUP_TOOLCHAIN", "stable")

class ProjectsEnumerator(Enum):
    """List of runnable projects Broken finds. Is dynamically extended"""
    ...

class ProjectLanguage:
    """The programming language of a project"""
    Python  = "python"
    Rust    = "rust"
    CPP     = "cpp"
    Unknown = "unknown"

# FIXME: How to merge with BrokenPlatform?
class ReleasePlatform(Enum):
    """List of common platforms targets for releases"""
    LinuxAMD64   = "linux-amd64"
    LinuxARM     = "linux-arm"
    WindowsAMD64 = "windows-amd64"
    WindowsARM   = "windows-arm"
    MacOSAMD64   = "macos-amd64"
    MacOSARM     = "macos-arm"

# -------------------------------------------------------------------------------------------------|

ABOUT = f"""
🚀 Broken Source Software manager script\n
• Tip: run "broken (command) --help" for options on commands or projects ✨

©️  2022-2023 Broken Source Software and its authors, AGPLv3-only License.
"""

class BrokenCLI:
    # Cargo.toml's required-features as ["--features", "default" ? "feature1,feature2"]
    RustProjectFeatures = {}

    # dict["depthflow"] -> "DepthFlow"
    ProjectsInfo = {}

    def __init__(self) -> None:
        # Mono repository directories for Broken CLI script
        self.RELEASES_DIR       = BROKEN_MONOREPO_DIR/"Release"
        self.PROJECTS_DIR       = BROKEN_MONOREPO_DIR/"Projects"
        self.ASSETS_DIR         = BROKEN_MONOREPO_DIR/"Assets"
        self.BUILD_DIR          = BROKEN_MONOREPO_DIR/"Build"
        self.DOCS_DIR           = BROKEN_MONOREPO_DIR/"Docs"
        self.TEMPLATES_DIR      = BROKEN_MONOREPO_DIR/"Templates"

        # Nested directories
        self.OTHER_PROJECTS_DIR = self.PROJECTS_DIR/"Hook"
        self.WINEPREFIX         = self.BUILD_DIR/"Wineprefix"

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.typer_app = BrokenBase.typer_app(description=ABOUT)

        # Add projects commands
        self.add_run_projects_commands()

        # Section: Installation
        emoji = "📦"
        self.typer_app.command(rich_help_panel=f"{emoji} Installation")(self.install)
        self.typer_app.command(rich_help_panel=f"{emoji} Installation")(self.requirements)
        self.typer_app.command(rich_help_panel=f"{emoji} Installation")(self.scripts)
        self.typer_app.command(rich_help_panel=f"{emoji} Installation")(self.link)

        # Section: Miscellaneous
        emoji = "🛡️ "
        self.typer_app.command(rich_help_panel=f"{emoji} Core")(self.date)
        self.typer_app.command(rich_help_panel=f"{emoji} Core", hidden=True)(self.hooks)
        self.typer_app.command(rich_help_panel=f"{emoji} Core")(self.update)
        self.typer_app.command(rich_help_panel=f"{emoji} Core")(self.clean)
        self.typer_app.command(rich_help_panel=f"{emoji} Core")(self.release)

        # Section: Experimental
        emoji = "⚠️ "
        self.typer_app.command(rich_help_panel=f"{emoji} Experimental")(self.pillow_simd)
        self.typer_app.command(rich_help_panel=f"{emoji} Experimental")(self.wheel)

        # Execute the CLI
        self.typer_app()

    # # Experimental

    def wheel(self):
        """Builds a Python wheel for Broken"""
        BrokenPath.mkdir(self.BUILD_DIR)
        dist = BrokenPath.resetdir(BROKEN_MONOREPO_DIR/"dist")

        # Make Python Wheel
        shell(POETRY, "build", "--format", "wheel", f"--directory={self.BUILD_DIR}")

        # Get the wheel file, move to Build dir
        wheel = next(dist.glob("*.whl"))
        wheel = BrokenPath.move(wheel, self.BUILD_DIR/wheel.name)
        BrokenPath.remove(dist)

        log.info(f"Python wheel built at {wheel}")

    def link(self, path: Path):
        """Links some Project Path or Folder of Projects to also be managed by Broken"""
        BrokenPath.symlink(self.OTHER_PROJECTS_DIR/path.name, path)

    def pillow_simd(self):
        """
        Installs Pillow-SIMD, a way faster Pillow fork, does not change poetry dependencies. Requires AVX2 CPU, and dependencies installed
        """
        shell(PIP, "uninstall", "pillow-simd", "-y")
        os.environ["CC"] = "cc -mavx2"
        shell(PIP, "install", "-U", "--force-reinstall", "pillow-simd")

    ## Adding Commands

    def __get_install_python_virtualenvironment(self,
        project_name: str,
        project_path: PathLike,
        reinstall: bool=False,
    ) -> Path:
        """Get the virtual environment path for a Python project"""

        with BrokenPath.pushd(project_path):

            # Unset virtualenv else the nested poetry will use it
            os.environ.pop("VIRTUAL_ENV", None)

            while True:
                venv = shell(POETRY + ["env", "info", "--path"], echo=False, capture_output=True, cwd=project_path)

                # Virtualenv is not created if command errors or if it's empty
                if (venv.returncode == 1) or (not venv.stdout.strip()):
                    log.info(f"Installing virtual environment for {project_name} project")
                    shell(POETRY, "install", cwd=project_path)
                    continue

                # Get and return virtualenv path
                venv_path = Path(venv.stdout.decode("utf-8").strip())

                # Reinstall virtualenv if requested
                if reinstall:
                    reinstall = False
                    BrokenPath.remove(venv_path)
                    BrokenPath.remove(project_path/"poetry.lock")
                    continue
                return venv_path

    def get_project_language(self, path: Path, echo=True) -> ProjectLanguage:
        """
        Get the programming language of a project
        # Fixme: this could be done smartly (like a Broken.toml file)
        """
        if (path/"pyproject.toml").exists():
            log.info(f"Project [{path}] is a Python project", echo=echo)
            return ProjectLanguage.Python
        elif (path/"Main.rs").exists() and (path.name in BrokenCLI.RustProjectFeatures):
            log.info(f"Project [{path}] is a Rust project", echo=echo)
            return ProjectLanguage.Rust
        elif (path/"meson.build").exists():
            log.info(f"Project [{path}] is a C++ project", echo=echo)
            return ProjectLanguage.CPP
        else:
            log.error(f"Unknown project language for [{path}]", echo=echo)
            return ProjectLanguage.Unknown

    def add_project_command(self, name: str, path: PathLike, language: ProjectLanguage) -> None:
        """Add a command to run a project on self.typer_app"""

        # A very weird @wraps() decorator to keep local strings and return a function that runs the project
        def run_project_template(name, path, language):
            def run_project(
                ctx: typer.Context,
                reinstall: Annotated[bool, typer.Option("--reinstall", help="Delete and reinstall Poetry dependencies")]=False,
                infinite: Annotated[bool, typer.Option("--infinite", help="Press Enter after each run to run again")]=False,
                clear: Annotated[bool, typer.Option("--clear", help="Clear terminal before running")]=False,
                debug: Annotated[bool, typer.Option("--debug", help="Debug mode for Rust projects")]=False,
            ):
                # Route for Python projects
                if language == ProjectLanguage.Python:

                    # For all arguments in ctx.args, if it's a file, replace it with its path
                    # This also fixes files references on the nested poetry command rebasing to its path
                    for i, arg in enumerate(ctx.args):
                        if (fix := BrokenPath.true_path(arg)).exists():
                            ctx.args[i] = fix

                    # Set env vars for Broken
                    os.environ["BROKEN_CURRENT_PROJECT_NAME"] = name

                    # Optionally clear terminal
                    shell("clear" if BrokenPlatform.OnUnix else "cls", do=clear, echo=False)

                    # Maybe install or reinstall virtualenv, run project, get status
                    project_venv = self.__get_install_python_virtualenvironment(name, path, reinstall=reinstall)
                    status = shell(POETRY, "run", name.lower(), ctx.args, cwd=path)

                    # Detect bad return status, reinstall virtualenv and retry once
                    if (status.returncode != 0) and (not reinstall):
                        log.warning(f"Detected bad return status for the Project [{name}], maybe a broken virtual environment or some exception?")
                        log.warning(f"- Virtual environment path: [{project_venv}]")

                        answer = rich.prompt.Prompt.ask(
                            f"• Choose action: (r)einstall venv and retry, (e)xit, (enter) to retry",
                            choices=["r", "e", ""],
                            default="retry"
                        )
                        if answer == "r":
                            BrokenUtils.recurse(run_project, reinstall=True)
                        elif answer == "retry":
                            BrokenUtils.recurse(run_project)

                    elif infinite:
                        log.success(f"Detected Project [{name}] finished running successfully")
                        rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True)
                        reinstall = False
                        BrokenUtils.recurse(run_project)

                # Route for Rust projects
                elif language == ProjectLanguage.Rust:
                    self.install_rust()
                    release = ["--profile", "release"] if not debug else []
                    shell(CARGO, "run", "--bin", name, "--features", BrokenCLI.RustProjectFeatures[name], release, "--", ctx.args)

                # Route for C++ projects
                elif language == ProjectLanguage.CPP:
                    with BrokenPath.pushd(path):
                        shell("meson", "setup", self.BUILD_DIR/name)
                        shell("meson", "compile", "-C", self.BUILD_DIR/name)
                        shell(self.BUILD_DIR/name/name, ctx.args)

            return run_project

        # Get the base parent path of the project (might be folder of projects), resolve symlinks
        base_path = path.resolve().parent.absolute()

        # Start with unknown project description
        description = "···"

        # Get project description from config files based on language
        # Fixme: Broken.toml specification would be nice
        if language == ProjectLanguage.Python:
            if (config := path/"pyproject.toml").exists():
                description = (
                    toml.loads(config.read_text())
                    .get("tool", {})
                    .get("poetry", {})
                    .get("description", description)
                )

        elif language == ProjectLanguage.Rust:
            if (config := path/"Cargo.toml").exists():
                description = (
                    toml.loads(config.read_text())
                    .get("package", {})
                    .get("description", description)
                )

        elif language == ProjectLanguage.CPP:
            # Experimental C++ because I ain't good enough in Rust yet
            # (I'm terrible at C++ also, but memory unsafe is easier to code lol)
            ...

        else:
            # TODO: Any standard on what Broken.toml might contain?
            if (config := path/"Broken.toml").exists():
                description = (
                    toml.loads(config.read_text())
                    .get("description", description)
                )

        # Add project's mascot to description
        if   language == ProjectLanguage.Python: description = f"🐍 (Python) {description}"
        elif language == ProjectLanguage.Rust:   description = f"🦀 (Rust  ) {description}"
        elif language == ProjectLanguage.CPP:    description = f"🌀 (C/C++ ) {description}"

        # Create Typer command
        self.typer_app.command(
            name=name.lower(),
            help=description,
            rich_help_panel=f"🔥 Projects at [bold]({base_path})[/bold]",

            # Catch extra (unknown to typer) arguments that are sent to Python
            context_settings=dict(allow_extra_args=True, ignore_unknown_options=True),

            # Projects implement their own --help
            add_help_option=False,

        )(run_project_template(name, path, language))

    # TODO: Will I ever have projects in other languages?
    def add_run_projects_commands(self, echo=False) -> None:
        self.cargo_toml = DotMap(toml.loads((BROKEN_MONOREPO_DIR/"Cargo.toml").read_text()))

        # Build Rust required features
        for rust_project in self.cargo_toml["bin"]:
            BrokenCLI.RustProjectFeatures[rust_project.get("name")] = ','.join(rust_project.get("required-features", ["default"]))

        def check_directory(path: Path):

            # Search every subdirectories for pyproject.toml or Main.rs
            for sub in path.glob("**/*"):

                # Avoid recursion
                if sub == BROKEN_MONOREPO_DIR:
                    continue

                # Resolve symlinks recursively
                if sub.is_symlink():
                    return check_directory(sub.resolve().absolute())

                # Might have non-project files
                if not sub.is_dir():
                    continue

                # Empty dir might be a bare submodule
                if not list(sub.iterdir()):
                    continue

                # Project programming language
                language = self.get_project_language(sub, echo=False)

                # Skip unknown projects
                if language == ProjectLanguage.Unknown:
                    continue

                # Get project name and translate lowercase to real name
                name = sub.name
                BrokenCLI.ProjectsInfo[name.lower()] = DotMap(
                    name=name,
                    path=sub,
                    language=language,
                )

                # Add project command
                self.add_project_command(name=name, path=sub, language=language)

                # Add attribute to the enumerator ProjectsEnumerator
                if name.lower() not in ProjectsEnumerator.__members__:
                    aenum.extend_enum(ProjectsEnumerator, name.lower(), name.lower())

        # Check all projects directories
        check_directory(self.PROJECTS_DIR)

    # NOTE: Also returns date string
    def date(self) -> str:
        """Set current UTC dates on all Cargo.toml and pyproject.toml for known projects"""
        date = arrow.utcnow().format("YYYY.M.D")
        log.info(f"Current UTC date is [{date}]")

        # Find "version=" line and set it to "version = {date}"", write back to file
        def update_date(file: Path) -> None:
            if not file.exists(): return
            log.info(f"Updating date of file [{file}]")
            file.write_text('\n'.join(
                [line if not line.startswith("version") else f'version = "{date}"'
                for line in file.read_text().split("\n")]
            ))

        for path in self.PROJECTS_DIR.glob("**/*"):

            # Might have non-project files
            if not path.is_dir():
                continue

            # Update common files
            update_date(path/"pyproject.toml")
            update_date(path/"Cargo.toml")

        # Broken
        update_date(BROKEN_MONOREPO_DIR/"pyproject.toml")
        update_date(BROKEN_MONOREPO_DIR/"Cargo.toml")

        # Update poetry.lock
        shell(POETRY, "install")

        return date

    # # Commands section

    def hooks(self) -> None:
        """Use all Git hooks under the folder Broken/Hooks"""

        # Make all hooks executable
        for file in (BROKEN_MONOREPO_DIR/"Broken/Hooks").iterdir():
            shell(CHMOD, "+x", file)

        # Set git hooks path to Broken/Hooks
        shell(GIT, "config", "core.hooksPath", "./Broken/Hooks")

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
            shell(ISORT, BROKEN_MONOREPO_DIR,
                "--force-single-line-imports",
                "--skip", self.RELEASES_DIR,
                "--skip", self.BUILD_DIR,
            )

        # Remove all .pyc files and __pycache__ folders
        if all or pycache:
            for path in list(BROKEN_MONOREPO_DIR.glob("**/*.pyc")) + list(BROKEN_MONOREPO_DIR.glob("**/__pycache__")):
                if any([ignore in path.parents for ignore in (self.RELEASES_DIR, self.BUILD_DIR)]):
                    continue
                BrokenPath.remove(path)

        # Remove build and releases folders if requested
        if all or build:    BrokenPath.remove(self.BUILD_DIR)
        if all or releases: BrokenPath.remove(self.RELEASES_DIR)

    # Install Rust toolchain on macOS, Linux
    def install_rust(self) -> None:

        # Install rustup for toolchains
        if not all([BrokenPath.get_binary(binary) is not None for binary in ["rustup", "rustc", "cargo"]]):
            log.info(f"Installing Rustup default profile")

            # Get rustup link for each platform
            if BrokenPlatform.OnWindows: rust_installer = "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-gnu/rustup-init.exe"
            elif BrokenPlatform.OnUnix:  rust_installer = "https://sh.rustup.rs"

            # Download and install Rust
            with BrokenDownloads.download(rust_installer) as installer:
                shell(BASH, installer, "--profile", "default", "-y")
                log.fixme(f"Please run the last command again or restart terminal or Rust binaries won't be found")
                exit(0)

        # Detect if default Rust toolchain installed is the one specified in RUSTUP_TOOLCHAIN
        for line in shell(RUSTUP, "toolchain", "list", output=True, echo=False).split("\n"):
            if ("no installed" in line) or (("default" in line) and (line.split("-")[0] != RUSTUP_TOOLCHAIN)):
                log.info(f"Defaulting Rust toolchain to [{RUSTUP_TOOLCHAIN}]")
                shell(RUSTUP, "default", RUSTUP_TOOLCHAIN)

    def install(self, linux_desktop_file: bool=True, scripts: bool=True) -> None:
        """Symlinks current directory to Broken Shared Directory for sharing code in External projects, makes `broken` command available anywhere by adding current folder to PATH, creates .desktop file on Linux"""
        log.fixme("Do you need to install Broken for multiple users? If so, please open an issue on GitHub.")

        # Create direct project scripts
        self.add_run_projects_commands()

        # Symlink Broken Shared Directory to Broken Root
        if BrokenPlatform.OnUnix:
            # BROKEN_SHARED_DIRECTORY might already be a symlink to BROKEN_ROOT
            if not Path(BROKEN_SHARED_DIR).resolve() == BROKEN_MONOREPO_DIR:
                log.info(f"Creating symlink [{BROKEN_SHARED_DIR}] -> [{BROKEN_MONOREPO_DIR}]")
                shell("sudo", "ln", "-snf", BROKEN_MONOREPO_DIR, BROKEN_SHARED_DIR)

            # Create .desktop file
            if linux_desktop_file:
                desktop = HOME_DIR/".local/share/applications/Broken.desktop"
                desktop.write_text('\n'.join([
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=Broken Shell",
                    f"Exec={BROKEN_SHARED_DIR/'brakeit'}",
                    f"Icon={self.ASSETS_DIR/'Default'/'Icon.png'}",
                    "Comment=Broken Shell Development Environment",
                    "Terminal=true",
                    "Categories=Development",
                ]))
                log.success(f"Created .desktop file [{desktop}]")

        elif BrokenPlatform.OnWindows:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                log.warning("Windows symlink requires admin privileges on current shell, please open an admin PowerShell/CMD and run [  broken install] again")
                return
            BrokenPath.remove(BROKEN_SHARED_DIR, confirm=True)
            Path(BROKEN_SHARED_DIR).symlink_to(BROKEN_MONOREPO_DIR, target_is_directory=True)
        else: log.error(f"Unknown Platform [{BrokenPlatform.Name}]"); return

        log.success(f"Symlink created [{BROKEN_SHARED_DIR}] -> [{BROKEN_MONOREPO_DIR}]")

        # Add Broken Shared Directory to PATH
        ShellCraft.add_path_to_system_PATH(BROKEN_SHARED_DIR)

        if scripts:
            self.scripts()

    def scripts(self):
        """Creates direct called scripts for every Broken command on venv/bin, [$ broken command -> $ command]"""

        # Get Broken virtualenv path
        bin_path = self.__get_install_python_virtualenvironment("Broken", BROKEN_MONOREPO_DIR)/"bin"

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

        # For each internal command
        for command in self.typer_app.registered_commands:

            # No typer.command(name=str)(...) given
            if command.name is None:
                continue

            log.info(f"Creating script for command [{command.name}]")
            script = bin_path/command.name

            if BrokenPlatform.OnUnix:
                script.write_text('\n'.join([
                    f"#!/bin/bash",
                    f"# {WATERMARK}",
                    f"broken {command.name} $@",
                ]))
                BrokenPath.make_executable(script, echo=False)
            elif BrokenPlatform.OnWindows:
                script.write_text('\n'.join([
                    f"@echo off",
                    f":: {WATERMARK}",
                    f"broken {command.name} %*",
                ]))

    def update(self,
        rust: bool=False,
        python: bool=False,
        repos: bool=False,
        all: bool=False,
    ):
        """Updates Cargo and Python dependencies, Rust language toolchain and Poetry"""
        if not any([rust, python, repos, all]):
            log.error("Please specify what to update see [broken update --help]")
            return

        # Update Rust
        if all or rust:
            self.install_rust()
            shell(CARGO, "update")
            shell(RUSTUP, "update")

        # Update Python
        if all or python:

            # Main repository dependencies
            shell(POETRY, "update")

            # All Python projects dependencies
            for project in self.PROJECTS_DIR.iterdir():
                if (project/"pyproject.toml").exists():
                    log.info(f"Updating Python dependencies for Project [{project.name}]")
                    os.environ.pop("VIRTUAL_ENV", None)
                    shell(POETRY, "update", cwd=project)

        # Update Git Repositories
        if all or repos:
            shell(GIT, "submodule", "update", "--init", "--recursive")

    def release(self,
        project: ProjectsEnumerator,
        platform: ReleasePlatform,
        nuitka: Annotated[bool, typer.Option("--nuitka", "-n", help="(Python) Use Nuitka than Pyinstaller for builds - experimental")]=False,
    ):
        """Builds and releases a project for a specific platform"""

        # Get info on the project
        project = BrokenCLI.ProjectsInfo.get(project.value.lower())

        # Find project's programming language
        language = self.get_project_language(path=project.path)

        # Update dates and create releases directory
        date = self.date()
        BrokenPath.mkdir(self.RELEASES_DIR)
        BrokenPath.mkdir(self.BUILD_DIR)

        # Get info based on target platform
        (rust_target_triple, compiled_extension, release_extension) = {
            # Linux
            ReleasePlatform.LinuxAMD64:   ("x86_64-unknown-linux-gnu",  "",     ".bin"),
            ReleasePlatform.LinuxARM:     ("aarch64-unknown-linux-gnu", "",     ".bin"),

            # Windows
            ReleasePlatform.WindowsAMD64: ("x86_64-pc-windows-gnu",     ".exe", ".exe"),

            # FIXME: MacOS Requires Xcode, can we crosscompile from Linux? Do not care for AMD64?
            ReleasePlatform.MacOSAMD64:   ("x86_64-apple-darwin",       "",     ".bin"),
            ReleasePlatform.MacOSARM:     ("aarch64-apple-darwin",      "",     ".bin"),
        }.get(platform)

        # -----------------------------------------------------------------------------------------|

        if language == ProjectLanguage.Python:

            # "python3.11.4", "python3.11", for example
            vi = sys.version_info
            python_version_installer_url = f"{vi.major}.{vi.minor}.{vi.micro}"
            python_version_site_packages = f"{vi.major}.{vi.minor}"

            # Cross compilation bootstrap for Windows from Linux
            if (BrokenPlatform.OnLinux) and (platform == ReleasePlatform.WindowsAMD64):
                log.warning("wine-staging as of version 8.11 fails creating and installing the virtual environments in poetry")

                # Wine called binaries
                WINE_PYTHON = [WINE, "python.exe"]
                WINE_PIP    = [WINE_PYTHON, "-m", "pip"]
                WINE_POETRY = [WINE_PYTHON, "-m", "poetry"]

                # Set Wineprefix
                os.environ["WINEPREFIX"] = str(self.WINEPREFIX)
                os.environ["WINEARCH"]   = "win64"
                os.environ["WINEDEBUG"]  = "-all"

                # Download and install Python for Windows
                python_installer_url = f"https://www.python.org/ftp/python/{python_version_installer_url}/python-{python_version_installer_url}-amd64.exe"

                # Set to Windows 10 version (Python can't be installed for <= 8)
                shell(WINETRICKS, "win10", "-q")

                # Install Python, add to path
                with BrokenDownloads.download(python_installer_url) as python_installer:
                    shell(WINE, python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1")

                # Install Broken dependencies and create virtualenv
                shell(WINE_PIP, "install", "--upgrade", "pip", "wheel")
                shell(WINE_PIP, "install", "--upgrade", "poetry")
                shell(WINE_POETRY, "install")

                # Inception: Run this function but from Wine Python
                os.environ.pop("VIRTUAL_ENV", None)
                shell(WINE_POETRY, "run", "broken", "release", project.name.lower(), platform.value, "--nuitka" if nuitka else "")
                return

            # Create install virtualenv dependencies
            project.venv = self.__get_install_python_virtualenvironment(project.name, project.path)

            # Find site_packages of the project's virtualenv
            project.site_packages = project.venv/"lib"/f"python{python_version_site_packages}"/"site-packages"

            # Use the project's virtualenv site-packages
            os.environ["PYTHONPATH"] = str(project.site_packages)
            log.info(f"Using site-packages at [{project.site_packages}]")

            # Find common project assets
            def get_project_asset_file_or_default(relative_path: Path) -> Path:
                if (target := self.ASSETS_DIR/project.name/relative_path).exists():
                    return target
                return self.ASSETS_DIR/"Default"/relative_path

            # Torch fixes not including metadata
            torch_fixes = [
                ("--copy-metadata", package)
                for package in "tqdm torch regex sacremoses requests packaging filelock numpy tokenizers importlib_metadata".split()
                if (target := project.site_packages/package).exists()
            ]

            # Use the project's virtualenv site-packages
            if (BrokenPlatform.OnLinux):
                lib_name = "libglfw.so"
                log.fixme(f"Applying [{lib_name}] workaround for Pyinstaller, is it on any other path than /usr/lib?")
                try:
                    lib = next(Path("/usr/lib").glob(f"**/{lib_name}"))
                    log.success(f"Found [{lib_name}] at [{lib}]")
                    os.environ["PYGLFW_LIBRARY"] = str(lib)
                except StopIteration:
                    log.error(f"[{lib_name}] not found on /usr/lib, ModernGL projects might fail")

            # Compile the Python project with Pyinstaller
            if not nuitka:
                shell(PYINSTALLER,

                    # Where and how to build
                    "--workpath", self.BUILD_DIR,
                    "--onefile",
                    # "--clean",
                    "--noconfirm",
                    # "--strip",
                    "--console",

                    # Hidden imports that may contain binaries
                    "--hidden-import", "imageio_ffmpeg",
                    "--hidden-import", "glcontext",
                    "--hidden-import", "glfw",
                    # "--hidden-import", "torch",

                    # Torch fixes
                    torch_fixes,

                    # Where to put the binary and its name
                    f"--distpath={self.RELEASES_DIR}",
                    f"--specpath={self.BUILD_DIR}",
                    "-n", project.name,

                    # Use the project's virtualenv site-packages just in case
                    "--paths", project.site_packages,

                    # Branding: Icon and splash screen
                    "--splash", get_project_asset_file_or_default("Splash.png"),
                    "--icon", get_project_asset_file_or_default("Icon.ico"),

                    # Target file to compile
                    project.path/project.name/"__main__.py",
                )

                # Path of the compiled binary
                compiled_binary = self.RELEASES_DIR/f"{project.name}{compiled_extension}"


            # Compile the Python project with Nuitka
            if nuitka:
                shell(NUITKA,
                    # Basic options
                    "--standalone",
                    "--onefile",
                    "--lto=yes",
                    "--assume-yes-for-downloads",

                    # FFmpeg Binaries
                    "--include-package-data=imageio_ffmpeg",

                    # "--onefile-tempdir-spec=%CACHE_DIR%/%COMPANY%/%PRODUCT%/%VERSION%"
                    f"--onefile-tempdir-spec=%CACHE_DIR%/BrokenSource/{project.name}-{date}",

                    # Binary metadata
                    f"--company-name='Broken Source Software'",
                    f"--product-name='{project.name}'",
                    f"--file-version={date}",
                    f"--product-version={date}",

                    # Output options
                    f"--output-filename={project.name}",
                    f"--output-dir={self.RELEASES_DIR}",

                    # Note: We don't target __main__ else nuitka won't "find the __init__ and as a package"
                    self.PROJECTS_DIR/project.name/project.name,
                )

                # Path of the compiled binary
                compiled_binary = self.RELEASES_DIR/f"{project.name}"

        # -----------------------------------------------------------------------------------------|

        elif language == ProjectLanguage.Rust:
            self.install_rust()
            rust_profile = "ultra"

            # Fix Fortran compiler for Windows cross compilation netlib for ndarray-linalg package
            if (BrokenPlatform == "linux") and (platform == "windows-amd64"):
                log.note("Fixing Fortran compilation for Windows cross compilation")
                os.environ["FC"] = "x86_64-w64-mingw32-gfortran"

            # Add target toolchain for Rust
            shell(RUSTUP, "target", "add", rust_target_triple)
            rust_required_features = BrokenCLI.RustProjectFeatures[project.name]

            # Build the binary
            shell(CARGO, "build",
                "--bin", project.name,
                "--target", rust_target_triple,
                "--features", rust_required_features,
                "--profile", rust_profile,
            )

            # Path of the compiled binary
            compiled_binary = self.BUILD_DIR/rust_target_triple/rust_profile/f"{project.name}{compiled_extension}"

        # -----------------------------------------------------------------------------------------|
        # # Deal with bundling
        else:
            log.error(f"Unknown Project [{project.name}] Language")
            return

        # Standard naming for all projects
        release_binary = self.RELEASES_DIR/f"{project.name.lower()}-{platform.value}-{date}{release_extension}"
        release_zip    = release_binary.parent/(release_binary.stem + ".zip")

        # Default release
        shutil.copy(compiled_binary, release_binary)
        os.remove(compiled_binary)

        # Rust: Windows bundling into a ZIP file for ndarray-linalg that doesn't properly statically link
        if (language == ProjectLanguage.Rust) and (BrokenPlatform.OnLinux) and (platform == "windows-amd64") and ("ndarray" in rust_required_features):
            required_shared_libraries = [
                "libgfortran-5.dll",
                "libgcc_s_seh-1.dll",
                "libwinpthread-1.dll",
                "libquadmath-0.dll",
            ]

            COMMON_MINGW_DLL_PATHS = [
                Path("/usr/x86_64-w64-mingw32/bin/"),              # Arch
                Path("/usr/lib/gcc/x86_64-w64-mingw32/10-win32/"), # Ubuntu
            ]

            # Zip the releaseBinary and all the required shared libraries
            with zipfile.ZipFile(release_zip, "w") as zip:
                def add_file_to_zip(file: Path, remove=False):
                    zip.write(file, file.name)
                    if remove: file.unlink()

                add_file_to_zip(release_binary, remove=True)

                for library in required_shared_libraries:
                    for path in COMMON_MINGW_DLL_PATHS:
                        try:
                            add_file_to_zip(path/library)
                        except FileNotFoundError:
                            pass

                    # Check if library was copied to the zip
                    if not library in zip.namelist():
                        raise FileNotFoundError(f"Could not find [{library}] in any of the following paths: {COMMON_MINGW_DLL_PATHS}")

        # Write sha256sum of a file next to it
        sha256 = hashlib.sha256(release_binary.read_bytes()).hexdigest()
        release_binary.with_suffix(".sha256").write_text(sha256)

    def requirements(self):
        """Install external dependencies based on your platform for Python releases or compiling Rust projects"""

        # "$ ./broken" -> "$ broken"
        if not "." in os.environ.get("PATH").split(os.pathsep):
            log.info(f"TIP: You can append '.' to $PATH env var so current directory binaries are found, no more typing './broken' but simply 'broken'. Add to your shell config: 'export PATH=$PATH:.'")

        # # Install Requirements depending on host platform
        if BrokenPlatform.OnLinux:
            if BrokenPlatform.LinuxDistro == "arch":
                shell(SUDO, PACMAN, "-Syu", [
                    "base-devel",
                    "gcc-fortran",
                    "mingw-w64-toolchain",
                    "upx",

                    # Python cross compilation to Windows
                    "wine",
                    "wine-mono",
                    "winetricks",

                    # Python Nuitka
                    "ccache",
                    "patchelf"
                ])
                return

            log.warning(f"[{BrokenPlatform.LinuxDistro}] Linux Distro is not officially supported. Please fix or implement dependencies for your distro if it doesn't work.")

            if BrokenPlatform.LinuxDistro == "ubuntu":
                shell(SUDO, APT, "update")
                shell(SUDO, APT, "install", "build-essential mingw-w64 gfortran-mingw-w64 gcc gfortran upx wine".split())

        elif BrokenPlatform == "windows":
            raise NotImplementedError("Broken releases on Windows not implemented")

        elif BrokenPlatform == "macos":
            raise NotImplementedError("Broken releases on macOS not tested / implemented")

            # Install Homebrew
            with BrokenDownloads.download("https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh") as installer:
                shell(BASH, installer)

            # Install make dependencies
            shell(brew, "install", "mingw-w64", "upx")


# -------------------------------------------------------------------------------------------------|

def main():
    broken = BrokenCLI()
    broken.cli()

if __name__ == "__main__":
    main()
