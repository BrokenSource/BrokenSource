import functools
import logging
import os
import sys
from pathlib import Path
from typing import Callable, Generator, Iterable, Union

import mkdocs_gen_files
from attr import define, field

from Broken import BROKEN, BrokenEnum, BrokenPlatform
from Broken.__main__ import BrokenManager

# Silence the site-urls plugin, it's too verbose / should be a lower level
logging.getLogger('mkdocs.plugins.mkdocs_site_urls').setLevel(logging.ERROR)

BrokenPlatform.clear_terminal()

BUILD_PROJECTS = (
    "ShaderFlow",
    "DepthFlow",
    "Pianola",
    "SpectroNote",
)

manager = BrokenManager()

# ---------------------------------- Auxiliary pathing functions --------------------------------- #

def lower(string: str) -> str:
    return string.lower()

def path2package(string: str) -> str:
    string = string.replace("__init__", "")
    string = string.replace(".py", "")
    return string

def parts(path: Path, *functions: Callable[[str], str]) -> Path:
    """Applies string transformations to each part of a path"""
    def reduce(part: str) -> str:
        return functools.reduce(lambda x, f: f(x), functions, part)

    return Path(*(reduce(part) for part in path.parts))

def files(iterable: Iterable[Path]) -> Generator[Path, None, None]:
    for path in iterable:
        if path.is_file():
            yield path

# ---------------------------------- Website generation functions --------------------------------- #

class Directory(BrokenEnum):
    Root      = "root"
    Package   = "package"
    Website   = "website"
    Resources = "resources"
    Examples  = "examples"

@define
class BrokenWebsite:
    root: Path = field(converter=Path)
    """The project's repository root path"""

    package: Path = field(converter=Path)
    """Where the code is located on the repository"""

    repository: str = field(converter=str)
    """The GitHub repository URL"""

    website: Path = field(converter=Path)
    """What subdirectory to put on the website"""

    @property
    def name(self) -> str:
        return self.package.name

    def __attrs_post_init__(self):
        sys.path.append(self.package)
        self.make(self.root,    type=Directory.Root)
        self.make(self.package, type=Directory.Package)
        self.make(self.root/"Website", type=Directory.Website)
        self.make(self.root/"Examples", type=Directory.Examples)
        self.make(self.package/"Resources", type=Directory.Resources)

    def make(self, path: Path, *, type: Directory):
        if (not path.exists()):
            return

        match type:
            case Directory.Root:
                for license in files(path.glob("License*")):
                    self.write(self.website/license.name, license.read_text())

                self.write(path=self.website/"index.md",
                    content='\n'.join((
                        "---",
                        f"title: '{self.name} Project'",
                        "---\n",
                        ((path/"Readme.md").read_text().split("<!-- Website end -->")[0])
                )))

            # Raw copy contents
            case Directory.Website:
                if (self.package.name == "Broken"):
                    return
                for file in files(path.rglob("*")):
                    self.write(self.website/file.relative_to(path),
                        file.read_bytes())

            # Raw copy resources
            case Directory.Resources:
                for file in files(path.rglob("*")):
                    script = parts(self.website/"resources"/file.relative_to(path), lower)
                    self.write(script, file.read_bytes())

            # Raw copy examples
            case Directory.Examples:
                for file in files(path.rglob("*")):
                    script = parts(self.website/"examples"/file.relative_to(path), lower)
                    self.write(script, file.read_text())

            # Write the Code Reference
            case Directory.Package:
                for file in path.rglob("*.py"):
                    # (File    ) "/home/tremeschin/Code/Broken/Externals/FFmpeg.py"
                    # (Relative) "Externals/FFmpeg.py"
                    # (Markdown) "externals/ffmpeg.md"
                    # (Source  ) "externals/ffmpeg.py"
                    # (Module  ) "Broken/Externals/FFmpeg.py"
                    # (Package ) "Broken.Externals.FFmpeg"
                    relative: Path = file.relative_to(path)
                    markdown: Path = parts(relative.with_suffix(".md"), lower)
                    source:   Path = parts(relative, lower)
                    module:   Path = file.relative_to(path.parent)
                    package:  str  = '.'.join(parts(module, path2package).parts)

                    # Write raw .py file for reference
                    self.write(Path("code", self.website, source), file.read_text())

                    # Note: Code reference takes a bit to generate
                    if not eval(os.getenv("CODE_REFERENCE", "0")):
                        continue

                    # Write code reference with mkdocstrings
                    self.write(path=Path("code", self.website, markdown), content='\n'.join((
                        "---",
                        f"title: '{module.stem}'",
                        f"description: 'Code reference for the {module} file of the {self.name} project'",
                        "---",
                        "",
                        f"# <b>File: <a href='{self.repository}/blob/main/{module}' target='_blank'>`{module}`</a></b>",
                        "",
                        f"::: {package}",
                    )))


    def write(self, path: Path, content: Union[str, bytes]):
        mode = ("wb" if isinstance(content, bytes) else "w")

        with mkdocs_gen_files.open(path, mode) as virtual:
            virtual.write(content)

# Generate the website for each project
for project in manager.projects:
    if (project.name not in BUILD_PROJECTS):
        continue
    BrokenWebsite(
        root=(project.path),
        package=(project.path/project.name),
        repository=f"https://github.com/BrokenSource/{project.name}",
        website=(project.name.lower()),
    )

# Monorepo special case
BrokenWebsite(
    root=(BROKEN.DIRECTORIES.REPOSITORY),
    package=(BROKEN.DIRECTORIES.REPOSITORY)/"Broken",
    repository="https://github.com/BrokenSource/BrokenSource",
    website="broken",
)
