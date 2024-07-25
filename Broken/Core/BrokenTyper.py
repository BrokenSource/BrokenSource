import contextlib
import sys
from typing import Callable, Generator, List

import pydantic
import typer.rich_utils
from attr import Factory, define
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
    """A wrap around Typer with goodies. # Todo: Maybe try Cyclopts"""
    description: str       = ""
    app:         Typer     = None
    chain:       bool      = False
    commands:    List[str] = Factory(list)
    default:     str       = None
    help_option: bool      = False
    epilog:      str       = (
        f"• Made with [red]:heart:[/red] by [green]Tremeschin[/green] [yellow]v{Broken.VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://brokensrc.dev/about/sponsors/]Sponsoring[/link][/blue] my Work[/italic grey53]"
    )

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
        target: Callable,
        help: str=None,
        add_help_option: bool=True,
        naih: bool=False,
        name: str=None,
        context: bool=True,
        default: bool=False,
        panel: str=None,
        **kwargs,
    ) -> None:
        # Command must be implemented
        if getattr(target, "__isabstractmethod__", False):
            return

        # Convert pydantic to a signature wrapper
        if issubclass(type(target), pydantic.BaseModel):
            name = name or str(target.__class__.__name__).lower()
            target = pydantic_cli(target)

        # Maybe get callable name
        else:
            name = (name or target.__name__).replace("_", "-")

        # Create Typer command
        self.app.command(
            help=help or target.__doc__,
            add_help_option=add_help_option,
            no_args_is_help=naih,
            name=name,
            rich_help_panel=(panel or self._panel),
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            **kwargs,
        )(target)

        # Add to known or default commands
        self.default = (name if default else self.default)
        self.commands.append(name)

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
