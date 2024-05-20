from __future__ import annotations

import importlib.metadata
import importlib.resources
import os
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

import diskcache
import dotenv
from appdirs import AppDirs
from attr import define, field
from loguru import logger as log
from rich import print as rprint
from rich.align import Align
from rich.panel import Panel
from typer import Typer

import Broken
from Broken import BrokenLogging, BrokenPath


@define(slots=False)
class _BrokenProjectDirectories:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # App basic information
    APP_DIRS: AppDirs = field(default=None)

    def __attrs_post_init__(self):
        args = (self.BROKEN_PROJECT.APP_AUTHOR, self.BROKEN_PROJECT.APP_NAME)
        self.APP_DIRS = AppDirs(*reversed(args) if (os.name == "nt") else args)

    def mkdir(self, path: Path, resolve: bool=True) -> Path:
        """Make a directory and return it"""
        path = Path(path).resolve() if resolve else Path(path)
        if not path.exists():
            log.info(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def PACKAGE(self) -> Path:
        """
        When running from the Source Code:
            - The current project's __init__.py location

        When running from a Release:
            - Directory where the executable is located
        """
        if Broken.RELEASE:
            return Path(sys.executable).parent.resolve()

        return Path(self.BROKEN_PROJECT.PACKAGE).parent.resolve()

    # # Convenience properties

    @property
    def APP_NAME(self) -> str:
        return self.BROKEN_PROJECT.APP_NAME

    @property
    def APP_AUTHOR(self) -> str:
        return self.BROKEN_PROJECT.APP_AUTHOR

    # # Unknown / new project directories

    def __set__(self, name: str, value: Path) -> Path:
        """Create a new directory property if Path is given, else set the value"""
        self.__dict__[name] = value if not isinstance(value, Path) else self.mkdir(value)

    def __setattr__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    def __setitem__(self, name: str, value: Path) -> Path:
        self.__set__(name, value)

    # # Base directories

    @property
    def REPOSITORY(self) -> Path:
        """Broken Source's Monorepo directory"""
        return self.mkdir(self.PACKAGE.parent)

    @property
    def HOME(self) -> Path:
        """(Unix: /home/$USER), (Windows: C://Users//$USER)"""
        return self.mkdir(Path.home())

    # # Common system directories

    @property
    def SYSTEM_ROOT(self) -> Path:
        """(Unix: /), (Windows: C://)"""
        return self.mkdir("/")

    @property
    def SYSTEM_TEMP(self) -> Path:
        """(Unix: /tmp), (Windows: C://Windows//Temp)"""
        return self.mkdir(tempfile.gettempdir())

    # # Broken monorepo specific, potentially useful

    @property
    def BROKEN_RELEASES(self) -> Path:
        """Broken Source's Monorepo general Releases directory"""
        return self.mkdir(self.REPOSITORY/"Release")

    @property
    def BROKEN_BUILD(self) -> Path:
        """Broken Source's Monorepo general Build directory"""
        return self.mkdir(self.REPOSITORY/"Build")

    @property
    def BROKEN_WINEPREFIX(self) -> Path:
        """Broken Source's Monorepo Wineprefix directory for Build"""
        return self.mkdir(self.BROKEN_BUILD/"Wineprefix")

    @property
    def BROKEN_WHEELS(self) -> Path:
        """Broken Source's Monorepo Wheels directory for Build"""
        return self.mkdir(self.BROKEN_BUILD/"Wheels")

    @property
    def BROKEN_PROJECTS(self) -> Path:
        """Broken Source's Monorepo Projects directory"""
        return self.mkdir(self.REPOSITORY/"Projects")

    @property
    def BROKEN_HOOK(self) -> Path:
        """Hook directory for other projects to be managed by Broken"""
        return self.mkdir(self.PROJECTS/"Hook")

    @property
    def BROKEN_META(self) -> Path:
        """Broken Source's Monorepo Meta directory (Many submodules there)"""
        return self.mkdir(self.REPOSITORY/"Meta")

    @property
    def BROKEN_FORK(self) -> Path:
        """Broken Source's Monorepo Forks directory"""
        return self.mkdir(self.BROKEN_META/"Fork")

    @property
    def BROKEN_PRIVATE(self) -> Path:
        """Broken Source's Monorepo Private directory"""
        return self.mkdir(self.REPOSITORY/"Private")

    # # Meta directories - Broken monorepo specific

    @property
    def DOCS(self) -> Path:
        """Broken Source's Monorepo Docs directory"""
        return self.mkdir(self.REPOSITORY/"Docs")

    @property
    def WEBSITE(self) -> Path:
        """Broken Source's Website directory"""
        return self.mkdir(self.REPOSITORY/"Website")

    @property
    def PAPERS(self) -> Path:
        """Broken Source's Monorepo Papers directory"""
        return self.mkdir(self.META/"Papers")

    @property
    def TEMPLATES(self) -> Path:
        """Broken Source's Monorepo Templates directory"""
        return self.mkdir(self.META/"Templates")

    # # Workspace directories

    @property
    def WORKSPACE(self) -> Path:
        """Root for the current Project's Workspace"""
        if (path := os.environ.get("WORKSPACE", None)):
            return self.mkdir(Path(path)/self.APP_AUTHOR/self.APP_NAME)
        if (os.name == "nt"):
            return self.mkdir(Path(self.APP_DIRS.user_data_dir))
        else:
            return self.mkdir(Path(self.APP_DIRS.user_data_dir)/self.APP_NAME)

    @property
    def CONFIG(self) -> Path:
        """General config directory"""
        return self.mkdir(self.WORKSPACE/"Config")

    @property
    def LOGS(self) -> Path:
        """General logs directory"""
        return self.mkdir(self.WORKSPACE/"Logs")

    @property
    def CACHE(self) -> Path:
        """General cache directory"""
        return self.mkdir(self.WORKSPACE/"Cache")

    @property
    def DATA(self) -> Path:
        """General Data directory"""
        return self.mkdir(self.WORKSPACE/"Data")

    @property
    def MOCK(self) -> Path:
        """Mock directory for testing"""
        return self.mkdir(self.WORKSPACE/"Mock")

    @property
    def PROJECTS(self) -> Path:
        """Projects directory (e.g. Video Editor or IDEs)"""
        return self.mkdir(self.WORKSPACE/"Projects")

    @property
    def OUTPUT(self) -> Path:
        """Output directory if it makes more sense than .DATA or .PROJECTS"""
        return self.mkdir(self.WORKSPACE/"Output")

    @property
    def DOWNLOADS(self) -> Path:
        """Downloads directory"""
        return self.mkdir(self.WORKSPACE/"Downloads")

    @property
    def EXTERNALS(self) -> Path:
        """Third party dependencies"""
        return self.mkdir(self.WORKSPACE/"Externals")

    @property
    def EXTERNAL_ARCHIVES(self) -> Path:
        """Third party archives"""
        return self.mkdir(self.EXTERNALS/"Archives")

    @property
    def EXTERNAL_IMAGES(self) -> Path:
        """Third party images"""
        return self.mkdir(self.EXTERNALS/"Images")

    @property
    def EXTERNAL_AUDIO(self) -> Path:
        """Third party audio"""
        return self.mkdir(self.EXTERNALS/"Audio")

    @property
    def EXTERNAL_FONTS(self) -> Path:
        """Third party fonts"""
        return self.mkdir(self.EXTERNALS/"Fonts")

    @property
    def EXTERNAL_SOUNDFONTS(self) -> Path:
        """Third party soundfonts"""
        return self.mkdir(self.EXTERNALS/"Soundfonts")

    @property
    def EXTERNAL_MIDIS(self) -> Path:
        """Third party midis"""
        return self.mkdir(self.EXTERNALS/"Midis")

    @property
    def TEMP(self) -> Path:
        """Temporary directory for working files"""
        return self.mkdir(self.WORKSPACE/"Temp")

    @property
    def DUMP(self) -> Path:
        """Dump directory for debugging (e.g. Shaders)"""
        return self.mkdir(self.WORKSPACE/"Dump")

    @property
    def SCREENSHOTS(self) -> Path:
        """Screenshots directory"""
        return self.mkdir(self.WORKSPACE/"Screenshots")

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class _BrokenProjectResources:
    """# Info: You shouldn't really use this class directly"""

    # Note: A reference to the main BrokenProject
    BROKEN_PROJECT: BrokenProject

    # # Internal states

    __RESOURCES__: Path = field(default=None)

    def __attrs_post_init__(self):
        if self.BROKEN_PROJECT.RESOURCES:

            # Fixme (#spec): Python 3.9 workaround; Spec-less packages
            if (sys.version_info < (3, 10)):
                spec = self.BROKEN_PROJECT.RESOURCES.__spec__
                spec.origin = spec.submodule_search_locations[0] + "/WorkaroundIgnore"

            self.__RESOURCES__ = importlib.resources.files(self.BROKEN_PROJECT.RESOURCES)

    def __div__(self, name: str) -> Path:
        return self.__RESOURCES__/name

    def __truediv__(self, name: str) -> Path:
        return self.__div__(name)

    # # Common section

    @property
    def IMAGES(self) -> Path:
        """Images directory"""
        return self.__RESOURCES__/"Images"

    @property
    def AUDIO(self) -> Path:
        """Audio directory"""
        return self.__RESOURCES__/"Audio"

    # # Branding section

    @property
    def ICON(self) -> Path:
        """Application icon in PNG format"""
        return self.IMAGES/f"{self.BROKEN_PROJECT.APP_NAME}.png"

    @property
    def ICON_ICO(self) -> Path:
        """Application icon in ICO format"""
        return self.IMAGES/f"{self.BROKEN_PROJECT.APP_NAME}.ico"

    # # Shaders section

    @property
    def SCENES(self) -> Path:
        """Scenes directory"""
        return self.__RESOURCES__/"Scenes"

    @property
    def SHADERS(self) -> Path:
        """Shaders directory - May you use .FRAGMENT and .VERTEX?"""
        return self.__RESOURCES__/"Shaders"

    @property
    def SHADERS_INCLUDE(self) -> Path:
        """Shaders include directory"""
        return self.SHADERS/"Include"

    @property
    def FRAGMENT(self) -> Path:
        """Fragment shaders directory"""
        return self.SHADERS/"Fragment"

    @property
    def VERTEX(self) -> Path:
        """Vertex shaders directory"""
        return self.SHADERS/"Vertex"

    # # Generic

    @property
    def PROMPTS(self) -> Path:
        """Prompts directory"""
        return self.__RESOURCES__/"Prompts"

    @property
    def FONTS(self) -> Path:
        """Fonts directory"""
        return self.__RESOURCES__/"Fonts"

# -------------------------------------------------------------------------------------------------|

@define(slots=False)
class BrokenProject:
    # Note: Send the importer's __init__.py's __file__ variable
    PACKAGE: str

    # App information
    APP_NAME:   str = field(default="Broken")
    APP_AUTHOR: str = field(default="BrokenSource")

    # Standard Broken objects for a project
    DIRECTORIES: _BrokenProjectDirectories = None
    RESOURCES:   _BrokenProjectResources   = None
    VERSION:     str                       = None

    def __attrs_post_init__(self):

        # Create Directories class
        self.DIRECTORIES = _BrokenProjectDirectories(BROKEN_PROJECT=self)
        self.RESOURCES   = _BrokenProjectResources  (BROKEN_PROJECT=self)
        self.PACKAGE     = Path(self.PACKAGE)

        # Fixme (#spec): Split the projects into many packages
        # self.VERSION = importlib.metadata.version(self.PACKAGE.parent.name.replace("Broken", "broken-source"))
        self.VERSION = Broken.VERSION
        BrokenLogging.set_project(self.APP_NAME)

        # Convenience: Symlink Workspace to projects data directory
        if Broken.DEVELOPMENT:
            try:
                BrokenPath.symlink(
                    virtual=self.DIRECTORIES.REPOSITORY/"Workspace",
                    real=self.DIRECTORIES.WORKSPACE,
                    echo=False
                )
            except Exception as e:
                log.minor(f"Failed to symlink Workspace: {e}")

        # Load .env files from the project
        for env in self.DIRECTORIES.REPOSITORY.glob("*.env"):
            dotenv.load_dotenv(env)

        if (os.environ.get("WELCOME", "0") == "1") and (self.APP_NAME != "Broken"):
            self.welcome()

    def welcome(self):
        """Pretty Welcome Message!"""
        import pyfiglet

        # Build message
        ascii = pyfiglet.figlet_format(self.APP_NAME, font="dos_rebel", width=1000)
        ascii = '\n'.join((x for x in ascii.split('\n') if x.strip()))

        # Print panel center-justified lines
        rprint(Panel(
            Align.center(ascii),
            subtitle=' '.join((
                f"Made with ❤️ by {self.APP_AUTHOR},",
                f"Python {sys.version.split()[0]}"
            )),
            padding=1,
            title_align="center",
            subtitle_align="center",
        ))
        print()

# -------------------------------------------------------------------------------------------------|

@define
class BrokenApp(ABC):
    broken_typer: Typer = None

    @abstractmethod
    def cli(self) -> None:
        pass
