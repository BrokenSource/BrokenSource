import site
import sys
from pathlib import Path
from typing import Annotated, Iterable, Optional, Union

from typer import Option

from Broken import Environment, Runtime, Tools
from Broken.Core import denum, every, shell
from Broken.Core.BrokenEnum import BrokenEnum
from Broken.Core.BrokenLogging import log
from Broken.Core.BrokenPlatform import BrokenPlatform
from Broken.Core.BrokenTyper import BrokenTyper
from Broken.Core.BrokenWorker import BrokenWorker

TORCH_INDEX_URL_NIGHTLY: str = "https://download.pytorch.org/whl/nightly/"
TORCH_INDEX_URL_STABLE:  str = "https://download.pytorch.org/whl/"
TORCH_VERSION: str = "2.6.0"

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

    # Installation

    @property
    def index(self) -> Optional[str]:
        if (not self.plain):
            return TORCH_INDEX_URL_STABLE + (self.flavor or '')

    @property
    def _packages(self) -> tuple[str]:
        return (f"torch=={self.value}", "torchvision")

    def install(self) -> None:
        log.special(f"Installing PyTorch version ({self.value})")
        shell(Tools.pip, "install", self._packages, every("--index-url", self.index))

    def uninstall(self) -> None:
        shell(Tools.pip, "uninstall", "--quiet", self._packages)

    # Differentiators

    @property
    def number(self) -> str:
        return self.value.split("+")[0]

    @property
    def flavor(self) -> Optional[str]:
        if len(parts := self.value.split("+")) > 1:
            return parts[1]

    # Util properties

    @property
    def plain(self) -> bool:
        return ("+" not in self.value)

    @property
    def cuda(self) -> bool:
        return ("+cu" in self.value)

    @property
    def rocm(self) -> bool:
        return ("+rocm" in self.value)

    @property
    def cpu(self) -> bool:
        return ("+cpu" in self.value)

    @property
    def xpu(self) -> bool:
        return ("+xpu" in self.value)

# -----------------------------------------------|

class SimpleTorch(BrokenEnum):
    """Global torch versions target and suggestions"""
    CPU   = TorchRelease.TORCH_260_CPU
    MACOS = TorchRelease.TORCH_260_MACOS
    CUDA  = TorchRelease.TORCH_260_CUDA_124
    ROCM  = TorchRelease.TORCH_260_ROCM_624
    XPU   = TorchRelease.TORCH_260_XPU

    @classmethod
    def prompt_choices(cls) -> Iterable[str]:
        for option in cls:
            if (option is cls.MACOS):
                continue
            yield option.name.lower()

# ------------------------------------------------------------------------------------------------ #

class BrokenTorch:

    @staticmethod
    def docker() -> Iterable[TorchRelease]:
        """List of versions for docker images builds"""
        yield SimpleTorch.CUDA.value
        yield SimpleTorch.CPU.value

    @staticmethod
    def version() -> Optional[Union[TorchRelease, str]]:
        """Current torch version if any, may return a string if not part of known enum"""

        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (script := (site_packages/"torch"/"version.py")).exists():
                exec(script.read_text("utf-8"), namespace := {})
                version = namespace.get("__version__")
                return TorchRelease.get(version) or version

    @BrokenWorker.easy_lock
    @staticmethod
    def install(
        version: Annotated[TorchRelease,
            Option("--version", "-v",
            help="Torch version and flavor to install"
        )]=None,

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

        log.special(f"Currently installed PyTorch version: {denum(installed)}")

        # Ask interactively if no flavor was provided
        if not (version := TorchRelease.get(version)):

            # Assume it's a Linux server on NVIDIA
            if (not Runtime.Interactive):
                version = SimpleTorch.CUDA

            # Fixed single version for macOS
            if BrokenPlatform.OnMacOS:
                version = SimpleTorch.MACOS

            else:
                version = BrokenTorch.prompt_flavor()

        if (installed == version):
            log.special("• Requested torch version matches current one!")
            return

        version.install()

    @staticmethod
    def prompt_flavor() -> TorchRelease:
        from rich.prompt import Prompt

        log.special("""
            Generally speaking, you should chose for:
            • [royal_blue1](Windows or Linux)[/] NVIDIA GPU: 'cuda'
            • [royal_blue1](Windows or Linux)[/] Intel ARC: 'xpu'
            • [royal_blue1](Linux)[/] AMD GPU (>= RX 5000): 'rocm'
            • [royal_blue1](Other)[/] Others or CPU: 'cpu'

            [dim]Tip: Set 'HSA_OVERRIDE_GFX_VERSION=10.3.0' for RX 5000 Series[/]
        """, dedent=True)

        try:
            choice = SimpleTorch.get(Prompt.ask(
                prompt="\n:: What PyTorch version do you want to install?\n\n",
                choices=list(SimpleTorch.prompt_choices()),
                default="cuda"
            ).upper())
            print()
        except KeyboardInterrupt:
            exit(0)

        return choice.value

# Rename the method for CLI usage
BrokenTorch.install.__name__ = "torch"
