from __future__ import annotations

import contextlib
import inspect
import itertools
import re
import runpy
import shlex
import sys
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Annotated, Any, Self, Union

import click
import typer
import typer.rich_utils
from attr import Factory, define
from pydantic import BaseModel
from rich import get_console
from rich.panel import Panel
from rich.text import Text
from typer.models import OptionInfo

from Broken import (
    BrokenAttrs,
    BrokenPlatform,
    BrokenProfiler,
    BrokenProject,
    Environment,
    Runtime,
    apply,
    arguments,
    flatten,
    list_get,
    log,
    shell,
)

# Apply custom styling to typer
typer.rich_utils.STYLE_METAVAR = "italic grey42"
typer.rich_utils.STYLE_OPTIONS_PANEL_BORDER = "bold grey42"
typer.rich_utils.STYLE_OPTION_DEFAULT = "bold bright_black"
typer.rich_utils.DEFAULT_STRING = "(default: {})"
typer.rich_utils.STYLE_OPTIONS_TABLE_PADDING = (0, 1, 0, 0)

console = get_console()

@define
class BrokenTyper:
    """Yet another Typer wrapper, with goodies"""

    app: typer.Typer = None
    """The main managed typer.Typer instance"""

    description: str = ""
    """The default 'help' message of the CLI"""

    commands: set[str] = Factory(set)
    """Known command names"""

    default: str = None
    """Default command to run if none is provided"""

    chain: bool = False
    """Same as Typer.chain"""

    help: bool = True
    """Add an --help option to the CLI"""

    naih: bool = True
    """No args is help"""

    credits: str = (
        f"• Made by [green][link=https://github.com/Tremeschin]Tremeschin[/link][/] [yellow]{Runtime.Method} v{Runtime.Version}[/]\n\n"
        "[italic grey53]→ Consider [blue][link=https://brokensrc.dev/about/sponsors/]Supporting[/link][/blue] my work [red]:heart:[/]"
    )

    def __attrs_post_init__(self):
        self.app = typer.Typer(
            add_help_option=self.help,
            pretty_exceptions_enable=False,
            no_args_is_help=self.naih,
            add_completion=False,
            rich_markup_mode="rich",
            chain=self.chain,
            epilog=self.credits,
        )

    _panel: str = None

    @contextlib.contextmanager
    def panel(self, name: str) -> Generator:
        try:
            previous = self._panel
            self._panel = name
            yield None
        finally:
            self._panel = previous

    def command(self,
        target: Union[Callable, BaseModel],
        name: str=None,
        panel: str=None,
        description: str=None,
        default: bool=False,
        hidden: bool=False,
        help: bool=True,
        naih: bool=False,
        context: bool=False,
        post: Callable=None,
        **kwargs,
    ) -> None:

        # Method must be implemented, fail ok otherwise
        if getattr(target, "__isabstractmethod__", False):
            return None

        # Can only have one default command
        if (default and self.default):
            raise ValueError("Only one default command can be set")

        # Add a default indicator
        description = ''.join((
            (description or target.__doc__ or "No help provided"),
            (default*" [bold indian_red](default)[/]"),
        ))

        # Get the type class of the target
        cls = (target if isinstance(target, type) else type(target))

        # Convert pydantic to a wrapper with same signature
        if issubclass(cls, BaseModel):
            target = BrokenTyper.pydantic2typer(cls=target, post=post)
            name = (name or cls.__name__)
            naih = True # (Complex command)
        else:
            name = (name or target.__name__)

        # Convert a function without args to a proxy
        if inspect.isfunction(target):
            if not inspect.signature(target).parameters:
                target = BrokenTyper.proxy(target)
                context = True
                help = False

        # Add to known or default commands, create it
        name = name.replace("_", "-").lower()
        self.default = (name if default else self.default)
        self.commands.add(name)
        self.app.command(
            name=name,
            help=description,
            add_help_option=help,
            no_args_is_help=naih,
            rich_help_panel=(panel or self._panel),
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            hidden=(hidden),
            **kwargs,
        )(target)

    # -------------------------------------------|

    @staticmethod
    def pydantic2typer(
        cls: Union[BaseModel, type[BaseModel]],
        post: Callable=None
    ) -> Callable:
        """Makes a Pydantic BaseModel class signature Typer compatible, creating a class and sending
        it to the 'post' method for back-communication/catching the new object instance"""

        # Assert object derives from BaseModel
        # Find where to get the signature from
        if isinstance(cls, type):
            if (not issubclass(cls, BaseModel)):
                raise TypeError(f"Class type {cls} is not a Pydantic BaseModel")
            signature = cls
        else:
            if (not isinstance(cls, BaseModel)):
                raise TypeError(f"Class instance {cls} is not a Pydantic BaseModel")
            signature = type(cls)

        # This function is what typer calls with exahustive arguments
        def wrapper(**kwargs):
            nonlocal cls, post

            # Instantiate target if type
            if isinstance(cls, type):
                cls = cls()

            # Copy new values to the instance
            for name, value in kwargs.items():
                field = cls.model_fields[name]

                # Idea: Deal with nested models?

                # Skip factory fields, not our business
                if (field.default_factory is not None):
                    continue

                setattr(cls, name, value)

            # Call the post method if provided
            if post: post(cls)

        # Copy the signatures to the wrapper function (the new initializer)
        wrapper.__signature__ = inspect.signature(signature)
        wrapper.__doc__ = cls.__doc__

        # Note: Requires ConfigDict(use_attribute_docstrings=True)
        # Inject docstring into any typer.Option's help
        for value in cls.model_fields.values():
            for metadata in value.metadata:
                if isinstance(metadata, OptionInfo):
                    metadata.help = (metadata.help or value.description)

        return wrapper

    # -------------------------------------------|

    @staticmethod
    def proxy(callable: Callable) -> Callable:
        """Redirects a ctx to sys.argv and calls the method"""
        def wrapper(ctx: typer.Context):
            sys.argv[1:] = ctx.args
            return callable()
        return wrapper

    @staticmethod
    def simple(*commands: Callable) -> None:
        app = BrokenTyper()
        apply(app.command, commands)
        return app(*sys.argv[1:])

    @staticmethod
    def toplevel() -> BrokenTyper:
        return BrokenTyper(
            help=False,
            description = (
                "[bold orange3]Note:[/] The default command is implicit when only arguments are provided\n\n"
                "[bold grey58]→ This means [orange3]'entry (default) (args)'[/] is the same as [orange3]'entry (args)'[/]\n"
            )
        ).should_shell()

    @staticmethod
    def exclude() -> typer.Option:
        return typer.Option(
            parser=(lambda type: type),
            expose_value=False,
            hidden=True,
        )

    # -------------------------------------------|
    # Special top-level commands

    def direct_script(self) -> Self:
        """Add a direct script runner command"""
        def python(
            script: Annotated[Path, typer.Argument(help="The Python script file to run")]=None,
            ctx: typer.Context=None,
        ) -> None:
            """🟢 Run a script file or enter the shell"""
            shell(sys.executable, script, *ctx.args, echo=False)
        self.command(python, context=True)
        return self

    # -------------------------------------------|

    shell: bool = False
    """If True, will run a REPL when no arguments are provided"""

    def should_shell(self) -> Self:
        self.shell = all((
            Environment.flag("REPL", 1),
            (Runtime.Binary),
            (not BrokenPlatform.OnLinux),
            (not arguments()),
        ))
        return self

    def shell_welcome(self) -> None:
        console.print(Panel(
            title="Tips",
            title_align="left",
            border_style="bold grey42",
            expand=False,
            padding=(0, 1),
            renderable=Text.from_markup(
                "• Press [spring_green1]'Ctrl+C'[/] to exit [bold bright_black](or close this window)[/]\n"
                "• Run any [spring_green1]'{command} --help'[/] for more info\n"
                "• Press [royal_blue1]Enter[/] for a command list [bold bright_black](above)[/]"
            )
        ))
        console.print(Text.from_markup(
            "\n[bold grey58]→ Write a command above and run it![/]"
        ))

    def shell_prompt(self) -> bool:
        try:
            sys.argv[1:] = shlex.split(typer.prompt(
                text="", prompt_suffix="\n❯",
                show_default=False,
                default=""
            ))
            return True
        except (click.exceptions.Abort, KeyboardInterrupt):
            log.trace(f"{type(self)} shell prompt exit KeyboardInterrupt")
        return False

    # -------------------------------------------|

    prehook: Callable = (lambda: None)
    """Function to run before any command"""

    posthook: Callable = (lambda: None)
    """Function to run after any command"""

    def __call__(self, *args: Any) -> None:
        """
        Run the Typer app with the provided arguments

        Warn:
            Send sys.argv[1:] if running directly from user input
        """
        if (not self.commands):
            log.warning("No commands were added to the Typer app")
            return None

        # Minor pre-processing
        self.app.info.help = (self.description or "No help provided for this CLI")
        sys.argv[1:] = apply(str, flatten(args))

        for index in itertools.count(0):

            # On subsequent runs, prompt for command
            if (self.shell) and (index > 0):
                if not self.shell_prompt():
                    return

            # Allow repl users to use the same commands as python entry point scripts,
            # like 'depthflow gradio' where 'depthflow' isn't the package __main__.py
            if (list_get(sys.argv, 1, "") == self.default):
                sys.argv.pop(1)

            # Defines a default, arguments are present, and no known commands were provided
            if (self.default and arguments()) and all((x not in sys.argv for x in self.commands)):
                sys.argv.insert(1, self.default)

            try:
                self.prehook()
                self.app(sys.argv[1:])
                self.posthook()
            except SystemExit:
                log.trace(f"Skipping SystemExit on {type(self)}")
            except KeyboardInterrupt:
                log.success(f"{type(self)} exit KeyboardInterrupt")
            except Exception as error:
                if (not self.shell):
                    raise error
                console.print_exception(); print() # noqa
                log.error(f"{type(self)} exited with error: {repr(error)}")
                input("\nPress Enter to continue..")

            # Exit out non-repl mode
            if (not self.shell):
                return

            # Some action was taken, like 'depthflow main -o ./video.mp4'
            if (index == 0) and arguments():
                return

            # Pretty welcome message on the first 'empty' run
            if (index == 0):
                self.shell_welcome()

            # The args were "consumed"
            sys.argv = [sys.argv[0]]

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenLauncher(ABC, BrokenAttrs):
    PROJECT: BrokenProject
    cli: BrokenTyper = Factory(BrokenTyper)

    def __post__(self):
        self.cli.should_shell()
        self.cli.description = self.PROJECT.ABOUT

        with BrokenProfiler(self.PROJECT.APP_NAME):
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
            log.warning(f"No Python scripts were scanned for {self.PROJECT.APP_NAME} {tag}s")

        # Add commands of all files, warn if none was sucessfully added
        elif (sum(self.add_project(script=file, tag=tag) for file in search) == 0):
            log.warning(f"No {self.PROJECT.APP_NAME} {tag}s found, searched in scripts:")
            log.warning('\n'.join(f"• {file}" for file in search))

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
