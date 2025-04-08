import contextlib
import functools
import logging
from pathlib import Path
from textwrap import dedent
from typing import Union

import mkdocs_gen_files
import yaml
from attrs import define, field
from dotmap import DotMap

from Broken import BROKEN, BrokenPath, BrokenPlatform, apply

monorepo = BROKEN.DIRECTORIES.REPO_WEBSITE

# Silence the site-urls plugin, it's too verbose / should be a lower level
logging.getLogger('mkdocs.plugins.mkdocs_site_urls').setLevel(logging.ERROR)

# ------------------------------------------------------------------------------------------------ #
# Fix tabbed items without a parent <h2> header

from pymdownx.tabbed import TabbedTreeprocessor

method = TabbedTreeprocessor.get_parent_header_slug

@functools.wraps(method)
def get_parent_header_slug(*args, **kwargs):
    with contextlib.suppress(AttributeError):
        return method(*args, **kwargs)
    return ''

TabbedTreeprocessor.get_parent_header_slug = get_parent_header_slug

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenMkdocs:

    project: str = field()
    """The project's main package name"""

    website: Path = field(converter=lambda x: Path(x).parent)
    """Send the importer's `__file__` gen-files (make.py)"""

    # # Common paths

    @property
    def repository(self) -> Path:
        return Path(self.website.parent)

    @property
    def package(self) -> Path:
        return (self.repository/self.project)

    @property
    def examples(self) -> Path:
        return (self.repository/"Examples")

    @property
    def config(self) -> DotMap:
        return DotMap(yaml.load(
            stream=(self.repository/"mkdocs.yml").read_text(),
            Loader=yaml.Loader
        ))

    # # Common actions

    def virtual_readme(self):
        """Copy the repository readme to a root index.md"""
        self.virtual(path="index.md", data='\n'.join((
            '<div id="tsparticles"></div>',
            (self.repository/"readme.md").read_text()
        )))

    def virtual(self, path: Path, data: Union[str, bytes, Path]) -> None:
        """Create a virtual file in the docs_dir (can be overriden by a real)"""
        if not (isinstance(data, Path) and (self.website/path).exists()):
            data = (data.read_bytes() if isinstance(data, Path) else data)
            data = (dedent(data) if isinstance(data, str) else data)
            mode = ("wb" if isinstance(data, bytes) else "w")
            with mkdocs_gen_files.open(path, mode) as virtual:
                virtual.write(data)

    def smartnav(self, nav: DotMap):
        """If a file on the nav isn't found locally, copy it from the monorepo"""
        if isinstance(nav, dict):
            return apply(self.smartnav, nav.values())
        elif isinstance(nav, list):
            return apply(self.smartnav, nav)

        if not (self.website/nav).exists():
            if (virtual := monorepo/nav).exists():
                self.virtual(nav, data=virtual)

    def __attrs_post_init__(self):
        BrokenPlatform.clear_terminal()
        self.smartnav(self.config.nav)

        # Copy themes and overrides folder
        for path in ("css", "javascript"):
            for file in BrokenPath.files(monorepo.rglob(f"{path}/*")):
                self.virtual(path=file.relative_to(monorepo), data=file)

        # Copy the project package files
        for file in BrokenPath.files(self.package.rglob("*")):
            self.virtual(path=file.relative_to(self.repository), data=file)

        # Copy example files
        for file in BrokenPath.files(self.examples.rglob("*")):
            self.virtual(path=file.relative_to(self.repository), data=file)

        self.virtual_readme()
