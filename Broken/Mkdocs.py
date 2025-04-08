# ------------------------------------------------------------------------------------------------ #
# Silence the site-urls plugin, it's too verbose / should be a lower level

import logging

logging.getLogger('mkdocs.plugins.mkdocs_site_urls').setLevel(logging.ERROR)

# ------------------------------------------------------------------------------------------------ #
# Fix tabbed items without a parent <h2> header

import contextlib
import functools

from pymdownx.tabbed import TabbedTreeprocessor

method = TabbedTreeprocessor.get_parent_header_slug

@functools.wraps(method)
def get_parent_header_slug(*args, **kwargs):
    with contextlib.suppress(AttributeError):
        return method(*args, **kwargs)
    return ''

TabbedTreeprocessor.get_parent_header_slug = get_parent_header_slug

# ------------------------------------------------------------------------------------------------ #

from pathlib import Path

from attrs import define, field

from Broken import BROKEN, BrokenPath, BrokenPlatform

MONOREPO = BROKEN.DIRECTORIES.REPO_WEBSITE

@define
class BrokenMkdocs:

    makefile: Path = field(converter=Path)

    @property
    def website(self) -> Path:
        return Path(self.makefile.parent)

    @property
    def repository(self) -> Path:
        return Path(self.website.parent)

    @property
    def project_name(self) -> str:
        return self.repository.name

    @property
    def symdir(self) -> Path:
        return (self.website/"Link")

    def symlink_readme(self):
        BrokenPath.symlink(
            real=(self.repository/"readme.md"),
            virtual=(self.website/"index.md"),
            echo=False,
        )

    def monolink(self, path: Path, local: Path=None):
        """Symlink a path in the monorepo to a local one"""
        BrokenPath.symlink(real=(MONOREPO/path),
            virtual=(self.website/(local or path)))

    def __attrs_post_init__(self):
        BrokenPlatform.clear_terminal()

        # Delete all previous symlinks
        for path in self.website.rglob("*"):
            if path.is_symlink():
                path.unlink()

        # Symlink the project package
        # BrokenPath.symlink(
        #     real=(self.repository/self.project_name),
        #     virtual=(self.symdir/self.project_name),
        #     echo=False,
        # )

        # Symlink the monorepo
        # BrokenPath.symlink(
        #     real=(MONOREPO),
        #     virtual=(self.symdir/"Broken"),
        #     echo=False,
        # )
