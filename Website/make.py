import functools
import logging
import os
import sys
from importlib.resources import Resource
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

def dunder2markdown(string: str) -> str:
    string = string.replace("__init__", "init")
    string = string.replace("__main__", "main")
    return string

def dunder2navbar(string: str) -> str:
    string = string.replace("__init__", "`__init__`")
    string = string.replace("__main__", "`__main__`")
    return string

def noinit(string: str) -> str:
    string = string.replace("__init__", "")
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
    Examples  = "examples"
    Resources = "resources"

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

    def __attrs_post_init__(self):
        sys.path.append(self.package)
        self.make(self.root,    type=Directory.Root)
        self.make(self.package, type=Directory.Package)
        self.make(self.root/"Website",  type=Directory.Website)
        self.make(self.root/"Examples", type=Directory.Examples)

    def make(self, path: Path, *, type: Directory):
        if (not path.exists()):
            return

        match type:
            case Directory.Root:
                self.write(self.website/"index.md", (path/"Readme.md").read_text())

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
                    self.write(self.website/"resources"/file.relative_to(path),
                        file.read_bytes())

            # Copy all *.py files
            case Directory.Examples:
                content = []
                content.append("# ⭐️ Examples")
                content.append((
                    f"The examples below are a _verbatim_ copy of the files in the "
                    f"[**GitHub Repository**]({self.repository}/tree/main/Examples)"
                ))

                for index, python in enumerate(path.rglob("*.py")):
                    example = str(python.relative_to(path)).replace('.py', '')
                    content.append(f"## {'🔴🟡🟢🔵'[index]} {example}")
                    content.append("```python")
                    content.append(python.read_text())
                    content.append("```")
                    content.append("\n<hr>\n")

                self.write((self.website/"easy"/"examples.md"), '\n'.join(content))

            # Write the Code Reference
            case Directory.Package:
                if not eval(os.getenv("CODE_REFERENCE", "0")):
                    return

                for python in path.rglob("*.py"):
                    package  = python.relative_to(path).with_suffix("")
                    markdown = (Path("code")/self.website/parts(package, lower, dunder2markdown))
                    module   = Path(self.package.name)/parts(package, noinit)

                    self.write(f"{markdown}.md", '\n'.join((
                        f"# {parts(package, dunder2navbar).name}",
                        f"::: {'.'.join(module.parts)}",
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
