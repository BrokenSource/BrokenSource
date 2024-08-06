import os
import platform

import distro

from Broken import BrokenEnum, log


class BrokenPlatform:
    """
    Host Platform information, Cross Compilation targets and some utilities
    """

    # Name of the current platform - (linux, windows, macos, bsd)
    Name:         str  = platform.system().lower().replace("darwin", "macos")

    # Booleans if the current platform is the following
    OnLinux:      bool = (Name == "linux")
    OnWindows:    bool = (Name == "windows")
    OnMacOS:      bool = (Name == "macos")
    OnBSD:        bool = (Name == "bsd")

    # Platform release binaries extension and CPU architecture
    Extension:    str  = (".exe" if OnWindows else ".bin")
    Architecture: str  = (platform.machine().lower().replace("x86_64", "amd64"))

    # Family of platforms
    OnUnix:       bool = (OnLinux or OnMacOS or OnBSD)

    # Distro IDs: https://distro.readthedocs.io/en/latest/
    LinuxDistro:  str  = distro.id()

    # # Booleans if the current platform is the following

    # Ubuntu-like
    OnUbuntu:     bool = (LinuxDistro == "ubuntu")
    OnDebian:     bool = (LinuxDistro == "debian")
    OnMint:       bool = (LinuxDistro == "linuxmint")
    OnRaspberry:  bool = (LinuxDistro == "raspbian")
    OnUbuntuLike: bool = (OnUbuntu or OnDebian or OnMint or OnRaspberry)

    # Arch-like
    OnArch:       bool = (LinuxDistro == "arch")
    OnManjaro:    bool = (LinuxDistro == "manjaro")
    OnArchLike:   bool = (OnArch or OnManjaro)

    # RedHat-like
    OnFedora:     bool = (LinuxDistro == "fedora")
    OnCentOS:     bool = (LinuxDistro == "centos")
    OnRedHat:     bool = (LinuxDistro == "rhel")
    OnRedHatLike: bool = (OnFedora or OnCentOS or OnRedHat)

    # Others
    OnGentoo:     bool = (LinuxDistro == "gentoo")

    # BSD-like
    OnOpenBSD:    bool = (LinuxDistro == "openbsd")
    OnNetBSD:     bool = (LinuxDistro == "netbsd")
    OnBSDLike:    bool = (OnOpenBSD or OnNetBSD)

    class Targets(BrokenEnum):
        """List of common platforms targets for releases"""
        LinuxAMD64:   str = "linux-amd64"
        LinuxARM:     str = "linux-arm64"
        WindowsAMD64: str = "windows-amd64"
        WindowsARM:   str = "windows-arm64"
        MacosAMD64:   str = "macos-amd64"
        MacosARM:     str = "macos-arm64"

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
            if ("macos" in self.value):
                return ".app"
            return ".bin"

        @property
        def name(self) -> str:
            """Same as BrokenPlatform.Name"""
            return self.value.split("-")[0]

        @property
        def architecture(self) -> str:
            """Same as BrokenPlatform.Architecture"""
            return self.value.split("-")[1]

    CurrentTarget: str = f"{Name}-{Architecture}"

    @staticmethod
    def log_system_info():
        log.info(f"• System Info: {platform.system()} {platform.release()}, Python {platform.python_version()} {platform.machine()}")

    @staticmethod
    def clear_terminal():
        os.system("cls" if BrokenPlatform.OnWindows else "clear")

    # Literally, why Windows/Python have different directory names for scripts? ...
    # https://github.com/pypa/virtualenv/commit/993ba1316a83b760370f5a3872b3f5ef4dd904c1
    PyScripts         = ("Scripts" if OnWindows else "bin")
    PyScriptExtension = (".cmd" if OnWindows else "")
