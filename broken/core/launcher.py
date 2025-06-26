import re
import runpy
import sys
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path

import typer
from attr import Factory, define

from broken import Environment, Runtime, log
from broken.core import BrokenAttrs
from broken.core.project import BrokenProject
from broken.core.typerx import BrokenTyper


@define
class BrokenLauncher(ABC, BrokenAttrs):
    PROJECT: BrokenProject
    cli: BrokenTyper = Factory(BrokenTyper)

    def __post__(self):
        self.cli.should_shell()
        self.cli.description = self.PROJECT.ABOUT
        self.main()

    @abstractmethod
    def main(self) -> None:
        pass

    def find_projects(self, tag: str="Project") -> None:
        """Find Python files in common directories (direct call, cwd) that any class inherits from
        something that contains the substring of `tag` and add as a command to this Typer app"""
        search = deque()

        # Note: Safe get argv[1], remove from argv if valid to not interfere with Typer
        if (direct := Path(dict(enumerate(sys.argv)).get(1, "\0"))).exists():
            direct = Path(sys.argv.pop(1))

        # The project file was sent directly
        if (direct.suffix == ".py"):
            search.append(direct)

        # It can be a glob pattern
        elif ("*" in direct.name):
            search.extend(direct.parent.glob(direct.name))

        # A directory of projects was sent
        elif direct.is_dir():
            search.extend(direct.glob("*.py"))

        # Scan common directories
        else:
            if (Runtime.Source):
                search.extend(self.PROJECT.DIRECTORIES.REPO_PROJECTS.rglob("*.py"))
                search.extend(self.PROJECT.DIRECTORIES.REPO_EXAMPLES.rglob("*.py"))
            search.extend(self.PROJECT.DIRECTORIES.PROJECTS.rglob("*.py"))
            search.extend(Path.cwd().glob("*.py"))

        # Add bundled examples in the resources directory
        if (len(search) == 0) or Environment.flag("BUNDLED", 0):
            search.extend(self.PROJECT.RESOURCES.EXAMPLES.rglob("*.py"))

        # No files were scanned
        if (len(search) == 0):
            log.warn(f"No Python scripts were scanned for {self.PROJECT.APP_NAME} {tag}s")

        # Add commands of all files, warn if none was sucessfully added
        elif (sum(self.add_project(script=file, tag=tag) for file in search) == 0):
            log.warn(f"No {self.PROJECT.APP_NAME} {tag}s found, searched in scripts:")
            log.warn('\n'.join(f"• {file}" for file in search))

    def _regex(self, tag: str) -> re.Pattern:
        """Generates the self.regex for matching any valid Python class that contains "tag" on the
        inheritance substring, and its optional docstring on the next line"""
        return re.compile(
            r"^class\s+(\w+)\s*\(.*?(?:" + tag + r").*\):\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
            re.MULTILINE
        )

    def add_project(self, script: Path, tag: str="Project") -> bool:
        if (not script.exists()):
            return False

        def wrapper(file: Path, class_name: str):
            def run(ctx: typer.Context):
                # Warn: Point of trust transfer to the file the user is running
                runpy.run_path(file)[class_name]().cli(*ctx.args)
            return run

        # Match all projects and their optional docstrings
        code = script.read_text("utf-8")
        matches = list(self._regex(tag).finditer(code))

        # Add a command for each match
        for match in matches:
            class_name, docstring = match.groups()
            self.cli.command(
                target=wrapper(script, class_name),
                name=class_name.lower(),
                description=(docstring or "No description provided"),
                panel=f"📦 {tag}s at ({script})",
                context=True,
                help=False,
            )

        return bool(matches)
