import ctypes
import os
import platform
from collections.abc import Iterable
from typing import Optional, Self

import distro

from broken import Environment, log
from broken.core.enumx import BrokenEnum, MultiEnum


class SystemEnum(str, MultiEnum):
    Linux:   str = "linux"
    Windows: str = ("windows", "win")
    MacOS:   str = ("macos", "darwin", "osx")
    BSD:     str = ("bsd", "freebsd", "openbsd", "netbsd")

    def is_linux(self) -> bool:
        return (self is self.Linux)

    def is_windows(self) -> bool:
        return (self is self.Windows)

    def is_macos(self) -> bool:
        return (self is self.MacOS)

    def is_bsd(self) -> bool:
        return (self is self.BSD)

    @property
    def extension(self) -> str:
        if (self is self.Windows):
            return ".exe"
        return ".bin"


class ArchEnum(str, MultiEnum):
    AMD32: str = ("amd32", "x86", "i686")
    AMD64: str = ("amd64", "x86_64")
    ARM32: str = "arm32"
    ARM64: str = "arm64"

    def is_arm(self) -> bool:
        return ("arm" in self.value)

    def is_amd(self) -> bool:
        return ("amd" in self.value)

    def is_32_bits(self) -> bool:
        return ("32" in self.value)

    def is_64_bits(self) -> bool:
        return ("64" in self.value)


class PlatformEnum(str, BrokenEnum):
    """List of common platforms targets for releases"""
    WindowsAMD64: str = "windows-amd64"
    WindowsARM64: str = "windows-arm64"
    LinuxAMD64:   str = "linux-amd64"
    LinuxARM64:   str = "linux-arm64"
    MacosAMD64:   str = "macos-amd64"
    MacosARM64:   str = "macos-arm64"

    @staticmethod
    def from_parts(system: SystemEnum, arch: ArchEnum) -> "PlatformEnum":
        return PlatformEnum(f"{system.value}-{arch.value}")

    @property
    def system(self) -> SystemEnum:
        return SystemEnum(self.value.split("-")[0])

    @property
    def arch(self) -> ArchEnum:
        return ArchEnum(self.value.split("-")[1])

    @property
    def extension(self) -> str:
        return self.system.extension

    def triple(self, msvc: bool=Environment.flag("MSVC")) -> Optional[str]:
        """Get the Rust target triple"""
        return {
            self.WindowsAMD64: "x86_64-pc-windows-"  + ("msvc" if msvc else "gnu"),
            self.WindowsARM64: "aarch64-pc-windows-" + ("msvc" if msvc else "gnullvm"),
            self.LinuxAMD64:   "x86_64-unknown-linux-gnu",
            self.LinuxARM64:   "aarch64-unknown-linux-gnu",
            self.MacosAMD64:   "x86_64-apple-darwin",
            self.MacosARM64:   "aarch64-apple-darwin",
        }.get(self, None)

    @staticmethod
    def all_host() -> Iterable[Self]:
        for option in PlatformEnum:
            if (option.system == BrokenPlatform.System):
                yield option

    @property
    def pip_platform(self) -> Iterable[str]:

        # https://en.wikipedia.org/wiki/MacOS_version_history
        def mac_versions() -> Iterable[str]:
            for minor in range(0, 16):
                yield (10, minor)
            for major in range(11, 16):
                yield (major, 0)

        # We MUST output ALL the platforms
        if (self == self.WindowsAMD64):
            yield "win_amd64"

        elif (self == self.WindowsARM64):
            yield "win_arm64"

        elif (self == self.LinuxAMD64):
            yield "linux_x86_64"
            yield "manylinux2014_x86_64"
            yield "manylinux2010_x86_64"
            yield "manylinux1_x86_64"

        elif (self == self.LinuxARM64):
            yield "manylinux2014_aarch64"
            yield "linux_aarch64"

        elif (self == self.MacosAMD64):
            for (major, minor) in reversed(list(mac_versions())):
                yield f"macosx_{major}_{minor}_x86_64"

        elif (self == self.MacosARM64):
            for (major, minor) in reversed(list(mac_versions())):
                yield f"macosx_{major}_{minor}_arm64"


class BrokenPlatform:
    Arch: ArchEnum = ArchEnum.get(
        platform.machine().lower())
    """The current machine's architecture"""

    System: SystemEnum = SystemEnum.get(
        platform.system().lower())
    """The current machine's operating system"""

    Host: PlatformEnum = PlatformEnum.from_parts(System, Arch)
    """The current machine's full platform"""

    # Primary platforms
    OnLinux:   bool = (System == SystemEnum.Linux)
    OnWindows: bool = (System == SystemEnum.Windows)
    OnMacOS:   bool = (System == SystemEnum.MacOS)
    OnBSD:     bool = (System == SystemEnum.BSD)

    # Distro IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro: str = (distro.id() if OnLinux else "")

    # Family of platforms
    OnUnix: bool = (OnLinux or OnMacOS or OnBSD)

    # Ubuntu family
    OnUbuntu:    bool = (LinuxDistro == "ubuntu")
    OnDebian:    bool = (LinuxDistro == "debian")
    OnMint:      bool = (LinuxDistro == "linuxmint")
    OnRaspberry: bool = (LinuxDistro == "raspbian")
    UbuntuLike:  bool = (OnUbuntu or OnDebian or OnMint or OnRaspberry)

    # Arch Linux family
    OnArch:      bool = (LinuxDistro == "arch")
    OnManjaro:   bool = (LinuxDistro == "manjaro")
    OnCachyOS:   bool = (LinuxDistro == "cachyos")
    OnEndeavour: bool = (LinuxDistro == "endeavouros")
    ArchLike:    bool = (OnArch or OnManjaro or OnCachyOS or OnEndeavour)

    # RedHat family
    OnFedora:   bool = (LinuxDistro == "fedora")
    OnCentOS:   bool = (LinuxDistro == "centos")
    OnRedHat:   bool = (LinuxDistro == "rhel")
    FedoraLike: bool = (OnFedora or OnCentOS or OnRedHat)

    # Others
    OnGentoo: bool = (LinuxDistro == "gentoo")

    # BSD family
    OnOpenBSD: bool = (LinuxDistro == "openbsd")
    OnFreeBSD: bool = (LinuxDistro == "freebsd")
    OnNetBSD:  bool = (LinuxDistro == "netbsd")
    BSDLike:   bool = (OnFreeBSD or OnOpenBSD or OnNetBSD)

    # ------------------------------------------ #

    Wayland: bool = (Environment.get("XDG_SESSION_TYPE") == "wayland")
    """Check if the current session is Wayland (False on non-linux)"""

    X11: bool = (Environment.get("XDG_SESSION_TYPE") == "x11")
    """Check if the current session is X11 (False on non-linux)"""

    # ------------------------------------------ #

    @staticmethod
    def log_system_info() -> None:
        log.info(f"• System Info: {platform.system()} {platform.release()}, Python {platform.python_version()} {platform.machine()}")

    @staticmethod
    def clear_terminal() -> None:
        os.system("cls" if BrokenPlatform.OnWindows else "clear")

    # Literally, why Windows/Python have different directory names for scripts? ...
    # https://github.com/pypa/virtualenv/commit/993ba1316a83b760370f5a3872b3f5ef4dd904c1
    PyBinDir = ("Scripts" if OnWindows else "bin")

    try:
        Root: bool = (os.getuid() == 0)
    except AttributeError:
        Root: bool = (ctypes.windll.shell32.IsUserAnAdmin() != 0)

    class DeveloperMode:
        # https://learn.microsoft.com/en-us/windows/apps/get-started/developer-mode-features-and-debugging

        @staticmethod
        def status() -> bool:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "AllowDevelopmentWithoutDevLicense")
            winreg.CloseKey(key)
            return bool(value)

        @staticmethod
        def set(state: bool=True):
            import winreg
            if (not BrokenPlatform.Root):
                raise PermissionError("Administrator privileges are required to enable Developer Mode")
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "AllowDevelopmentWithoutDevLicense", 0, winreg.REG_DWORD, int(state))
            winreg.CloseKey(key)

        @staticmethod
        def enable() -> bool:
            return BrokenPlatform.DeveloperMode.set(True)

        @staticmethod
        def enabled() -> bool:
            return BrokenPlatform.DeveloperMode.status()
