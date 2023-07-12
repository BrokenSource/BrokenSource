from . import *

# Distros IDs: https://distro.readthedocs.io/en/latest/
LINUX_DISTRO = distro.id()

class BrokenPlatform:
    # Name of the current platform
    Name    = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    Linux   = Name == "linux"
    Windows = Name == "windows"
    MacOS   = Name == "macos"
    BSD     = Name == "bsd"

    # Family of platforms
    Unix    = Linux or MacOS or BSD
