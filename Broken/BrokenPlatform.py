from . import *


class BrokenPlatform:
    # Name of the current platform
    Name      = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    OnLinux   = Name == "linux"
    OnWindows = Name == "windows"
    OnMacOS   = Name == "macos"
    OnBSD     = Name == "bsd"

    # Family of platforms
    OnUnix    = OnLinux or OnMacOS or OnBSD

    # Distros IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro = distro.id()

