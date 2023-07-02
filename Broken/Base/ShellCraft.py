from . import *


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
            success(f"Path [{path}] already in PATH", echo=echo)
            return True

        # Unix is complicated, ideally one would put on /etc/profile but it's only reloaded on logins
        # The user shell varies a lot, but most are in BASH, ZSH or FISH apparently, but need sourcing or restarting
        if BrokenPlatform.Unix:

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
                    error(f"Your shell is unknown and PATH will be re-exported in [{shellrc}], you need to log out and log in for changes to take effect, go touch some grass..   (PRs are welcome!)", echo=echo)

                info(f"Your current shell is [{ShellCraft.SHELL_BINARY}], adding the directory [{path}] to PATH in the shell rc file [{shellrc}] as [{export}]", echo=echo)

                # Add the export line to the shell rc file
                with open(shellrc, "a") as file:
                    file.write(f"{export}\n")

            # Need to restart the shell or source it
            warning(f"Please restart your shell for the changes to take effect or run [source {shellrc}] or [. {shellrc}] on current one, this must be done since a children process (Python) can't change the parent process (your shell) environment variables plus the [source] or [.] not binaries but shell builtins")

        # No clue if this works.
        elif BrokenPlatform.Windows:
            fixme("I don't know if the following reg command works for adding a PATH to PATH on Windows")
            shell("reg", "add", r"HKCU\Environment", "/v", "PATH", "/t", "REG_SZ", "/d", f"{path};%PATH%", "/f")
            shell("refreshenv")

        else:
            error(f"Unknown Platform [{BrokenPlatform.Name}]")
            return False

        return True
