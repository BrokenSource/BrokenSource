import functools
import re
import site
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Iterable, Optional, Union

from packaging.version import Version
from typer import Option

from broken import BrokenCache, Environment, Runtime, Tools, log
from broken.core import denum, every, shell
from broken.core.enumx import BrokenEnum
from broken.core.system import BrokenPlatform
from broken.core.typerx import BrokenTyper

# Nightly builds are daily and it's safe-ish to use 'yesterday' as the dev version
YESTERDAY: str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
TORCH_INDEX_URL_NIGHTLY: str = "https://download.pytorch.org/whl/nightly/"
TORCH_INDEX_URL_STABLE:  str = "https://download.pytorch.org/whl/"

class TorchRelease(str, BrokenEnum):
    TORCH_251_MACOS    = "2.5.1"
    TORCH_251_CPU      = "2.5.1+cpu"
    TORCH_251_CUDA_118 = "2.5.1+cu118"
    TORCH_251_CUDA_121 = "2.5.1+cu121"
    TORCH_251_CUDA_124 = "2.5.1+cu124"
    TORCH_251_ROCM_610 = "2.5.1+rocm6.1"
    TORCH_251_ROCM_620 = "2.5.1+rocm6.2"
    TORCH_260_MACOS    = "2.6.0"
    TORCH_260_CPU      = "2.6.0+cpu"
    TORCH_260_CUDA_118 = "2.6.0+cu118"
    TORCH_260_CUDA_124 = "2.6.0+cu124"
    TORCH_260_CUDA_126 = "2.6.0+cu126"
    TORCH_260_ROCM_610 = "2.6.0+rocm6.1"
    TORCH_260_ROCM_624 = "2.6.0+rocm6.2.4"
    TORCH_260_XPU      = "2.6.0+xpu"
    TORCH_270_MACOS    = "2.7.0"
    TORCH_270_CPU      = "2.7.0+cpu"
    TORCH_270_CUDA_118 = "2.7.0+cu118"
    TORCH_270_CUDA_126 = "2.7.0+cu126"
    TORCH_270_CUDA_128 = "2.7.0+cu128"
    TORCH_270_ROCM_624 = "2.7.0+rocm6.2.4"
    TORCH_270_ROCM_630 = "2.7.0+rocm6.3"
    TORCH_270_XPU      = "2.7.0+xpu"

    # # Differentiators

    @property
    def number(self) -> Version:
        """The number part of the version '2.6.0'"""
        return Version(self.value.split("+")[0])

    @property
    def flavor(self) -> Optional[str]:
        """The local part of the version '+cu124'"""
        if len(parts := self.value.split("+")) > 1:
            return parts[1]

    @property
    def version(self) -> Version:
        """The full version of the torch release '2.6.0+cu124'"""
        return ''.join(filter(None, (
            f"torch=={self.number}",
            f".dev{YESTERDAY}"*(self.is_nightly),
            f"+{self.flavor}"*(self.is_flavored)
        )))

    # # Installation

    @property
    def index(self) -> Optional[str]:
        if self.is_plain:
            return None
        elif self.is_stable:
            return (TORCH_INDEX_URL_STABLE  + self.flavor)
        elif self.is_nightly:
            return (TORCH_INDEX_URL_NIGHTLY + self.flavor)

    @property
    def packages(self) -> Iterable[str]:
        yield str(self.version)
        return "torchvision"

    def install(self, reinstall: bool=False) -> subprocess.CompletedProcess:
        log.info(f"Installing PyTorch version ({self.value})")
        return shell(
            Tools.pip, "install", self.packages,
            every("--index-url", self.index),
            "--force-reinstall"*(reinstall)
        )

    def uninstall(self) -> subprocess.CompletedProcess:
        return shell(Tools.pip, "uninstall", "--quiet", self.packages)

    # # Release types

    @property
    @functools.lru_cache
    def is_nightly(self) -> bool:
        if self.number < Version("2.8.0"):
            return False
        with BrokenCache.package_info("torch") as package:
            return (Version(package.info.version) < self.number)

    @property
    def is_stable(self) -> bool:
        return (not self.is_nightly)

    # # Flavors

    @property
    def is_flavored(self) -> bool:
        return ("+" in self.value)

    @property
    def is_plain(self) -> bool:
        return (not self.is_flavored)

    @property
    def is_cpu(self) -> bool:
        return ("+cpu" in self.value)

    @property
    def is_cuda(self) -> bool:
        return ("+cu" in self.value)

    @property
    def is_rocm(self) -> bool:
        return ("+rocm" in self.value)

    @property
    def is_xpu(self) -> bool:
        return ("+xpu" in self.value)

# -----------------------------------------------|

class SimpleTorch(BrokenEnum):
    """Global torch versions target and suggestions"""
    CPU     = TorchRelease.TORCH_270_CPU
    MACOS   = TorchRelease.TORCH_270_MACOS
    CUDA124 = TorchRelease.TORCH_270_CUDA_126
    CUDA128 = TorchRelease.TORCH_270_CUDA_128
    ROCM    = TorchRelease.TORCH_270_ROCM_630
    XPU     = TorchRelease.TORCH_270_XPU

    @classmethod
    def _prompt_choices(cls) -> Iterable[str]:
        for option in cls:
            if (option is cls.MACOS):
                continue
            yield option.name.lower()

    @staticmethod
    def prompt() -> TorchRelease:
        if BrokenPlatform.OnMacOS:
            return SimpleTorch.MACOS.value

        from rich import get_console
        from rich.box import ROUNDED
        from rich.prompt import Prompt
        from rich.table import Table

        table: Table = Table(
            title="\n[blue][link=https://pytorch.org/]PyTorch[/link][/] is used to run deep learning models",
            header_style="bold grey42",
            border_style="dim",
            box=ROUNDED,
        )

        # Table headers
        table.add_column("GPU", style="bold")
        table.add_column("Accel")
        table.add_column("Option")
        table.add_column("Size", style="dim", justify="right")
        table.add_column("Notes", style="dim")

        # Table rows
        table.add_row("[green]NVIDIA[/]", "[green]CUDA[/]", "cuda128", "6.5 GB",
            "Required for [light_coral]RTX 5000+ Blackwell[/] GPUs")
        table.add_row("[green]NVIDIA[/]", "[green]CUDA[/]", "cuda126", "5.0 GB",
            "More common, doesn't need latest drivers")

        # Hoping one day ROCm solves their issues..
        if BrokenPlatform.OnWindows:
            table.add_row("[red]Radeon[/]", "[red]ROCm[/]", "-", "-",
                "Not supported yet (https://pytorch.org/)")
        elif BrokenPlatform.OnLinux:
            table.add_row("[red]Radeon[/]", "[red]ROCm[/]", "rocm", "18.0 GB",
                "Check GPU support, override GFX if needed")

        table.add_row("[blue]Intel[/]", "[blue]XPU[/]", "xpu", "6.0 GB",
            "Desktop Arc or Integrated Graphics")
        table.add_row("-", "CPU", "cpu", "0.7 GB",
            "Slow but most compatible, small models")

        # Display the table
        console = get_console()
        console.print(table)

        try:
            choice: str = Prompt.ask(
                "\n:: What PyTorch version do you want to install?\n\n",
                choices=list(SimpleTorch._prompt_choices()),
                default=("cpu" if BrokenPlatform.OnWindows else "cpu"),
            )
            console.print()
        except KeyboardInterrupt:
            exit(0)

        return denum(SimpleTorch.get(choice.upper()))

# ------------------------------------------------------------------------------------------------ #

class BrokenTorch:

    @staticmethod
    def docker() -> Iterable[TorchRelease]:
        """Versions to build docker images for"""
        # https://en.wikipedia.org/wiki/CUDA#GPUs_supported
        yield TorchRelease.TORCH_260_CUDA_124
        yield TorchRelease.TORCH_260_CPU

    @staticmethod
    def version() -> Optional[Union[TorchRelease, str]]:
        """Current torch version if any, may return a string if not part of known enum"""

        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (script := (site_packages/"torch"/"version.py")).exists():
                exec(script.read_text("utf-8"), namespace := {})
                version = namespace.get("__version__")
                version = re.sub(r"\.dev\d{8}", "", version)
                return TorchRelease.get(version) or version

    @staticmethod
    def install(
        version: Annotated[TorchRelease,
            Option("--version", "-v",
            help="Torch version and flavor to install"
        )]=None,

        reinstall: Annotated[bool,
            Option("--reinstall", "-r",
            help="Force a reinstallation of the requested version"
        )]=False,

        exists_ok: Annotated[bool, BrokenTyper.exclude()]=False
    ) -> None:
        """📦 Install or modify PyTorch versions"""

        # Global opt-out of torch management
        if not Environment.flag("BROKEN_TORCH", True):
            return None

        installed = BrokenTorch.version()

        # Only skip if installed and exists_ok, but not 'torch' in sys.argv
        if (exists_ok and (installed or "torch" in sys.argv)):
            return None

        log.info(f"Currently installed PyTorch version: {denum(installed)}")

        # Ask interactively if no flavor was provided
        if not (version := TorchRelease.get(version)):

            # Assume it's a Linux server on NVIDIA
            if (not Runtime.Interactive):
                log.info("• Assuming Linux server with NVIDIA GPU")
                version = denum(SimpleTorch.CUDA124)

            # Fixed single version for macOS
            if BrokenPlatform.OnMacOS:
                log.info("• There is only one PyTorch version for macOS")
                version = denum(SimpleTorch.MACOS)

            else:
                version = SimpleTorch.prompt()

        if (installed == version) and (not reinstall):
            log.info("• Requested torch version matches current one!")
            if version.is_nightly:
                log.info("• Use '--reinstall' to force a nightly update")
            return

        version.install(reinstall=reinstall)

# Rename the method for CLI usage
BrokenTorch.install.__name__ = "torch"
