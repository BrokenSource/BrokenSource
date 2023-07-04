# isort: off
from .Imports import *
from .CustomTypes import *
from .Logging import *
from .Platform import *
from .Directories import *
from .Functions import *
from .Dependencies import *
from .ShellCraft import *
# isort: on

try:
    import pkg_resources
    BROKEN_VERSION = f'v{pkg_resources.get_distribution("Broken").version}'
except:
    # FIXME: How to, do we need version on releases?
    BROKEN_VERSION = ""

class BrokenBase:
    def typer_app(description: str="No help provided") -> typer.Typer:
        return typer.Typer(
            help=description,
            add_help_option=False,
            no_args_is_help=True,
            add_completion=False,
            rich_markup_mode="rich",
            epilog=f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]{BROKEN_VERSION}[/yellow]",
        )
