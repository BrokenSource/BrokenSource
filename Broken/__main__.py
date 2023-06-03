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
        self.installRust()

    # Builds CLI commands and starts Typer
    def cli(self) -> None:
        self.typerApp = typer.Typer(help=ABOUT, no_args_is_help=True, add_completion=False)
        self.typerApp.command()(self.hooks)
        self.typerApp.command()(self.release)
        self.typerApp.command()(self.requirements)
        self.typerApp.command()(self.update)

        # Directories
        self.Root     = Path(__file__).absolute().parent.parent
        self.Releases = self.Root/"Release"
        self.Build    = self.Releases/"Build"

        # Cargo dictionary
        self.cargotoml = DotMap(toml.loads((self.Root/"Cargo.toml").read_text()))

        # Add Typer commands for all projects
        for project in self.cargotoml["bin"]:
            projectName = project["name"]

            # Don't add non existing projects (private repos)
            if not (self.Root/project["path"]).exists(): continue

            # List of required features specified in Cargo.tml
            Broken.ProjectFeatures[projectName] = ','.join(project.get("required-features", ["default"]))
            Broken.FindProjectLowercase[projectName.lower()] = projectName

            # This is a bit sophisticated, projectName should be kept after the callable
            # is created, so we have a method that creates a method with given string
            def runProjectTemplate(projectName):
                def runProject(ctx: typer.Context, release: bool=False):
                    release = ["--profile", "release"] if release else []
                    shell(cargo, "run", "--bin", projectName, "--features", Broken.ProjectFeatures[projectName], release, "--", ctx.args)
                return runProject

            # Create Typer command
            self.typerApp.command(
                name=projectName.lower(),
                help=f"Project: {projectName}",

                # Catch extra (unknown to typer) arguments that are sent to Rust
                context_settings=dict(allow_extra_args=True, ignore_unknown_options=True),

                # Rust projects implement their own --help
                add_help_option=False,

            )(runProjectTemplate(projectName))

        # Execute the CLI
        self.typerApp()

    # NOTE: Also returns date string
    def date(self) -> str:
        """Set current UTC dates on Cargo.toml"""
        date = arrow.utcnow().format("YYYY.M.D")

        # Find "version=" line and set it to "version={date}"", write back to file
        (self.Root/"Cargo.toml").write_text('\n'.join(
            [line if not line.startswith("version") else f'version = "{date}"'
            for line in (self.Root/"Cargo.toml").read_text().split("\n")]
        ))

        return date

    # # Commands section

    def hooks(self) -> None:
        """Uses Git hooks under the folder Broken/Hooks"""

        # Make all hooks executable
        for file in (self.Root/"Broken/Hooks").iterdir():
            shell(chmod, "+x", file)

        # Set git hooks path to Broken/Hooks
        shell("git", "config", "core.hooksPath", "./Broken/Hooks")

    # Install Rust toolchain on macOS, Linux
    def installRust(self) -> None:

        # Install rustup for toolchains
        if not all([binary_exists(b) for b in ["rustup", "rustc", "cargo"]]):
            info(f"Installing Rustup default profile")

            # Get rustup link for each platform
            rustInstaller = dict(
                windows="https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-gnu/rustup-init.exe",
                linux=  "https://sh.rustup.rs",
                macos=  "https://sh.rustup.rs"
            ).get(BrokenPlatform)

            # Download and install Rust
            with download(rustInstaller) as installer:
                shell(sh, installer, "--profile", "default", "-y")

        # Detect if default Rust toolchain installed is the one specificed in RUSTUP_TOOLCHAIN
        for line in shell(rustup, "toolchain", "list", output=True, echo=False).split("\n"):
            if ("no installed" in line) or (("default" in line) and (line.split("-")[0] != RUSTUP_TOOLCHAIN)):
                info(f"Defaulting Rust toolchain to [{RUSTUP_TOOLCHAIN}]")
                shell(rustup, "default", RUSTUP_TOOLCHAIN)

    def update(self):
        """Update Cargo, Python dependencies and Rust lang"""
        self.installRust()
        shell(cargo, "update")
        shell(rustup, "update")
        shell(poetry, "update")

    def release(self, project: str, platform: str, profile: str="ultra", upx: bool=False) -> None:
        """Compile and release a project (or 'all') to a target (or 'all') platforms"""
        mkdir(self.Releases)

        platformsConfiguration = {
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
            for platform in platformsConfiguration.keys():
                try: self.release(project, platform, profile, upx)
                except FileNotFoundError:
                    error(f"Could not compile [{project}] for [{platform}]")
            return

        # Fix Fortran compiler for Windows crosscompilation netlib for ndarray-linalg package
        if (BrokenPlatform == "linux") and (platform == "windows-amd64"):
            os.environ["FC"] = "x86_64-w64-mingw32-gfortran"

        # # Target platform
        (targetTriple, compileSuffix, releaseSuffix) = platformsConfiguration[platform]

        # Update dates
        date = self.date()

        # Add target toolchain for Rust
        shell(rustup, "target", "add", targetTriple)
        features = Broken.ProjectFeatures[project]

        # Build the binary
        shell(cargo, "build",
            "--bin", project,
            "--target", targetTriple,
            "--features", features,
            "--profile", profile,
        )

        # Post-compile binary namings and release name
        compiledBinary   = self.Build/targetTriple/profile/f"{project}{compileSuffix}"
        releaseBinary    = self.Releases/f"{project.lower()}-{platform}-{date}{releaseSuffix}"
        releaseZip       = releaseBinary.parent/(releaseBinary.stem + ".zip")
        releaseBinaryUPX = releaseBinary.parent/(releaseBinary.stem + f"-upx{releaseSuffix}")

        # Default release and UPX
        shutil.copy(compiledBinary, releaseBinary)
        if upx: shell("upx", "-q", "-9", "--lzma", releaseBinary, "-o", releaseBinaryUPX)

        # Windows bundling into a ZIP file for ndarray-linalg that doesn't properly statically link
        if (BrokenPlatform == "linux") and (platform == "windows-amd64") and ("ndarray" in features):
            requiredSharedLibraries = [
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
            with zipfile.ZipFile(releaseZip, "w") as zip:
                def addFileToZip(file: Path, remove=False):
                    zip.write(file, file.name)
                    if remove: file.unlink()

                if upx: addFileToZip(releaseBinaryUPX, remove=True)
                addFileToZip(releaseBinary, remove=True)

                for library in requiredSharedLibraries:
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
