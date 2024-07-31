import contextlib
import sys
from typing import Callable, Generator, Set, Union

import typer.rich_utils
from attr import Factory, define
from pydantic import BaseModel
from typer import Typer

import Broken
from Broken import flatten, log, pydantic_cli

typer.rich_utils.STYLE_METAVAR = "italic grey42"
typer.rich_utils.STYLE_OPTIONS_PANEL_BORDER = "bold grey42"
typer.rich_utils.STYLE_OPTION_DEFAULT = "bold bright_black"
typer.rich_utils.DEFAULT_STRING = "({})"
typer.rich_utils.STYLE_OPTIONS_TABLE_PADDING = (0, 1, 0, 0)

@define
class BrokenTyper:
    """Yet another Typer wrapper, with goodies"""
    description: str = ""

    app: Typer = None
    """The main managed typer.Typer instance"""

    chain: bool = False
    """Same as Typer.chain"""

    commands: Set[str] = Factory(set)
    """List of known commands"""

    default: str = None
    """Default command to run if none is provided"""

    help_option: bool = False

    epilog: str = (
        f"• Made with [red]:heart:[/red] by [green][link=https://github.com/Tremeschin]Tremeschin[/link][/green] [yellow]v{Broken.VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://brokensrc.dev/about/sponsors/]Sponsoring[/link][/blue] my work[/italic grey53]")

    def __attrs_post_init__(self):
        self.app = Typer(
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

    def __call__(self, *args):
        self.app.info.help = (self.description or "No help provided")

        # Default to argv[1:], flat cast everything to str
        args = list(map(str, flatten(args) or sys.argv[1:]))

        # Insert default command if none
        if self.default and not bool(args):
            args.insert(0, self.default)

        try:
            self.app(args)
        except SystemExit:
            log.trace("Skipping SystemExit on BrokenTyper")
        except KeyboardInterrupt:
            log.success("BrokenTyper exit KeyboardInterrupt")
