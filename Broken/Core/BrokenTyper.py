from __future__ import annotations

import contextlib
import itertools
import os
import shlex
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Iterable, List, Set, Union

import click
import typer
import typer.rich_utils
from attr import Factory, define
from pydantic import BaseModel
from rich import get_console
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

import Broken
from Broken import BrokenPlatform, apply, flatten, log, pydantic2typer

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

    app: typer.Typer = None
    """The main managed typer.Typer instance"""

    chain: bool = False
    """Same as Typer.chain"""

    commands: Set[str] = Factory(set)
    """List of known commands"""

    default: str = None
    """Default command to run if none is provided"""

    repl: bool = False
    """If True, will run a REPL when no arguments are provided"""

    naih: bool = True
    """No args is help"""

    help: bool = True

    credits: str = (
        f"• Made by [green][link=https://github.com/Tremeschin]Tremeschin[/link][reset] [yellow]{Broken.RUNTIME} v{Broken.VERSION}[reset]\n\n"
        "→ [italic grey53]Consider [blue][link=https://brokensrc.dev/about/sponsors/]Supporting[/link][/blue] my work [red]:heart:[reset]"
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
    def panel(self, name: str) -> Generator[None, None, None]:
        try:
            previous = self._panel
            self._panel = name
            yield
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

        # Command must be implemented
        if getattr(target, "__isabstractmethod__", False):
            return

        _class = (target if isinstance(target, type) else target.__class__)

        # Convert pydantic to a wrapper with same signature
        if issubclass(_class, BaseModel):
            _instance = (target() if isinstance(target, type) else target)
            target = pydantic2typer(instance=_instance, post=post)
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
        self.app.command(name=name,
            help=(description or target.__doc__),
            add_help_option=help,
            no_args_is_help=naih,
            rich_help_panel=(panel or self._panel),
            hidden=hidden,
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            **kwargs,
        )(target)

    @property
    def _repl(self) -> bool:
        BYPASS = (os.getenv("REPL", "1") == "0")
        return (self.repl and not BYPASS)

    def release_repl(self) -> None:
        self.repl = all((
            Broken.RELEASE,
            not bool(sys.argv[1:]),
            not BrokenPlatform.OnLinux
        ))

    @staticmethod
    def simple(*commands: Iterable[Callable]) -> None:
        app = BrokenTyper()
        app.release_repl()

        for command in commands:
            app.command(command)

        return app(sys.argv[1:])

    @staticmethod
    def release(main: Callable, *others: Iterable[Callable]) -> None:
        app = BrokenTyper(description=(
            "📦 [bold orange3]BrokenTyper's[reset] Multiple entry points handler for releases executables\n\n"
            "• Chose an option below for what parts of the software you want to run!\n"
        ))
        app.release_repl()

        # Redirects a ctx to sys.argv and calls the method
        def proxy(callable: Callable) -> None:
            def wrapper(ctx: typer.Context) -> None:
                sys.argv[1:] = ctx.args
                callable()
            return wrapper

        for method in flatten(main, others):

            # Automatically select 'main' method on non-repl or with incoming args
            default = ((method is main) and (not app.repl or bool(sys.argv[1:])))

            app.command(
                target=proxy(method),
                name=method.__name__,
                description=method.__doc__,
                default=default,
                context=True,
                help=False,
            )

        return app(sys.argv[1:])

    def repl_welcome(self) -> None:
        console.print(Panel(
            title="( 🔴🟡🟢 ) Welcome to the Interactive Shell mode for Releases 🚀",
            title_align="left",
            border_style="bold grey42",
            expand=False,
            renderable=Group(
                Text.from_markup(
                    "\nHere's your chance to [royal_blue1]run commands on a basic shell[reset], interactively\n\n"
                    "> This mode is [royal_blue1]Experimental[reset] and projects might not work as expected\n\n"
                    "• Preferably run the projects on a [royal_blue1]Terminal[reset] as [spring_green1]./program.exe (args)[reset]\n"
                    "• You can skip this shell mode with [spring_green1]'REPL=0'[reset] environment variable\n"
                ), Panel(
                    "• Run any [spring_green1]'command --help'[reset] for a command list [bold bright_black](seen above)[reset]\n"
                    "• Press [spring_green1]'CTRL+C'[reset] to exit this shell [bold bright_black](or close the Terminal)[reset]",
                    title="Tips",
                    border_style="green"
                )
            ),
        ))

    def repl_prompt(self) -> bool:
        try:
            sys.argv[1:] = shlex.split(typer.prompt(
                text="", prompt_suffix="❯",
                show_default=False,
                default=""
            ))
            return True
        except (click.exceptions.Abort, KeyboardInterrupt):
            log.trace("BrokenTyper Repl exit KeyboardInterrupt")
        return False

    def __call__(self, *args: Iterable[Any]) -> None:
        """
        Warn: Send sys.argv[1:] if running directly from user input
        """
        self.app.info.help = (self.description or "No help provided for this CLI")
        sys.argv[1:] = apply(str, flatten(args))

        for index in itertools.count():

            # On subsequent runs, prompt for command
            if (self._repl) and (index > 0):
                if not self.repl_prompt():
                    break

            # Insert default command if none
            if self.default and not any((name in sys.argv for name in self.commands)):
                sys.argv.insert(1, self.default)

            try:
                self.app(sys.argv[1:])
            except SystemExit:
                log.trace("Skipping SystemExit on BrokenTyper")
            except KeyboardInterrupt:
                log.success("BrokenTyper exit KeyboardInterrupt")

            # Exit out non-repl mode
            if (not self._repl):
                break

            # Some action was taken, like 'depthflow main -o ./video.mp4'
            if (index == 0) and bool(sys.argv[1:]):
                break

            # Pretty welcome message on the first 'empty' run
            if (index == 0):
                self.repl_welcome()

            # The args were "consumed"
            sys.argv = sys.argv[:1]
