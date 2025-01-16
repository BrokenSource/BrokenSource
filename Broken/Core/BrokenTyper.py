from __future__ import annotations

import contextlib
import inspect
import itertools
import shlex
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterable
from typing import Any, Optional, Self, Union

import click
import typer
import typer.rich_utils
from attr import Factory, define
from pydantic import BaseModel
from rich import get_console
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from Broken import (
    BrokenPlatform,
    Environment,
    Runtime,
    apply,
    arguments,
    flatten,
    list_get,
    log,
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

    description: str = ""
    """The default 'help' message of the CLI"""

    app: typer.Typer = None
    """The main managed typer.Typer instance"""

    chain: bool = False
    """Same as Typer.chain"""

    commands: set[str] = Factory(set)
    """List of known commands"""

    default: str = None
    """Default command to run if none is provided"""

    prehook: Callable = lambda: None
    """Function to run before any command"""

    posthook: Callable = lambda: None
    """Function to run after any command"""

    shell: bool = False
    """If True, will run a REPL when no arguments are provided"""

    naih: bool = True
    """No args is help"""

    help: bool = True
    """Add an --help option to the CLI"""

    credits: str = (
        f"• Made by [green][link=https://github.com/Tremeschin]Tremeschin[/link][/] [yellow]{Runtime.Method} v{Runtime.Version}[/]\n\n"
        "[italic grey53]→ Consider [blue][link=https://brokensrc.dev/about/sponsors/]Supporting[/link][/blue] my work [red]:heart:[/]"
    )

    @staticmethod
    def exclude() -> typer.Option:
        return typer.Option(
            parser=(lambda type: type),
            expose_value=False,
            hidden=True,
        )

    class BaseModel(ABC, BaseModel):
        """A meta class for BaseModels that contains other BaseModels and will be added to aBrokenTyper"""

        @abstractmethod
        def commands(self, typer: BrokenTyper) -> None:
            pass

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
        description: str=None,
        help: bool=True,
        naih: bool=False,
        name: str=None,
        context: bool=False,
        default: bool=False,
        panel: str=None,
        post: Callable=None,
        hidden: bool=False,
        **kwargs,
    ) -> None:

        # Method must be implemented, ignore and fail ok else
        if getattr(target, "__isabstractmethod__", False):
            return None

        _class = (target if isinstance(target, type) else type(target))

        # Convert pydantic to a wrapper with same signature
        if issubclass(_class, BaseModel):
            _instance = (target() if isinstance(target, type) else target)
            target = BrokenTyper.pydantic2typer(cls=_instance, post=post)
            name = (name or _class.__name__)
            naih = True # (Complex command)

            # Add nested commands from meta class
            if issubclass(_class, BrokenTyper.BaseModel):
                _instance.commands(self)
        else:
            name = (name or target.__name__)

        # Add to known or default commands, create it
        name = name.replace("_", "-").lower()
        self.default = (name if default else self.default)
        self.commands.add(name)
        self.app.command(
            name=(name),
            help=(description or target.__doc__),
            add_help_option=(help),
            no_args_is_help=(naih),
            rich_help_panel=(panel or self._panel),
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            hidden=(hidden),
            **kwargs,
        )(target)

    @staticmethod
    def pydantic2typer(cls: object, post: Callable=None) -> Callable:
        """Makes a Pydantic BaseModel class signature Typer compatible, by copying the class's signature
        to a wrapper virtual function. All kwargs sent are set as attributes on the instance, and typer
        will send all default ones overriden by the user commands. The 'post' method is called afterwards,
        for example `post = self.set_object` for back-communication between the caller and the instance"""
        from pydantic import BaseModel
        from typer.models import OptionInfo

        if not issubclass(this := type(cls), BaseModel):
            raise TypeError(f"Object {this} is not a Pydantic BaseModel")

        def wrapper(**kwargs):
            for name, value in kwargs.items():
                setattr(cls, name, value)
            if post: post(cls)

        # Copy the signatures to the wrapper function (the new initializer)
        wrapper.__signature__ = inspect.signature(type(cls))
        wrapper.__doc__ = cls.__doc__

        # Inject docstring into typer's help
        for value in cls.model_fields.values():
            for metadata in value.metadata:
                if isinstance(metadata, OptionInfo):
                    metadata.help = (metadata.help or value.description)

        return wrapper

    @property
    def _shell(self) -> bool:
        BYPASS = Environment.flag("REPL", 1)
        return (self.shell and not BYPASS)

    def should_shell(self) -> Self:
        self.shell = all((
            (Runtime.Binary),
            (not BrokenPlatform.OnLinux),
            (not arguments()),
        ))
        return self

    @staticmethod
    def simple(*commands: Callable) -> None:
        app = BrokenTyper()
        apply(app.command, commands)
        return app(sys.argv[1:])

    @staticmethod
    def proxy(callable: Callable) -> Callable:
        """Redirects a ctx to sys.argv and calls the method"""
        def wrapper(ctx: typer.Context):
            sys.argv[1:] = ctx.args
            callable()
        return wrapper

    @staticmethod
    def complex(
        main: Callable,
        nested: Optional[Iterable[Callable]]=None,
        direct: Optional[Iterable[Callable]]=None,
    ) -> None:
        app = BrokenTyper(description=(
            "📦 [bold orange3]Note:[/] The default command is implicit when no other command is run!\n\n"
            "[bold grey58]→ This means [orange3]'entry (default) (args)'[/] is the same as [orange3]'entry (args)'[/]\n"
        ), help=False).should_shell()

        # Preprocess arguments
        nested = flatten(nested)
        direct = flatten(direct)

        for target in set(flatten(main, nested, direct)):
            method:  bool = (target in direct)
            default: bool = (target is main)

            # Mark the default command
            description = ' '.join((
                (target.__doc__ or "No help provided"),
                (default*"[bold indian_red](default)[/]"),
            ))

            # Nested typer apps must be used with sys.argv
            _target = (target if method else BrokenTyper.proxy(target))

            app.command(
                target=_target,
                name=target.__name__,
                description=description,
                default=default,
                context=True,
                help=method,
            )

        return app(sys.argv[1:])

    def shell_welcome(self) -> None:
        console.print(Panel(
            title="( 🔴🟡🟢 ) Basic prompt for releases",
            title_align="left",
            border_style="bold grey42",
            expand=False,
            renderable=Group(
                Text.from_markup(
                    "\nSelect a [royal_blue1]command above[/], type and run it!\n"
                    "• Press [royal_blue1]Enter[/] for a command list\n"
                ), Panel(
                    "• Run [spring_green1]'{command} --help'[/] for usage [bold bright_black](seen above)[/]\n"
                    "• Press [spring_green1]'Ctrl+C'[/] to exit [bold bright_black](or close this window)[/]",
                    title="Tips",
                    border_style="green"
                )
            ),
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
            log.trace("BrokenTyper Repl exit KeyboardInterrupt")
        return False

    def __call__(self, *args: Iterable[Any]) -> None:
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

        for index in itertools.count(0):

            # On subsequent runs, prompt for command
            if (self._shell) and (index > 0):
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
                log.trace("Skipping SystemExit on BrokenTyper")
            except KeyboardInterrupt:
                log.success("BrokenTyper exit KeyboardInterrupt")
            except Exception as error:
                if (not self.shell):
                    raise error
                console.print_exception(); print() # noqa
                log.error(f"BrokenTyper exited with error: {repr(error)}")
                input("\nPress Enter to continue..")

            # Exit out non-repl mode
            if (not self._shell):
                return

            # Some action was taken, like 'depthflow main -o ./video.mp4'
            if (index == 0) and arguments():
                return

            # Pretty welcome message on the first 'empty' run
            if (index == 0):
                self.shell_welcome()

            # The args were "consumed"
            sys.argv = [sys.argv[0]]
