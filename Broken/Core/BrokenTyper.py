import contextlib
import shlex
from typing import (
    Callable,
    Generator,
    List,
)

import pydantic
from attr import Factory, define
from typer import Typer

import Broken
from Broken import flatten, log, pydantic_cli


@define
class BrokenTyper:
    """A wrap around Typer with goodies. # Todo: Maybe try Cyclopts"""
    description: str       = ""
    app:         Typer     = None
    chain:       bool      = False
    commands:    List[str] = Factory(list)
    default:     str       = None
    help_option: bool      = False
    _first:      bool      = True
    epilog:      str       = (
        f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]v{Broken.VERSION}[/yellow]\n\n"
        "→ [italic grey53]Consider [blue][link=https://brokensrc.dev/about/sponsors/]Sponsoring[/link][/blue] my Open Source Work[/italic grey53]"
    )

    def __attrs_post_init__(self):
        self.app = Typer(
            help=self.description or "No help provided",
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
        name: str=None,
        context: bool=True,
        default: bool=False,
        panel: str=None,
        **kwargs,
    ):
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
            help=help or target.__doc__ or None,
            add_help_option=add_help_option,
            name=name,
            rich_help_panel=panel or self._panel,
            context_settings=dict(
                allow_extra_args=True,
                ignore_unknown_options=True,
            ) if context else None,
            **kwargs,
        )(target)

        # Add to known commands
        self.commands.append(name)

        # Set as default command
        self.default = name if default else self.default

    def __call__(self, *args, shell: bool=False):
        while True:
            args = list(map(str, flatten(args)))

            # Insert default implied command
            first = (args[0] if (len(args) > 0) else None)
            if self.default and ((not args) or (first not in self.commands)):
                args.insert(0, self.default)

            # Update args to BrokenTyper
            if not self._first:
                args = shlex.split(input("\n:: BrokenShell (enter for help) $ "))
            self._first = False

            try:
                self.app(args)
            except SystemExit:
                log.trace("Skipping SystemExit on BrokenTyper")
            except KeyboardInterrupt:
                log.success("BrokenTyper exit KeyboardInterrupt")
            except Exception as error:
                raise error

            # Don't continue on non BrokenShell mode
            if not shell:
                break
