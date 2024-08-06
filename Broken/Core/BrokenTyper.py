import contextlib
import itertools
import os
import shlex
import sys
from typing import Any, Callable, Generator, Iterable, Set, Union

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
from Broken import flatten, log, pydantic_cli

typer.rich_utils.STYLE_METAVAR = "italic grey42"
typer.rich_utils.STYLE_OPTIONS_PANEL_BORDER = "bold grey42"
typer.rich_utils.STYLE_OPTION_DEFAULT = "bold bright_black"
typer.rich_utils.DEFAULT_STRING = "({})"
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
    """If True, will run a REPL instead of a command"""

    help_option: bool = False

    epilog: str = (
        f"• Made with [red]:heart:[/red] by [green][link=https://github.com/Tremeschin]Tremeschin[/link][/green] [yellow]v{Broken.VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://brokensrc.dev/about/sponsors/]Sponsoring[/link][/blue] my work[/italic grey53]")

    def __attrs_post_init__(self):
        self.app = typer.Typer(
            add_help_option=self.help_option,
            pretty_exceptions_enable=False,
            no_args_is_help=True,
            add_completion=False,
            rich_markup_mode="rich",
            chain=self.chain,
            epilog=self.epilog,
        )

    _panel: str = None

    @contextlib.contextmanager
    def panel(self, name: str) -> Generator[None, None, None]:
        try:
            self._panel = name
            yield
        finally:
            self._panel = None

    def command(self,
        target: Union[Callable, BaseModel],
        help: str=None,
        add_help_option: bool=True,
        naih: bool=False,
        name: str=None,
        context: bool=True,
        default: bool=False,
        panel: str=None,
        post: Callable=None,
        **kwargs,
    ) -> None:

        # Command must be implemented
        if getattr(target, "__isabstractmethod__", False):
            return

        # Convert pydantic to a wrapper with same signature
        _class = (target if isinstance(target, type) else target.__class__)
        _instance = (target() if isinstance(target, type) else target)

        if issubclass(_class, BaseModel):
            target = pydantic_cli(instance=_instance, post=post)
            name = (name or _class.__name__)
            naih = True # (Complex command)
        else:
            name = (name or target.__name__)

        # Add to known or default commands, create it
        name = name.replace("_", "-").lower()
        self.default = (name if default else self.default)
        self.commands.add(name)
        self.app.command(name=name,
            help=(help or target.__doc__),
            add_help_option=add_help_option,
            no_args_is_help=naih,
            rich_help_panel=(panel or self._panel),
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            **kwargs,
        )(target)

    @property
    def _repl(self) -> bool:
        BYPASS = (os.environ.get("REPL", "1") == "0")
        return (self.repl and not BYPASS)

    def __call__(self, *args: Iterable[Any]) -> None:
        self.app.info.help = (self.description or "No help provided")
        args = (flatten(args) or sys.argv[1:])

        for i in itertools.count():

            # On subsequent runs, prompt for command
            if (self._repl) and (i > 0):
                try:
                    args = shlex.split(typer.prompt(
                        text="",
                        prompt_suffix="❯",
                        show_default=False,
                        default=""
                    ))
                except click.exceptions.Abort:
                    log.trace("BrokenTyper exit KeyboardInterrupt")
                    break

            # Insert default command if none
            if self.default and not bool(args):
                args.insert(0, self.default)

            try:
                # Safety: Flat cast everything to str
                self.app(list(map(str, flatten(args))))
            except SystemExit:
                log.trace("Skipping SystemExit on BrokenTyper")
            except KeyboardInterrupt:
                log.success("BrokenTyper exit KeyboardInterrupt")

            # Exit out non-repl mode
            if (not self._repl):
                break

            # Some action was taken, like 'depthflow main -o ./video.mp4'
            if (i == 0) and bool(args):
                break

            # Pretty welcome message on the first 'empty' run
            if (i == 0):
                console.print(Panel(
                    title="( 🔴🟡🟢 ) Welcome to the Interactive Shell mode for Releases 🚀",
                    title_align="left",
                    border_style="bold grey42",
                    expand=False,
                    renderable=Group(
                        Text.from_markup(
                            "\nHere's your chance to [royal_blue1]run commands on a basic shell[/royal_blue1], interactively\n\n"
                            "> This mode is [royal_blue1]Experimental[/royal_blue1] and projects might not work as expected\n\n"
                            "• Preferably run the projects on a [royal_blue1]Terminal[/royal_blue1] as [spring_green1]./program.exe (args)[/spring_green1]\n"
                            "• You can skip this shell mode with [spring_green1]'REPL=0'[/spring_green1] environment var\n"
                        ), Panel(
                                "• Run [spring_green1]'--help'[/spring_green1] or press [spring_green1]'Enter'[/spring_green1] for a command list [bold bright_black](seen above)[/bold bright_black]\n"
                            "• Press [spring_green1]'CTRL+C'[/spring_green1] to exit this shell [bold bright_black](or close the Terminal)[/bold bright_black]",
                            title="Tips",
                            border_style="green"
                        )
                    ),
                ))

            # The args were "consumed"
            args = []
