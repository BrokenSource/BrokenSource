from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

from attr import define, field
from platformdirs import PlatformDirs

import Broken
from Broken import BrokenLogging, Environment, Runtime, log
from Broken.Core import BrokenCache, arguments, list_get
from Broken.Core.BrokenPath import BrokenPath
from Broken.Core.BrokenPlatform import BrokenPlatform
from Broken.Core.BrokenTrackers import FileTracker

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenProject:
    PACKAGE: Path = field(converter=lambda x: Path(x).parent)
    """Send the importer's __init__.py's __file__ variable"""

    # App information
    APP_NAME: str
    APP_AUTHOR: str
    VERSION: str = Runtime.Version
    ABOUT: str = "No description provided"

    # Refactored functionality
    DIRECTORIES: _Directories = None
    RESOURCES: _Resources = None

    def __attrs_post_init__(self):
        BrokenLogging.set_project(self.APP_NAME)

        # Print version information and quit if requested
        if (list_get(sys.argv, 1) in ("--version", "-V")):
            print(f"{self.APP_NAME} {self.VERSION} {BrokenPlatform.Host.value}")
            sys.exit(0)

        # Create refactored classes
        self.DIRECTORIES = _Directories(PROJECT=self)
        self.RESOURCES = _Resources(PROJECT=self)

        # Replace Broken.PROJECT with the first initialized project
        if (project := getattr(Broken, "PROJECT", None)):
            if (project is Broken.BROKEN):
                if (BrokenPlatform.Root and not Runtime.Docker):
                    log.warn("Running as [bold blink red]Administrator or Root[/] is discouraged unless necessary!")
                Broken.PROJECT = self

        # Convenience symlink the project's workspace
        if Runtime.Source and Environment.flag("WORKSPACE_SYMLINK", 0):
            BrokenPath.symlink(
                virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
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
    def REPO_RELEASES(self) -> Path:
        return (self.REPOSITORY/"Release")

    @property
    def REPO_BUILD(self) -> Path:
        return (self.REPOSITORY/"Build")

    @property
    def REPO_DOCKER(self) -> Path:
        return (self.REPOSITORY/"Docker")

    @property
    def BUILD_WHEELS(self) -> Path:
        return (self.REPO_BUILD/"Wheels")

    @property
    def BUILD_CARGO(self) -> Path:
        return (self.REPO_BUILD/"Cargo")

    # # Meta directories

    @property
    def REPO_META(self) -> Path:
        return (self.REPOSITORY/"Meta")

    @property
    def INSIDERS(self) -> Path:
        return (self.REPO_META/"Insiders")

    @property
    def REPO_WEBSITE(self) -> Path:
        return (self.REPOSITORY/"Website")

    @property
    def REPO_EXAMPLES(self) -> Path:
        return (self.REPOSITORY/"Examples")

    @property
    def REPO_PROJECTS(self) -> Path:
        return (self.REPOSITORY/"Projects")

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
        return (self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        return (self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        return (self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        return (self.WORKSPACE/"Data")

    @property
    def PROJECTS(self) -> Path:
        return (self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        return (self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        return (self.WORKSPACE/"Downloads")

    @property
    def TEMP(self) -> Path:
        return (self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        return (self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        return (self.WORKSPACE/"Screenshots")

    # # Third party dependencies

    @property
    def EXTERNALS(self) -> Path:
        return (self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_MODELS(self) -> Path:
        return (self.EXTERNALS/"Models")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        return (self.EXTERNALS/"Archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        return (self.EXTERNALS/"Images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        return (self.EXTERNALS/"Audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        return (self.EXTERNALS/"Fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        return (self.EXTERNALS/"Soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        return (self.EXTERNALS/"Midis")

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class _Resources:
    PROJECT: BrokenProject
    ROOT: Path = None
    """The path of the resources package"""

    def __attrs_post_init__(self):
        self.ROOT = (self.PROJECT.PACKAGE/"Resources")

    def __div__(self, name: str) -> Path:
        return (self.ROOT/name)

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Bundled items

    @property
    def EXAMPLES(self) -> Path:
        return (self.ROOT/"Examples")

    # # Common section

    @property
    def IMAGES(self) -> Path:
        return (self.ROOT/"Images")

    @property
    def AUDIO(self) -> Path:
        return (self.ROOT/"Audio")

    @property
    def FONTS(self) -> Path:
        return (self.ROOT/"Fonts")

    @property
    def TEMPLATES(self) -> Path:
        return (self.ROOT/"Templates")

    # # Branding section

    @property
    def ICON_PNG(self) -> Path:
        return (self.IMAGES)/f"{self.PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        return (self.IMAGES)/f"{self.PROJECT.APP_NAME}.ico"

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        return (self.ROOT/"Scenes")

    @property
    def SHADERS(self) -> Path:
        return (self.ROOT/"Shaders")

    @property
    def SHADERS_INCLUDE(self) -> Path:
        return (self.SHADERS/"Include")

    @property
    def FRAGMENT(self) -> Path:
        return (self.SHADERS/"Fragment")

    @property
    def VERTEX(self) -> Path:
        return (self.SHADERS/"Vertex")
