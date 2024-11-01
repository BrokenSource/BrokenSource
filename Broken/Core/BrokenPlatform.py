import ctypes
import os
import platform
from typing import Generator, Self

import distro

from Broken import BrokenEnum, log


class BrokenPlatform:
    """
    Host Platform information, Cross Compilation targets and some utilities
    """

    class SystemEnum(str, BrokenEnum):
        Linux:   str = "linux"
        Windows: str = "windows"
        MacOS:   str = "macos"
        BSD:     str = "bsd"

    System: SystemEnum = SystemEnum.get(platform.system().lower().replace("darwin", "macos"))
    """Current operating system"""

    @property
    def Name(self) -> str:
        """Name of the current platform - (linux, windows, macos, bsd)"""
        return self.System.value

    # Booleans if the current platform is the following
    OnLinux:   bool = (System == SystemEnum.Linux)
    OnWindows: bool = (System == SystemEnum.Windows)
    OnMacOS:   bool = (System == SystemEnum.MacOS)
    OnBSD:     bool = (System == SystemEnum.BSD)

    # Family of platforms
    OnUnix: bool = (OnLinux or OnMacOS or OnBSD)

    # Distro IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro: str = distro.id()

    # # Booleans if the current platform is the following

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

    # Platform release binaries extension and CPU architecture
    class ArchEnum(str, BrokenEnum):
        AMD64: str = "amd64"
        ARM64: str = "arm64"

    Arch: ArchEnum = ArchEnum.get(platform.machine().lower().replace("x86_64", "amd64"))
    Extension: str = (".exe" if OnWindows else ".bin")

    class Target(BrokenEnum):
        """List of common platforms targets for releases"""
        LinuxAMD64:   str = "linux-amd64"
        LinuxARM:     str = "linux-arm64"
        WindowsAMD64: str = "windows-amd64"
        WindowsARM:   str = "windows-arm64"
        MacosAMD64:   str = "macos-amd64"
        MacosARM:     str = "macos-arm64"
        All:          str = "all"

        @staticmethod
        def all() -> Generator[Self, None, None]:
            for target in BrokenPlatform.Target.options():
                if target != BrokenPlatform.Target.All:
                    yield target

        @property
        def rust(self) -> str:
            windows_compiler = ("msvc" if BrokenPlatform.OnWindows else "gnu")
            return {
                self.LinuxAMD64:   "x86_64-unknown-linux-gnu",
                self.LinuxARM:     "aarch64-unknown-linux-gnu",
                self.WindowsAMD64: "x86_64-pc-windows-" + windows_compiler,
                self.WindowsARM:   "aarch64-pc-windows-" + windows_compiler,
                self.MacosAMD64:   "x86_64-apple-darwin",
                self.MacosARM:     "aarch64-apple-darwin",
            }[self]

        @property
        def extension(self) -> str:
            """Same as BrokenPlatform.Extension"""
            if ("windows" in self.value):
                return ".exe"
            return ".bin"

        @property
        def name(self) -> str:
            """Same as BrokenPlatform.Name"""
            return self.value.split("-")[0]

        @property
        def architecture(self) -> str:
            """Same as BrokenPlatform.Architecture"""
            return self.value.split("-")[1]

    CurrentTarget: Target = Target.get(f"{System}-{Arch}")

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
