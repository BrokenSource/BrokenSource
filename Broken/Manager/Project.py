import json
import re
import sys
from pathlib import Path
from typing import Annotated, Self

import toml
from attrs import Factory, define, field
from dotmap import DotMap
from typer import Context, Option

from Broken import (
    BROKEN,
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenTyper,
    log,
    shell,
)


class ProjectLanguage(BrokenEnum):
    Python  = "python"
    NodeJS  = "nodejs"
    Rust    = "rust"
    CPP     = "cpp"


@define(eq=False)
class CodeProject:
    path: Path = field(converter=BrokenPath.get)
    """The project's root directory"""

    cli: BrokenTyper = Factory(BrokenTyper)

    def __hash__(self) -> int:
        return hash(self.path)

    def __eq__(self, other: Self) -> bool:
        return (self.path == other.path)

    # ------------------------------------------ #

    languages: set[ProjectLanguage] = Factory(set)

    @property
    def _pretty_language(self) -> str:
        if self.is_python: return f"🟢 [dim grey58](Python)[/] {self.description}"
        if self.is_nodejs: return f"🟡 [dim grey58](NodeJS)[/] {self.description}"
        if self.is_rust:   return f"🟠 [dim grey58](Rust  )[/] {self.description}"
        if self.is_cpp:    return f"🔵 [dim grey58](C/C++ )[/] {self.description}"
        return self.description

    # ------------------------------------------ #
    # Shorthands for project language

    @property
    def is_known(self) -> bool:
        return (len(self.languages) > 0)

    @property
    def is_python(self) -> bool:
        return (ProjectLanguage.Python in self.languages)

    @property
    def is_nodejs(self) -> bool:
        return (ProjectLanguage.NodeJS in self.languages)

    @property
    def is_rust(self) -> bool:
        return (ProjectLanguage.Rust in self.languages)

    @property
    def is_cpp(self) -> bool:
        return (ProjectLanguage.CPP in self.languages)

    # ------------------------------------------ #

    @property
    def pyproject(self) -> DotMap:
        return DotMap(toml.load(self.path/"pyproject.toml"))

    @property
    def cargo(self) -> DotMap:
        return DotMap(toml.load(self.path/"Cargo.toml"))

    @property
    def name(self) -> str:
        return str(self.pyproject.project.name)

    @property
    def description(self) -> str:
        return str(self.pyproject.project.description)

    # ------------------------------------------ #
    # Actions

    def __attrs_post_init__(self) -> None:
        self.cli.command(self.mkdocs)
        self.cli.command(self.update)
        self.cli.command(self.run)

        # Add known project languages
        if (self.path/"pyproject.toml").exists():
            self.languages.add(ProjectLanguage.Python)
        if (self.path/"Cargo.toml").exists():
            self.languages.add(ProjectLanguage.Rust)
        if (self.path/"meson.build").exists():
            self.languages.add(ProjectLanguage.CPP)

    def mkdocs(self, deploy: Annotated[bool, Option("--deploy", "-d", help="Deploy to GitHub Pages")]=False) -> None:
        """📚 Serve or deploy the project's mkdocs website"""
        shell(sys.executable, "-m", "mkdocs",
            ("gh-deploy", "--force")*deploy,
            ("serve")*(not deploy),
            cwd=self.path,
        )

    def update(self) -> None:
        """✨ Update this project's dependencies"""
        if self.is_python:
            outdated = shell("uv", "pip", "list", "--outdated", "--format=json", output=True)
            pyproject = (self.path/"pyproject.toml").read_text("utf8")

            # Replaces any package version of '~=', '>=', '^=' with latest
            for package in map(DotMap, json.loads(outdated)):
                pyproject = re.sub(
                    rf'({re.escape(package.name)}(?:\[[^\]]+\])?\s*(?:~=|>=|\^))\s*([^\"]*)"',
                    rf'\g<1>{package.latest_version}"',
                    pyproject
                )

            # Write changes
            (self.path/"pyproject.toml").write_text(pyproject, "utf8")
            shell("uv", "sync", "--all-packages")

        if self.is_nodejs:
            shell("pnpm", "update")
        if self.is_rust:
            shell("cargo", "update")
        if self.is_cpp:
            log.error("C++ projects are not supported yet")

    def run(self, ctx: Context,
        loop:  Annotated[bool, Option("--loop",  help="Press Enter after each run to run again")]=False,
        clear: Annotated[bool, Option("--clear", help="Clear terminal before running")]=False,
        debug: Annotated[bool, Option("--debug", help="Debug mode for Rust projects")]=False,
    ) -> None:
        """🔥 Run this project with all arguments that follow"""

        while True:
            BrokenPlatform.clear_terminal() if clear else None

            if self.is_python:
                log.info(f"Hey! Just type '{self.name.lower()}' to run the project directly, it's faster 😉")
                return

            elif self.is_rust:
                raise RuntimeError(log.error("Rust projects are not supported yet"))
                _status = shell(
                    "cargo", "run",
                    "--bin", self.name,
                    ["--profile", "release"] if not debug else [],
                    "--features", self.rust_features,
                    "--", ctx.args
                )

            elif self.is_nodejs:
                shell("pnpm", "install")
                shell("pnpm", "run", "dev")

            elif self.is_cpp:
                BUILD_DIR = (BROKEN.DIRECTORIES.REPO_BUILD/self.name)
                if shell("meson", BUILD_DIR, "--reconfigure", "--buildtype", "release").returncode != 0:
                    exit(log.error(f"Could not build project ({self.name})") or 1)
                if shell("ninja", "-C", BUILD_DIR).returncode != 0:
                    exit(log.error(f"Could not build project ({self.name})") or 1)
                binary = next(BUILD_DIR.glob(f"{self.name.lower()}"))
                shell(binary, ctx.args)

            if (not loop):
                break

            import rich.prompt
            log.success(f"Project ({self.name}) finished successfully")
            if not rich.prompt.Confirm.ask("(Infinite mode) Press Enter to run again", default=True):
                break

# ------------------------------------------------------------------------------------------------ #

SKIP_DIRECTORIES = {
    "venv", ".venv","__pycache__",
    "node_modules", "build", "dist",
    ".git", "build", "dist",
}

@define
class ProjectManager:
    cli: BrokenTyper = Factory(BrokenTyper)

    cls: CodeProject = CodeProject

    projects: set[CodeProject] = Factory(set)

    def find_projects(self, path: Path, depth: int=2):
        if (depth <= 0):
            return
        for path in (path, *Path(path).iterdir()):
            name = path.name

            if path.is_file():
                continue

            # Recurse on good directories
            if (name.lower() in SKIP_DIRECTORIES):
                continue
            elif name.startswith("."):
                continue
            elif path.is_dir():
                self.find_projects(path=path, depth=depth-1)

            # Check for any known project files
            for file in ("pyproject.toml",):
                if (path/file).exists():
                    project = self.cls(path=path)
                    self.projects.add(project)
                    self.cli.command(
                        target=project.cli,
                        name=project.name.lower(),
                        description=project._pretty_language,
                        panel=f"[bold]📦 Projects at[/] ({project.path.parent})",
                    )
                    continue

    @property
    def python_projects(self) -> list[CodeProject]:
        return list(filter(lambda project: project.is_python, self.projects))
