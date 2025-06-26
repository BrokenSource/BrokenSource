from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

from attr import define, field
from platformdirs import PlatformDirs

import broken
from broken import BrokenLogging, Environment, Runtime, log
from broken.core import list_get
from broken.core.path import BrokenPath
from broken.core.system import BrokenPlatform

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenProject:
    PACKAGE: Path = field(converter=lambda x: Path(x).parent)
    """Send the importer's `__init__.py`'s `__file__` variable"""

    # App information
    APP_NAME:   str
    APP_AUTHOR: str = "BrokenSource"
    VERSION:    str = Runtime.Version
    ABOUT:      str = "No description provided"

    # Refactored functionality
    DIRECTORIES: _Directories = None
    RESOURCES: _Resources = None

    def __attrs_post_init__(self):

        # Print version information and quit if requested
        if (list_get(sys.argv, 1) in ("--version", "-V")):
            print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.Host.value}")
            sys.exit(0)

        # Create refactored classes
        self.DIRECTORIES = _Directories(PROJECT=self)
        self.RESOURCES = _Resources(PROJECT=self)

        # Replace with the first initialized project
        if (project := getattr(broken, "PROJECT", None)):
            if (project is broken.BROKEN):
                if (BrokenPlatform.Root and not Runtime.Docker):
                    log.warn("Running as [bold blink red]Administrator or Root[/] is discouraged unless necessary!")
                BrokenLogging.set_project(self.APP_NAME)
                broken.PROJECT = self

        # Convenience symlink the project's workspace
        if Runtime.Source and Environment.flag("WORKSPACE_SYMLINK", 0):
            BrokenPath.symlink(
                virtual=self.DIRECTORIES.REPOSITORY/"workspace",
                real=self.DIRECTORIES.WORKSPACE, echo=False
            )

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Directories:
    PROJECT: BrokenProject
    APP_DIRS: PlatformDirs = None

    def __attrs_post_init__(self):
        args = (self.PROJECT.APP_AUTHOR, self.PROJECT.APP_NAME)
        args = (reversed(args) if (os.name == "nt") else args)
        self.APP_DIRS = PlatformDirs(*args)

    # # Unknown / new project directories

    def _new_directory(self, name: str, value: Path) -> Path:
        """Create a new directory property if Path is given, else set the value"""
        self.__dict__[name] = (value if not isinstance(value, Path) else value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self._new_directory(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self._new_directory(name, value)

    # # Base directories

    @property
    def SYSTEM_TEMP(self) -> Path:
        return (
            Path(tempfile.gettempdir()) /
            self.PROJECT.APP_AUTHOR /
            self.PROJECT.APP_NAME
        )

    @property
    def REPOSITORY(self) -> Path:
        return Path(self.PROJECT.PACKAGE).parent

    # # Repository specific

    @property
    def REPO_DOCKER(self) -> Path:
        return (self.REPOSITORY/"docker")

    @property
    def REPO_BUILD(self) -> Path:
        return (self.REPOSITORY/"build")

    @property
    def BUILD_WHEELS(self) -> Path:
        return (self.REPO_BUILD/"wheels")

    @property
    def BUILD_CARGO(self) -> Path:
        return (self.REPO_BUILD/"cargo")

    @property
    def REPO_RELEASES(self) -> Path:
        return (self.REPOSITORY/"release")

    # # Meta directories

    @property
    def REPO_META(self) -> Path:
        return (self.REPOSITORY/"meta")

    @property
    def INSIDERS(self) -> Path:
        return (self.REPO_META/"insiders")

    @property
    def REPO_WEBSITE(self) -> Path:
        return (self.REPOSITORY/"website")

    @property
    def REPO_EXAMPLES(self) -> Path:
        return (self.REPOSITORY/"examples")

    @property
    def REPO_PROJECTS(self) -> Path:
        return (self.REPOSITORY/"projects")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        if (path := Environment.get("WORKSPACE")):
            return (Path(path) / self.PROJECT.APP_NAME)
        elif (os.name == "nt"):
            return Path(self.APP_DIRS.user_data_dir)
        return (
            Path(self.APP_DIRS.user_data_dir) /
            self.PROJECT.APP_NAME
        )

    @property
    def WORKSPACE_ROOT(self) -> Path:
        return self.WORKSPACE.parent

    @property
    def CONFIG(self) -> Path:
        return (self.WORKSPACE/"config")

    @property
    def LOGS(self) -> Path:
        return (self.WORKSPACE/"logs")

    @property
    def CACHE(self) -> Path:
        return (self.WORKSPACE/"cache")

    @property
    def DATA(self) -> Path:
        return (self.WORKSPACE/"data")

    @property
    def PROJECTS(self) -> Path:
        return (self.WORKSPACE/"projects")

    @property
    def OUTPUT(self) -> Path:
        return (self.WORKSPACE/"output")

    @property
    def DOWNLOADS(self) -> Path:
        return (self.WORKSPACE/"downloads")

    @property
    def TEMP(self) -> Path:
        return (self.WORKSPACE/"temp")

    @property
    def DUMP(self) -> Path:
        return (self.WORKSPACE/"dump")

    @property
    def SCREENSHOTS(self) -> Path:
        return (self.WORKSPACE/"screenshots")

    # # Third party dependencies

    @property
    def EXTERNALS(self) -> Path:
        return (self.WORKSPACE/"externals")

    @property
    def EXTERNAL_MODELS(self) -> Path:
        return (self.EXTERNALS/"models")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        return (self.EXTERNALS/"archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        return (self.EXTERNALS/"images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        return (self.EXTERNALS/"audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        return (self.EXTERNALS/"fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        return (self.EXTERNALS/"soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        return (self.EXTERNALS/"midis")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Resources:
    PROJECT: BrokenProject
    ROOT: Path = None
    """The path of the resources package"""

    def __attrs_post_init__(self):
        self.ROOT = (self.PROJECT.PACKAGE/"resources")

    def __div__(self, name: str) -> Path:
        return (self.ROOT/name)

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Bundled items

    @property
    def EXAMPLES(self) -> Path:
        return (self.ROOT/"examples")

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return (self.ROOT/"images")

    @property
    def AUDIO(self) -> Path:
        return (self.ROOT/"audio")

    @property
    def FONTS(self) -> Path:
        return (self.ROOT/"fonts")

    @property
    def TEMPLATES(self) -> Path:
        return (self.ROOT/"templates")

    # # Branding section

    @property
    def ICON_PNG(self) -> Path:
        return (self.IMAGES/"logo.png")

    @property
    def ICON_ICO(self) -> Path:
        return (self.IMAGES/"logo.ico")

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        return (self.ROOT/"scenes")

    @property
    def SHADERS(self) -> Path:
        return (self.ROOT/"shaders")

    @property
    def SHADERS_INCLUDE(self) -> Path:
        return (self.SHADERS/"include")

    @property
    def FRAGMENT(self) -> Path:
        return (self.SHADERS/"fragment")

    @property
    def VERTEX(self) -> Path:
        return (self.SHADERS/"vertex")
