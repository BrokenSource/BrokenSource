import ctypes
import os
import platform
from collections.abc import Iterable
from typing import Any, Optional, Self

import distro

from broken.enumx import BrokenEnum
from broken.envy import Environment


class SystemEnum(str, BrokenEnum):
    Linux:   str = "linux"
    Windows: str = "windows"
    MacOS:   str = "macos"
    BSD:     str = "bsd"

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value in ("win32", "win", "windows", "cygwin"):
            return cls.Windows
        if value in ("darwin", "macos", "osx"):
            return cls.MacOS
        if ("bsd" in value):
            return cls.BSD
        return None

    def is_linux(self) -> bool:
        return (self is self.Linux)

    def is_windows(self) -> bool:
        return (self is self.Windows)

    def is_macos(self) -> bool:
        return (self is self.MacOS)

    def is_bsd(self) -> bool:
        return (self is self.BSD)

    def is_unix(self) -> bool:
        return any((
            self.is_linux(),
            self.is_macos(),
            self.is_bsd(),
        ))

    @property
    def extension(self) -> str:
        if (self is self.Windows):
            return ".exe"
        return ".bin"


class ArchEnum(str, BrokenEnum):
    AMD32: str = "amd32"
    AMD64: str = "amd64"
    ARM32: str = "arm32"
    ARM64: str = "arm64"

    @classmethod
    def _missing_(cls, value: object):
        if value in ("x86", "i686"):
            return cls.AMD32
        elif value in ("x86_64",):
            return cls.AMD64
        return None

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
    LinuxAMD64:   str = "linux-amd64"
    LinuxARM64:   str = "linux-arm64"
    WindowsAMD64: str = "windows-amd64"
    WindowsARM64: str = "windows-arm64"
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
            if (option.system == Host.System):
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


class Host:
    Arch: ArchEnum = ArchEnum.get(platform.machine().lower())
    """The current machine's architecture"""

    System: SystemEnum = SystemEnum.get(platform.system().lower())
    """The current machine's operating system"""

    Platform: PlatformEnum = PlatformEnum.from_parts(System, Arch)
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

    # -------------------------------- #

    Wayland: bool = (Environment.get("XDG_SESSION_TYPE") == "wayland")
    """Current windowing session protocol is Wayland"""

    X11: bool = (Environment.get("XDG_SESSION_TYPE") == "x11")
    """Current windowing session protocol is X11"""

    # -------------------------------- #

    @staticmethod
    def clear_terminal() -> None:
        os.system("cls" if Host.OnWindows else "clear")

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
            if (not Host.Root):
                raise PermissionError("Administrator privileges are required to enable Developer Mode")
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "AllowDevelopmentWithoutDevLicense", 0, winreg.REG_DWORD, int(state))
            winreg.CloseKey(key)

        @staticmethod
        def enable() -> bool:
            return Host.DeveloperMode.set(True)

        @staticmethod
        def enabled() -> bool:
            return Host.DeveloperMode.status()
