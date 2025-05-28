from __future__ import annotations

import contextlib
import functools
import inspect
import itertools
import shlex
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Annotated, Any, Self, Union

import click
import rich
import typer
import typer.rich_utils
from attr import Factory, define
from pydantic import BaseModel
from typer.models import OptionInfo

from broken import Environment, Runtime, log
from broken.core import apply, arguments, flatten, list_get, shell
from broken.core.system import BrokenPlatform

# Apply custom styling to typer
typer.rich_utils.STYLE_METAVAR = "italic grey42"
typer.rich_utils.STYLE_OPTIONS_PANEL_BORDER = "bold grey42"
typer.rich_utils.STYLE_OPTION_DEFAULT = "bold bright_black"
typer.rich_utils.DEFAULT_STRING = "(default: {})"
typer.rich_utils.STYLE_OPTIONS_TABLE_PADDING = (0, 1, 0, 0)
console = rich.get_console()

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

        # Proxy Typer objects
        if isinstance(target, type(self)):
            target = target.app
        if isinstance(target, typer.Typer):
            target = BrokenTyper.proxy(target)
            context, help = (True, False)

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
                context, help = (True, False)

        # Generators must be consumed
        if inspect.isgeneratorfunction(target):
            _generator = target

            @functools.wraps(target)
            def wrapper(*args, **kwargs):
                return all(_generator(*args, **kwargs))

            target = wrapper

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
                    if (help := (metadata.help or value.description)):
                        metadata.help = help.split("\n")[0]

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
                "[bold orange3]Note:[/] The default command is implicit when args are directly passed\n\n"
                "[bold grey58]→ This means [orange3]'entry (default) (args)'[/] is the same as [orange3]'entry (args)'[/]\n"
            )
        ).should_shell()

    @staticmethod
    @functools.cache
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
            (Runtime.Installer),
            (not BrokenPlatform.OnLinux),
            (not arguments()),
        ))
        return self

    def shell_welcome(self) -> None:
        from rich.panel import Panel
        from rich.text import Text
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
            log.warn("No commands were added to the Typer app")
            return None

        # Minor pre-processing
        self.app.info.help = (self.description or "No help provided for this CLI")
        sys.argv[1:] = apply(str, flatten(args))

        for cycle in itertools.count(0):

            # On subsequent runs, prompt for command
            if (self.shell) and (cycle > 0):
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
                log.ok(f"{type(self)} exit KeyboardInterrupt")
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
            if (cycle == 0) and arguments():
                return

            # Pretty welcome message on the first 'empty' run
            if (cycle == 0):
                self.shell_welcome()

            # The args were "consumed"
            sys.argv = [sys.argv[0]]
