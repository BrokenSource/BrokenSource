"""Class that handles common path operations, env PATH, getting binaries, touch, mkdir, copy, chmod"""
from . import *


class BrokenPath:

    @contextmanager
    def PATH(
        directories: List[PathLike],
        recursive: bool=True,
        prepend: bool=True,
        clean: bool=False,
        restore: bool=True,
    ):
        """
        Temporarily limits the PATH to given directories
        - directories: List of directories to add to PATH
        - recursive: Whether to add subdirectories of given directories to PATH
        - prepend: Prioritize binaries found in input directories
        - restricted: Do not include current PATH in the new PATH
        """

        # Make Path objects
        directories = [Path(x) for x in BrokenUtils.force_list(directories)]

        # Get current PATH
        old = os.environ["PATH"]

        # List of all directories in PATH
        PATH = [] if clean else os.environ["PATH"].split(os.pathsep)

        # Add directories to PATH
        for directory in directories:
            PATH.append(directory)

            # Do not recurse if so
            if not recursive:
                continue

            # WARN: This could be slow on too many directories (wrong input?)
            # Find all subdirectories of a path
            for path in directory.rglob("*"):
                if path.is_dir():
                    if prepend:
                        PATH.insert(0, path)
                    else:
                        PATH.append(path)

        # Set new PATH
        os.environ["PATH"] = os.pathsep.join(map(str, PATH))

        yield os.environ["PATH"]

        # Restore PATH
        os.environ["PATH"] = old

    def get_binary(name: str, file_not_tagged_executable_workaround=True, echo=True) -> Option[Path, None]:
        """Get a binary from PATH"""

        # Get binary if on path and executable
        binary = shutil.which(name)

        # Workaround for files that are not set as executable: shutil will not find them
        # • Attempt finding directory/name for every directory in PATH
        if (binary is None) and file_not_tagged_executable_workaround :
            for directory in os.environ["PATH"].split(os.pathsep):
                if (maybe_the_binary := Path(directory)/name).is_file():
                    binary = maybe_the_binary
                    break

        # Print information about the binary
        if echo: (log.warning if (binary is None) else log.success)(f"• Binary [{str(name).ljust(20)}]: [{binary}]", echo=echo)

        return binary

    def binary_exists(name: str, echo=True) -> bool:
        """Check if a binary exists on PATH"""
        return BrokenPath.get_binary(name, echo=echo) is not None

    # # Specific / "Utils"

    @contextmanager
    def pushd(path: PathLike):
        """Change directory, then change back when done"""
        cwd = os.getcwd()
        os.chdir(path)
        yield path
        os.chdir(cwd)

    def true_path(path: PathLike) -> Path:
        return Path(path).expanduser().resolve().absolute()

    def make_executable(path: PathLike, echo=False) -> None:
        """Make a file executable"""
        path = Path(path)
        if BrokenPlatform.OnUnix:
            shell("chmod", "+x", path, echo=echo)

    # # File or directory creation

    def mkdir(path: PathLike, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        path = Path(path)
        if path.exists():
            log.success(f"Directory [{path}] already exists", echo=echo)
            return
        log.info(f"Creating directory {path}", echo=echo)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def touch(path: PathLike, echo=True):
        """Creates a file, fail safe™"""
        path = Path(path)
        if path.exists():
            log.success(f"File [{path}] already exists", echo=echo)
            return
        log.info(f"Creating file {path}", echo=echo)
        path.touch()

    # # Data moving

    def copy(source: PathLike, destination: PathLike, echo=True):
        source, destination = Path(source), Path(destination)
        log.info(f"Copying [{source}] -> [{destination}]", echo=echo)
        shutil.copy2(source, destination)

    # Path may be a file or directory
    def remove(path: PathLike, confirm=False, echo=True) -> bool:
        path = Path(path)
        log.info(f"• Removing Path ({confirm=}) [{path}]", echo=echo)

        if not path.exists():
            log.success(f"└─ Does not exist", echo=echo)
            return False

        # Symlinks are safe to remove
        if path.is_symlink():
            path.unlink()
            log.success(f"└─ Removed Symlink", echo=echo)
            return True

        # Confirm removal: directory contains data
        if confirm and (not rich.prompt.Confirm.ask(f"• Confirm removing path ({path})")):
            return False

        # Remove the path
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            log.success(f"└─ Removed Directory", echo=echo)
        else:
            path.unlink()
            log.success(f"└─ Removed File", echo=echo)

        return True

    def open_in_file_explorer(path: PathLike):
        """Opens a path in the file explorer"""
        path = Path(path)
        if BrokenPlatform.OnWindows:
            os.startfile(str(path))
        elif BrokenPlatform.OnLinux:
            shell("xdg-open", path)
        elif BrokenPlatform.OnMacOS:
            shell("open", path)

    def symlink(where: Path, to: Path, echo=True):
        """Symlink a path to another path"""
        log.info(f"Symlinking [{where}] -> [{to}]", echo=echo)
        BrokenPath.mkdir(where.parent, echo=False)
        where.symlink_to(to)

class ShellCraft:

    # Current shell name (binary path)
    SHELL_BINARY = os.environ.get("SHELL", "unknown")

    # Booleans if the current shell is the following
    BASH       = "bash" in SHELL_BINARY
    ZSH        = "zsh"  in SHELL_BINARY
    FISH       = "fish" in SHELL_BINARY
    Unknown    = (not (BASH or ZSH or FISH)) or (SHELL_BINARY == "unknown")

    def add_path_to_system_PATH(path: PathLike, echo=True) -> bool:
        """Add a path to the system PATH _ideally_ for all platforms. Sincerely, f-pointer-comment-at this function"""
        path = Path(path)

        # If the path is already in the system path, no work to do
        if str(path) in os.environ.get("PATH", "").split(os.pathsep):
            log.success(f"Path [{path}] already in PATH", echo=echo)
            return True

        # Unix is complicated, ideally one would put on /etc/profile but it's only reloaded on logins
        # The user shell varies a lot, but most are in BASH, ZSH or FISH apparently, but need sourcing or restarting
        if BrokenPlatform.OnUnix:

            # The export line adding to PATH the wanted path
            export = f"export PATH={path}:$PATH"

            # Add the export line based on the current shell
            for current_shell, shellrc in [
                (ShellCraft.BASH,    HOME_DIR/".bashrc"                 ),
                (ShellCraft.ZSH,     HOME_DIR/".zshrc"                  ),
                (ShellCraft.FISH,    HOME_DIR/".config/fish/config.fish"),
                (ShellCraft.Unknown, HOME_DIR/".profile")
            ]:
                # Skip if not on this chell
                if not current_shell: continue

                # Info on what's going on
                if ShellCraft.Unknown:
                    log.error(f"Your shell is unknown and PATH will be re-exported in [{shellrc}], you need to log out and log in for changes to take effect, go touch some grass..   (PRs are welcome!)", echo=echo)

                log.info(f"Your current shell is [{ShellCraft.SHELL_BINARY}], adding the directory [{path}] to PATH in the shell rc file [{shellrc}] as [{export}]", echo=echo)

                # Add the export line to the shell rc file
                with open(shellrc, "a") as file:
                    file.write(f"{export}\n")

            # Need to restart the shell or source it
            log.warning(f"Please restart your shell for the changes to take effect or run [source {shellrc}] or [. {shellrc}] on current one, this must be done since a children process (Python) can't change the parent process (your shell) environment variables plus the [source] or [.] not binaries but shell builtins")

        # No clue if this works.
        elif BrokenPlatform.OnWindows:
            log.fixme("I don't know if the following reg command works for adding a PATH to PATH on Windows")
            shell("reg", "add", r"HKCU\Environment", "/v", "PATH", "/t", "REG_SZ", "/d", f"{path};%PATH%", "/f")
            shell("refreshenv")

        else:
            log.error(f"Unknown Platform [{BrokenPlatform.Name}]")
            return False

        return True

