from Broken import *

# "nightly" or "stable"
RUSTUP_TOOLCHAIN = "stable"

# Binaries shorthands
python = system.executable
sh = "sh" if (not BrokenPlatform.Windows) else None
poetry = [python, "-m", "poetry"]
pip = [python, "-m", "pip"]
pacman = "pacman"
rustup = "rustup"
cargo = "cargo"
chmod = "chmod"
sudo = "sudo"
apt = "apt"

# -------------------------------------------------------------------------------------------------|

ABOUT = """
Broken Source Software manager script\n
• Tip: run "broken (command) --help" for options on commands or projects

(c) 2022-2023 BrokenSource, AGPLv3-only License.
"""

class Broken:
    ProjectFeatures = {}
    FindProjectLowercase = {}

    def __init__(self) -> None:
        self.install_rust()

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.typer_app = typer.Typer(help=ABOUT, no_args_is_help=True, add_completion=False)
        self.typer_app.command()(self.hooks)
        self.typer_app.command()(self.install)
        self.typer_app.command()(self.release)
        self.typer_app.command()(self.requirements)
        self.typer_app.command()(self.update)

        # Directories
        self.RELEASES_DIR = BROKEN_ROOT/"Release"
        self.BUILD_DIR    = self.RELEASES_DIR/"Build"

        # Cargo dictionary
        self.cargotoml = DotMap(toml.loads((BROKEN_ROOT/"Cargo.toml").read_text()))

        # Add Typer commands for all projects
        for project in self.cargotoml["bin"]:
            project_name = project["name"]

            # Don't add non existing projects (private repos)
            if not (BROKEN_ROOT/project["path"]).exists(): continue

            # List of required features specified in Cargo.tml
            Broken.ProjectFeatures[project_name] = ','.join(project.get("required-features", ["default"]))
            Broken.FindProjectLowercase[project_name.lower()] = project_name

            # This is a bit sophisticated, projectName should be kept after the callable
            # is created, so we have a method that creates a method with given string
            def run_project_template(project_name):
                def runProject(ctx: typer.Context, debug: bool=False):
                    release = ["--profile", "release"] if not debug else []
                    shell(cargo, "run", "--bin", project_name, "--features", Broken.ProjectFeatures[project_name], release, "--", ctx.args)
                return runProject

            # Create Typer command
            self.typer_app.command(
                name=project_name.lower(),
                help=f"Run {project_name} project",
                rich_help_panel="Projects",

                # Catch extra (unknown to typer) arguments that are sent to Rust
                context_settings=dict(allow_extra_args=True, ignore_unknown_options=True),

                # Rust projects implement their own --help
                add_help_option=False,

            )(run_project_template(project_name))

        # Execute the CLI
        self.typer_app()

    # NOTE: Also returns date string
    def date(self) -> str:
        """Set current UTC dates on Cargo.toml"""
        date = arrow.utcnow().format("YYYY.M.D")

        # Find "version=" line and set it to "version={date}"", write back to file
        (BROKEN_ROOT/"Cargo.toml").write_text('\n'.join(
            [line if not line.startswith("version") else f'version = "{date}"'
            for line in (BROKEN_ROOT/"Cargo.toml").read_text().split("\n")]
        ))

        return date

    # # Commands section

    def hooks(self) -> None:
        """Uses Git hooks under the folder Broken/Hooks"""

        # Make all hooks executable
        for file in (BROKEN_ROOT/"Broken/Hooks").iterdir():
            shell(chmod, "+x", file)

        # Set git hooks path to Broken/Hooks
        shell("git", "config", "core.hooksPath", "./Broken/Hooks")

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
                shell(sh, installer, "--profile", "default", "-y")

        # Detect if default Rust toolchain installed is the one specificed in RUSTUP_TOOLCHAIN
        for line in shell(rustup, "toolchain", "list", output=True, echo=False).split("\n"):
            if ("no installed" in line) or (("default" in line) and (line.split("-")[0] != RUSTUP_TOOLCHAIN)):
                info(f"Defaulting Rust toolchain to [{RUSTUP_TOOLCHAIN}]")
                shell(rustup, "default", RUSTUP_TOOLCHAIN)

    def install(self) -> None:
        """Symlinks current directory to BROKEN_SHARED_DIRECTORY for sharing code in External projects, makes `broken` command available globally by adding it to PATH"""
        # FIXME: How to handle multiple users (not common)? pyproject.toml shall point to /Broken as the shared directory, but it can't source env vars, that would be the ideal case

        if BrokenPlatform.Unix:
            # BROKEN_SHARED_DIRECTORY might already be a symlink to BROKEN_ROOT
            if not Path(BROKEN_SHARED_DIRECTORY).resolve() == BROKEN_ROOT:
                info(f"Creating symlink [{BROKEN_SHARED_DIRECTORY}] -> [{BROKEN_ROOT}]")
                shell("sudo", "ln", "-snf", BROKEN_ROOT, BROKEN_SHARED_DIRECTORY)

        # FIXME: Does this work?
        elif BrokenPlatform.Windows:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                warning("Windows symlink requires admin privileges on current shell, please open an admin PowerShell/CMD and run [  broken install] again")
                return
            rmdir(BROKEN_SHARED_DIRECTORY, confirm=True)
            Path(BROKEN_SHARED_DIRECTORY).symlink_to(BROKEN_ROOT, target_is_directory=True)

        else: error(f"Unknown Platform [{BrokenPlatform.Name}]"); return

        # Symlink created, add to PATH the shared directory
        success(f"Symlink created [{BROKEN_SHARED_DIRECTORY}] -> [{BROKEN_ROOT}]")
        ShellCraft.add_path_to_system_PATH(BROKEN_SHARED_DIRECTORY)

    def update(self):
        """Update Cargo, Python dependencies and Rust lang"""
        self.install_rust()
        shell(cargo, "update")
        shell(rustup, "update")
        shell(poetry, "update")

    def release(self, project: str, platform: str, profile: str="ultra", upx: bool=False) -> None:
        """Compile and release a project (or 'all') to a target (or 'all') platforms"""
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
            for project in Broken.ProjectFeatures.keys():
                self.release(project, platform, profile, upx)

        # Project CLI input may be lowercase
        project = Broken.FindProjectLowercase.get(project, project)

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
        shell(rustup, "target", "add", target_triple)
        features = Broken.ProjectFeatures[project]

        # Build the binary
        shell(cargo, "build",
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
        """Install requirements based on platform"""

        # "$ ./broken" -> "$ broken"
        if not "." in os.environ.get("PATH").split(os.pathsep):
            info(f"TIP: You can append '.' to $PATH env var so current directory binaries are found, no more typing './broken' but simply 'broken'. Add to your shell config: 'export PATH=$PATH:.'")

        # # Install Requirements depending on host platform
        if BrokenPlatform == "linux":
            if LINUX_DISTRO == "arch":
                self.shell(sudo, pacman, "-Syu", "base-devel gcc-fortran mingw-w64-toolchain upx".split())
                return

            self.warning(f"[{LINUX_DISTRO}] Linux Distro is not officially supported. Please fix or implement dependencies for your distro if it doesn't work.")

            if LINUX_DISTRO == "ubuntu":
                self.shell(sudo, apt, "update")
                self.shell(sudo, apt, "install", "build-essential mingw-w64 gfortran-mingw-w64 gcc gfortran upx".split())

        elif BrokenPlatform == "windows":
            raise NotImplementedError("Broken releases on Windows not implemented")

        elif BrokenPlatform == "macos":
            raise NotImplementedError("Broken releases on macOS not tested / implemented")

            # Install Homebrew
            with download("https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh") as installer:
                self.shell(bash, installer)

            # Install make dependencies
            self.shell(brew, "install", "mingw-w64", "upx")


# -------------------------------------------------------------------------------------------------|

def main():
    broken = Broken()
    broken.cli()

if __name__ == "__main__":
    main()
