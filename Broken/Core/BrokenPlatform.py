import ctypes
import os
import platform
from typing import Generator, List, Self
from aenum import MultiValueEnum

import distro

from Broken.Core.BrokenLogging import log
from Broken.Core.BrokenEnum import MultiEnum, BrokenEnum


class SystemEnum(str, MultiEnum):
    Linux:   str = "linux"
    Windows: str = "windows"
    MacOS:   str = ("macos", "darwin")
    BSD:     str = "bsd"

    @property
    def extension(self) -> str:
        if (self == self.Windows):
            return ".exe"
        return ".bin"

    def is_linux(self) -> bool:
        return (self == self.Linux)

    def is_windows(self) -> bool:
        return (self == self.Windows)

    def is_macos(self) -> bool:
        return (self == self.MacOS)

    def is_bsd(self) -> bool:
        return (self == self.BSD)


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


class Platform(str, BrokenEnum):
    """List of common platforms targets for releases"""
    WindowsAMD64: str = "windows-amd64"
    WindowsARM64: str = "windows-arm64"
    LinuxAMD64:   str = "linux-amd64"
    LinuxARM64:   str = "linux-arm64"
    MacosAMD64:   str = "macos-amd64"
    MacosARM64:   str = "macos-arm64"

    @property
    def system(self) -> SystemEnum:
        return SystemEnum(self.value.split("-")[0])

    @property
    def arch(self) -> ArchEnum:
        return ArchEnum(self.value.split("-")[1])

    @property
    def extension(self) -> str:
        return self.system.extension

    @property
    def triple(self) -> str:
        """Get the Rust target triple"""
        return {
            self.WindowsAMD64: "x86_64-pc-windows-" + ("msvc" if BrokenPlatform.OnWindows else "gnu"),
            self.WindowsARM64: "aarch64-pc-windows-" + ("msvc" if BrokenPlatform.OnWindows else "gnullvm"),
            self.LinuxAMD64:   "x86_64-unknown-linux-gnu",
            self.LinuxARM64:   "aarch64-unknown-linux-gnu",
            self.MacosAMD64:   "x86_64-apple-darwin",
            self.MacosARM64:   "aarch64-apple-darwin",
        }[self]

    _AllAMD64: str = "all-amd64"
    _AllARM64: str = "all-arm64"
    _AllHost:  str = "all-host"
    _All:      str = "all"

    def get_all(self) -> Generator[Self, None, None]:
        if ("all" in self.value):
            for option in Platform.options():
                if ("all" in option.value):
                    continue
                elif (self == self._All):
                    yield option
                elif (self == self._AllAMD64):
                    if (option.arch == ArchEnum.AMD64):
                        yield option
                elif (self == self._AllARM64):
                    if (option.arch == ArchEnum.ARM64):
                        yield option
                elif (self == self._AllHost):
                    if (option.system == BrokenPlatform.System):
                        yield option
        else:
            yield self

class BrokenPlatform:
    Arch: ArchEnum = ArchEnum.get(
        platform.machine().lower())

    System: SystemEnum = SystemEnum.get(
        platform.system().lower())

    Host: Platform = Platform.get(
        f"{System.value}-{Arch.value}")

    # Booleans if the current platform is the following
    OnLinux:   bool = (System == SystemEnum.Linux)
    OnWindows: bool = (System == SystemEnum.Windows)
    OnMacOS:   bool = (System == SystemEnum.MacOS)
    OnBSD:     bool = (System == SystemEnum.BSD)

    # Distro IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro: str = distro.id()

    # Family of platforms
    OnUnix: bool = (OnLinux or OnMacOS or OnBSD)

    # Ubuntu-like
    OnUbuntu:    bool = (LinuxDistro == "ubuntu")
    OnDebian:    bool = (LinuxDistro == "debian")
    OnMint:      bool = (LinuxDistro == "linuxmint")
    OnRaspberry: bool = (LinuxDistro == "raspbian")
    UbuntuLike:  bool = (OnUbuntu or OnDebian or OnMint or OnRaspberry)

    # Arch-like
    OnArch:    bool = (LinuxDistro == "arch")
    OnManjaro: bool = (LinuxDistro == "manjaro")
    ArchLike:  bool = (OnArch or OnManjaro)

    # RedHat-like
    OnFedora:   bool = (LinuxDistro == "fedora")
    OnCentOS:   bool = (LinuxDistro == "centos")
    OnRedHat:   bool = (LinuxDistro == "rhel")
    FedoraLike: bool = (OnFedora or OnCentOS or OnRedHat)

    # Others
    OnGentoo: bool = (LinuxDistro == "gentoo")

    # BSD-like
    OnFreeBSD: bool = (LinuxDistro == "freebsd")
    OnOpenBSD: bool = (LinuxDistro == "openbsd")
    OnBSDLike: bool = (OnFreeBSD or OnOpenBSD)

    @staticmethod
    def log_system_info():
        log.info(f"• System Info: {platform.system()} {platform.release()}, Python {platform.python_version()} {platform.machine()}")

    @staticmethod
    def clear_terminal():
        os.system("cls" if BrokenPlatform.OnWindows else "clear")

    # Literally, why Windows/Python have different directory names for scripts? ...
    # https://github.com/pypa/virtualenv/commit/993ba1316a83b760370f5a3872b3f5ef4dd904c1
    PyBinDir = ("Scripts" if OnWindows else "bin")

    try:
        Administrator: bool = (os.getuid() == 0)
    except AttributeError:
        Administrator: bool = ctypes.windll.shell32.IsUserAnAdmin() != 0

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
            if (not BrokenPlatform.Administrator):
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
