from Broken import *

# "nightly" or "stable"
RUSTUP_TOOLCHAIN = "stable"

# -------------------------------------------------------------------------------------------------|

find = lambda name: get_binary(name, echo=False)

# Find binaries absolute path
PYTHON      = system.executable
POETRY      = [PYTHON, "-m", "poetry"]
PIP         = [PYTHON, "-m", "pip"]
PYINSTALLER = find("pyinstaller")
BASH        = find("bash") if (not BrokenPlatform.Windows) else None
PACMAN      = find("pacman")
RUSTUP      = find("rustup")
CARGO       = find("cargo")
CHMOD       = find("chmod")
SUDO        = find("sudo")
APT         = find("apt")
GIT         = find("git")

# Development tools
ISORT   = find("isort")
PYCLEAN = find("pyclean")

# -------------------------------------------------------------------------------------------------|

ABOUT = """
Broken Source Software manager script\n
• Tip: run "broken (command) --help" for options on commands or projects

(c) 2022-2023 BrokenSource, AGPLv3-only License.
"""

class Broken:
    # Cargo.toml's required-features as ["--features", "default" ? "feature1,feature2"]
    RustProjectFeatures = {}

    # dict["depthflow"] -> "DepthFlow"
    ProjectNameLowercaseToReal = {}

    def __init__(self) -> None:
        self.RELEASES_DIR = BROKEN_ROOT_DIR/"Release"
        self.BUILD_DIR    = self.RELEASES_DIR/"Build"
        self.PROJECTS_DIR = BROKEN_ROOT_DIR/"Projects"

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.typer_app = typer.Typer(
            help=ABOUT,
            add_help_option=False,
            no_args_is_help=True,
            add_completion=False,
            rich_markup_mode="rich",
            epilog="• Made with [red]:heart:[/red] by [green]Broken Source Software[/green]"
        )

        # Section: Installation
        self.typer_app.command(rich_help_panel="Installation")(self.install)
        self.typer_app.command(rich_help_panel="Installation")(self.clone)
        self.typer_app.command(rich_help_panel="Installation")(self.requirements)

        # Section: Releases
        self.typer_app.command(rich_help_panel="Releases")(self.release)
        self.typer_app.command(rich_help_panel="Releases")(self.mock_release_python)

        # Section: Miscellanous
        self.typer_app.command(rich_help_panel="Miscellaneous")(self.date)
        self.typer_app.command(rich_help_panel="Miscellaneous")(self.hooks)
        self.typer_app.command(rich_help_panel="Miscellaneous")(self.update)
        self.typer_app.command(rich_help_panel="Miscellaneous")(self.clean)

        # Add projects commands
        self.add_run_projects_commands()

        # Execute the CLI
        self.typer_app()

    def python_projects(self) -> Iterable[Path]:
        """Generator that yields all Python projects paths"""
        for path in self.PROJECTS_DIR.iterdir():
            if (path/"pyproject.toml").exists():
                yield path

    def __get_install_python_virtualenvironment(self,
        project_name: str,
        project_path: PathLike,
        unset_current_virtualenv: bool=False
    ) -> Path:
        """Get the virtual environment path for a Python project"""
        info(f"Installing virtual environment for {project_name} project")

        with pushd(project_path):

            # Unset virtualenv else the nested poetry will use it
            if unset_current_virtualenv:
                del os.environ["VIRTUAL_ENV"]

            while True:
                venv = shell(POETRY + ["env", "info", "--path"], capture_output=True, cwd=project_path)

                # Virtualenv is not created if command errors or if it's empty
                if (venv.returncode == 1) or (not venv.stdout.strip()):
                    shell(POETRY, "install", cwd=project_path)
                    continue

                # Get and return virtualenv path
                venv_path = Path(venv.stdout.decode("utf-8").strip())
                success(f"Virtual environment for Project [{project_name}] is [{venv_path}]")
                return venv_path

    # FIXME: Will I ever have projects in other languages?
    def add_run_projects_commands(self, echo=False) -> None:
        self.cargotoml = DotMap(toml.loads((BROKEN_ROOT_DIR/"Cargo.toml").read_text()))

        # Build Rust required features
        for rust_project in self.cargotoml["bin"]:
            Broken.RustProjectFeatures[rust_project.get("name")] = ','.join(rust_project.get("required-features", ["default"]))

        # Iterate on all directories
        for project_path in self.PROJECTS_DIR.iterdir():

            # Might have non-project files
            if not project_path.is_dir():
                continue

            # Empty dir might be a bare submodule
            if not list(project_path.iterdir()):
                if echo: warning(f"Project [{project_path.name}] is empty")
                continue

            # Get project name and translate lowercase to real name
            project_name = project_path.name
            Broken.ProjectNameLowercaseToReal[project_name.lower()] = project_name

            project_language = "python" if (project_path/"pyproject.toml").exists() else "rust"

            if (project_path/"pyproject.toml").exists():
                project_language = "python"
            elif project_name in Broken.RustProjectFeatures:
                project_language = "rust"
            else:
                if echo: error(f"Unknown Project [{project_name}]")
                continue

            # A very weird @wraps() decorator to keep local strings and return a function that runs the project
            def run_project_template(project_name: str, project_path: PathLike, project_language: str):
                def run_project(
                    ctx: typer.Context,
                    debug=typer.Option(False, "--debug", "-d", help="Debug mode for Rust projects"),
                ):
                    # Route for Python projects
                    if project_language == "python":
                        self.__get_install_python_virtualenvironment(
                            project_name, project_path,
                            unset_current_virtualenv=True
                        )
                        shell(POETRY, "run", project_name.lower(), ctx.args, cwd=project_path)

                    # Route for Rust projects
                    elif project_language == "rust":
                        self.install_rust()
                        release = ["--profile", "release"] if not debug else []
                        shell(CARGO, "run", "--bin", project_name, "--features", Broken.RustProjectFeatures[project_name], release, "--", ctx.args)

                return run_project

            # Create Typer command
            self.typer_app.command(
                name=project_name.lower(),
                help=f"Run {project_name} project",
                rich_help_panel=f"{project_language.capitalize()} Projects",

                # Catch extra (unknown to typer) arguments that are sent to Python
                context_settings=dict(allow_extra_args=True, ignore_unknown_options=True),

                # Projects implement their own --help
                add_help_option=False,

            )(run_project_template(project_name, project_path, project_language))

    # NOTE: Also returns date string
    def date(self) -> str:
        """Set current UTC dates on Cargo.toml and all Python project's pyproject.toml"""
        date = arrow.utcnow().format("YYYY.M.D")

        # Find "version=" line and set it to "version = {date}"", write back to file
        def update_date(file: Path) -> None:
            if not file.exists(): return
            info(f"Updating date on file [{file}] to [{date}]")
            file.write_text('\n'.join(
                [line if not line.startswith("version") else f'version = "{date}"'
                for line in file.read_text().split("\n")]
            ))

        # Python projects
        for project in self.python_projects():
            update_date(project/"pyproject.toml")

        # Rust projects
        update_date(BROKEN_ROOT_DIR/"Cargo.toml")

        return date

    # # Commands section

    def hooks(self) -> None:
        """Use all Git hooks under the folder Broken/Hooks"""

        # Make all hooks executable
        for file in (BROKEN_ROOT_DIR/"Broken/Hooks").iterdir():
            shell(CHMOD, "+x", file)

        # Set git hooks path to Broken/Hooks
        shell(GIT, "config", "core.hooksPath", "./Broken/Hooks")

    def clean(self) -> None:
        """Sorts imports, cleans .pyc files"""

        # Sort imports, ignore "Releases" folder
        shell(ISORT, BROKEN_ROOT_DIR,
            "--force-single-line-imports",
            "--skip", self.RELEASES_DIR
        )

        # Clean pycache with pycclean
        shell(PYCLEAN, "-v", BROKEN_ROOT_DIR)

    # Install Rust toolchain on macOS, Linux
    def install_rust(self) -> None:

        # Install rustup for toolchains
        if not all([binary_exists(b) for b in ["rustup", "rustc", "cargo"]]):
            info(f"Installing Rustup default profile")

            # Get rustup link for each platform
            rust_installer = dict(
                windows="https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-gnu/rustup-init.exe",
                linux=  "https://sh.rustup.rs",
                macos=  "https://sh.rustup.rs"
            ).get(BrokenPlatform)

            # Download and install Rust
            with download(rust_installer) as installer:
                shell(BASH, installer, "--profile", "default", "-y")

        # Detect if default Rust toolchain installed is the one specificed in RUSTUP_TOOLCHAIN
        for line in shell(RUSTUP, "toolchain", "list", output=True, echo=False).split("\n"):
            if ("no installed" in line) or (("default" in line) and (line.split("-")[0] != RUSTUP_TOOLCHAIN)):
                info(f"Defaulting Rust toolchain to [{RUSTUP_TOOLCHAIN}]")
                shell(RUSTUP, "default", RUSTUP_TOOLCHAIN)

    def clone(self, private: bool=False) -> None:
        """Clones and initializes to default branch for all public submodules"""

        # Cached requests session since GitHub API is rate limited to 60 requests per hour
        session = requests_cache.CachedSession(BROKEN_DIRECTORIES.CACHE/'GitHubApiCache')

        def needed_repo_data(owner: str, name: str) -> Tuple[bool, str]:
            """Returns: (is_private, default_branch)"""
            private, branch = True, "Unknown"

            # Uses GitHub API to get status on a repo, might return content if credentials are set
            data = session.get(f"https://api.github.com/repos/{owner}/{name}").json()

            # Check for GitHub API rate limit
            if "rate limit" in data.get("message", "").lower():
                error(f"GitHub API rate limit reached, maybe authenticate or wait a few minutes")
                fixme("Rewrite this code for something that doesn't rely on GitHub API")
                exit(1)

            # No credentials given it'll simply return Not Found message
            if data.get("message") != "Not Found":
                private, branch = data.get("private"), data.get("default_branch")

            return private, branch

        # Read .gitmodules file to a dictionary (.ini file)
        import configparser

        gitmodules = configparser.ConfigParser()
        gitmodules.read(".gitmodules")

        # Iterate over each submodule
        for section in gitmodules.sections():

            # Get path and url, split on owner and name, find private and branch
            path = BROKEN_ROOT_DIR/gitmodules.get(section, "path", fallback=None)
            url  = gitmodules.get(section, "url",  fallback=None)
            owner, name = url.split("/")[-2:]
            private, branch = needed_repo_data(owner, name)

            # Log info on screen
            (warning if private else success)(f"Repository [{f'{owner}/{name}'.ljust(25)}] [Private: {str(private).ljust(5)}] [Default Branch: {branch}]")

            # Skip private repos
            if private: continue

            # Clone repo
            shell(GIT, "submodule", "update", "--init", "--recursive", path)

            # Checkout to default branch
            if branch: shell(GIT, "checkout", branch, "-q", cwd=path)
            else: warning(f"Default branch not found for [{owner}/{name}], skipping checkout?")

    def install(self) -> None:
        """Symlinks current directory to BROKEN_SHARED_DIRECTORY for sharing code in External projects, makes `brokenshell` command available anywhere by adding current folder to PATH"""
        fixme("Do you need to install Broken for multiple users? If so, please open an issue on GitHub.")

        # Symlink Broken Shared Directory to Broken Root
        if BrokenPlatform.Unix:
            # BROKEN_SHARED_DIRECTORY might already be a symlink to BROKEN_ROOT
            if not Path(BROKEN_SHARED_DIR).resolve() == BROKEN_ROOT_DIR:
                info(f"Creating symlink [{BROKEN_SHARED_DIR}] -> [{BROKEN_ROOT_DIR}]")
                shell("sudo", "ln", "-snf", BROKEN_ROOT_DIR, BROKEN_SHARED_DIR)
        elif BrokenPlatform.Windows:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                warning("Windows symlink requires admin privileges on current shell, please open an admin PowerShell/CMD and run [  broken install] again")
                return
            # FIXME: Does this work?
            fixme("I'm not sure if the symlink command on Windows works and links to C:\\Broken")
            rmdir(BROKEN_SHARED_DIR, confirm=True)
            Path(BROKEN_SHARED_DIR).symlink_to(BROKEN_ROOT_DIR, target_is_directory=True)
        else: error(f"Unknown Platform [{BrokenPlatform.Name}]"); return

        success(f"Symlink created [{BROKEN_SHARED_DIR}] -> [{BROKEN_ROOT_DIR}]")

        # Add Broken Shared Directory to PATH
        ShellCraft.add_path_to_system_PATH(BROKEN_SHARED_DIR)

    def update(self):
        """Updates Cargo and Python dependencies, Rust language toolchain and Poetry"""
        self.install_rust()
        shell(CARGO, "update")
        shell(RUSTUP, "update")
        shell(POETRY, "update")

    def mock_release_python(self) -> None:
        mkdir(self.RELEASES_DIR)

        # Simulate eventual function arguments
        project_name = "DepthFlow"
        project_path = self.PROJECTS_DIR/project_name

        # Create install virtualenv dependencies
        project_venv = self.__get_install_python_virtualenvironment(
            project_name, project_path,
            unset_current_virtualenv=False
        )

        # Find site_packages of the project's virtualenv
        python_version = f"python{system.version_info.major}.{system.version_info.minor}"
        site_packages = project_venv/"lib"/python_version/"site-packages"

        # Use the project's virtualenv site-packages
        os.environ["PYTHONPATH"] = str(site_packages)
        info(f"Using site-packages [{site_packages}]")

        # Compile project
        shell(PYINSTALLER,

            # Where and how to build
            "--workpath", self.BUILD_DIR,
            "--onefile",
            "--clean",
            "--noconfirm",

            # Hidden imports that may contain binaries
            "--hidden-import", "imageio_ffmpeg",
            "--hidden-import", "glcontext",

            # Where to put the binary and its name
            f"--distpath={self.RELEASES_DIR}",
            "-n", project_name,

            # Target file to compile
            self.PROJECTS_DIR/project_name/project_name/"__init__.py",
        )


    def release(self, project: str, platform: str, profile: str="ultra", upx: bool=False) -> None:
        """Compile and release a project (or 'all') to a target (or 'all') platforms"""
        self.install_rust()
        mkdir(self.RELEASES_DIR)

        # Target triple, compiled extension, release extension
        platforms_configuration = {
            "linux-amd64":   ("x86_64-unknown-linux-gnu",  "",     ".bin"),
            # "linux-arm":     ("aarch64-unknown-linux-gnu", "",     ".bin"),
            "windows-amd64": ("x86_64-pc-windows-gnu",     ".exe", ".exe"),

            # FIXME: Requires Xcode, can we crosscompile from Linux?
            # "macos-amd64":   ("x86_64-apple-darwin",       "",     ".bin"),
            # "macos-arm":     ("aarch64-apple-darwin",      "",     ".bin"),
        }

        # Acronym for all available projects
        if project == "all":
            for project in Broken.RustProjectFeatures.keys():
                self.release(project, platform, profile, upx)

        # Project CLI input may be lowercase
        project = Broken.ProjectNameLowercaseToReal.get(project, project)

        # Acronym for all available platforms
        if platform == "all":
            for platform in platforms_configuration.keys():
                try: self.release(project, platform, profile, upx)
                except FileNotFoundError:
                    error(f"Could not compile [{project}] for [{platform}]")
            return

        # Fix Fortran compiler for Windows crosscompilation netlib for ndarray-linalg package
        if (BrokenPlatform == "linux") and (platform == "windows-amd64"):
            os.environ["FC"] = "x86_64-w64-mingw32-gfortran"

        # # Target platform
        (target_triple, compiled_extension, release_extension) = platforms_configuration[platform]

        # Update dates
        date = self.date()

        # Add target toolchain for Rust
        shell(RUSTUP, "target", "add", target_triple)
        features = Broken.RustProjectFeatures[project]

        # Build the binary
        shell(CARGO, "build",
            "--bin", project,
            "--target", target_triple,
            "--features", features,
            "--profile", profile,
        )

        # Post-compile binary namings and release name
        compiled_binary    = self.BUILD_DIR/target_triple/profile/f"{project}{compiled_extension}"
        release_binary     = self.RELEASES_DIR/f"{project.lower()}-{platform}-{date}{release_extension}"
        release_zip        = release_binary.parent/(release_binary.stem + ".zip")
        release_binary_UPX = release_binary.parent/(release_binary.stem + f"-upx{release_extension}")

        # Default release and UPX
        shutil.copy(compiled_binary, release_binary)
        if upx: shell("upx", "-q", "-9", "--lzma", release_binary, "-o", release_binary_UPX)

        # Windows bundling into a ZIP file for ndarray-linalg that doesn't properly statically link
        if (BrokenPlatform == "linux") and (platform == "windows-amd64") and ("ndarray" in features):
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
                def addFileToZip(file: Path, remove=False):
                    zip.write(file, file.name)
                    if remove: file.unlink()

                if upx: addFileToZip(release_binary_UPX, remove=True)
                addFileToZip(release_binary, remove=True)

                for library in required_shared_libraries:
                    for path in COMMON_MINGW_DLL_PATHS:
                        try:
                            addFileToZip(path/library)
                        except FileNotFoundError:
                            pass

                    # Check if library was copied to the zip
                    if not library in zip.namelist():
                        raise FileNotFoundError(f"Could not find [{library}] in any of the following paths: {COMMON_MINGW_DLL_PATHS}")

    def requirements(self):
        """Install external dependencies based on your platform for Python releases or compiling Rust projects"""

        # "$ ./broken" -> "$ broken"
        if not "." in os.environ.get("PATH").split(os.pathsep):
            info(f"TIP: You can append '.' to $PATH env var so current directory binaries are found, no more typing './broken' but simply 'broken'. Add to your shell config: 'export PATH=$PATH:.'")

        # # Install Requirements depending on host platform
        if BrokenPlatform == "linux":
            if LINUX_DISTRO == "arch":
                self.shell(SUDO, PACMAN, "-Syu", [
                    "base-devel",
                    "gcc-fortran",
                    "mingw-w64-toolchain",
                    "upx",

                    # Python Nuitka
                    "ccache",
                    "patchelf"
                ])
                return

            self.warning(f"[{LINUX_DISTRO}] Linux Distro is not officially supported. Please fix or implement dependencies for your distro if it doesn't work.")

            if LINUX_DISTRO == "ubuntu":
                self.shell(SUDO, APT, "update")
                self.shell(SUDO, APT, "install", "build-essential mingw-w64 gfortran-mingw-w64 gcc gfortran upx".split())

        elif BrokenPlatform == "windows":
            raise NotImplementedError("Broken releases on Windows not implemented")

        elif BrokenPlatform == "macos":
            raise NotImplementedError("Broken releases on macOS not tested / implemented")

            # Install Homebrew
            with download("https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh") as installer:
                self.shell(BASH, installer)

            # Install make dependencies
            self.shell(brew, "install", "mingw-w64", "upx")


# -------------------------------------------------------------------------------------------------|

def main():
    broken = Broken()
    broken.cli()

if __name__ == "__main__":
    main()
