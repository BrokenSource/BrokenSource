# FIXME: How to, do we need version on releases?
try:
    import pkg_resources
    BROKEN_VERSION = f'v{pkg_resources.get_distribution("Broken").version}'
except:
    BROKEN_VERSION = ""

import sys

# Is the current Python some "compiler" release?
IS_RELEASE_NUITKA      = ("__compiled__" in globals())
IS_RELEASE_PYINSTALLER = getattr(sys, "frozen", False)

# https://github.com/pytorch/vision/issues/1899#issuecomment-598200938
# Patch torch.jit requiring inspect.getsource
if IS_RELEASE_PYINSTALLER:
    import torch.jit
    patch = lambda object, **kwargs: object
    torch.jit.script_method = patch
    torch.jit.script = patch

# Close Pyinstaller splash screen
if IS_RELEASE_PYINSTALLER:
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass

# isort: off
from .BrokenImports import *
from .BrokenLogging import *
from .BrokenPlatform import *
from .BrokenDirectories import *
from .BrokenInline import *
from .BrokenPath import *
from .BrokenDotmap import *
from .BrokenExternals import *
from .BrokenWrappers import *

# How to better name those ↓ ?
from .Smart import *
# isort: on

class BrokenBase:
    def typer_app(description: str="No help provided") -> typer.Typer:
        return typer.Typer(
            help=description,
            add_help_option=False,
            no_args_is_help=True,
            add_completion=False,
            rich_markup_mode="rich",
            epilog=(
                f"• Made with [red]:heart:[/red] by [green]Broken Source Software[/green] [yellow]{BROKEN_VERSION}[/yellow]\n\n"
                "→ [italic grey53]Consider [blue][link=https://github.com/sponsors/Tremeschin]Sponsoring[/link][/blue] my Open Source Work[/italic grey53]"
            ),
        )
