import os
import site
import sys
from pathlib import Path
from typing import Annotated, Optional

from typer import Option

from Broken import (
    BrokenEnum,
    BrokenPlatform,
    BrokenThread,
    Runtime,
    Tools,
    log,
    shell,
)


class TorchFlavor(str, BrokenEnum):
    CPU     = "cpu"
    CUDA118 = "cu118"
    CUDA121 = "cu121"
    CUDA124 = "cu124"
    ROCM61  = "rocm6.1"
    ROCM62  = "rocm6.2"

    def is_cuda(self) -> bool:
        return ("cu1" in self.value)

    def is_rocm(self) -> bool:
        return ("rocm" in self.value)

    def is_cpu(self) -> bool:
        return (self == TorchFlavor.CPU)


class BrokenTorch:

    @staticmethod
    def full_version() -> Optional[str]:
        """Get the current installed full version string importing torch"""

        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (torch_version := (site_packages/"torch"/"version.py")).exists():
                exec(torch_version.read_text("utf-8"), namespace := {})
                return namespace["__version__"]

    @staticmethod
    def version() -> Optional[tuple[int]]:
        """Get the current installed version tuple without importing torch"""
        if (version := BrokenTorch.full_version()):
            return tuple(map(int, version.split("+")[0].split(".")))

    @staticmethod
    def flavor() -> Optional[TorchFlavor]:
        """Get the current installed flavor without importing torch"""
        if (version := BrokenTorch.full_version()):
            return TorchFlavor.get(version.split("+")[-1])

    @BrokenThread.easy_lock
    @staticmethod
    def install(
        version: Annotated[str,
            Option("--version", "-v",
            help="Torch version to install (found in https://pypi.org/project/torch/#history)"
        )]="2.5.1",

        flavor: Annotated[Optional[TorchFlavor],
            Option("--flavor", "-f",
            help="Torch flavor to install, 'None' to ask interactively"
        )]=None,

        exists_ok: bool=False
    ) -> None:
        """📦 Install or modify PyTorch versions"""

        # Global opt-out of torch management
        if (os.getenv("BROKEN_TORCH", "1") == "0"):
            return None

        installed = BrokenTorch.full_version()

        # Only skip if installed and exists_ok, but not 'torch' in sys.argv
        if (exists_ok and (installed or "torch" in sys.argv)):
            return None

        log.special(f"Currently installed PyTorch version: {installed}")

        # Ask interactively if no flavor was provided
        if not (flavor := TorchFlavor.get(flavor)):

            # Assume it's a Linux server on NVIDIA
            if (not Runtime.Interactive):
                flavor = TorchFlavor.CUDA121

            # Pick your GPU on non-macos
            elif (not BrokenPlatform.OnMacOS):
                log.special("""
                    Generally speaking, you should chose for:
                    • [royal_blue1](Windows or Linux)[/] NVIDIA GPU: 'cuda'
                    • [royal_blue1](Linux)[/] AMD GPU (>= RX 5000): 'rocm'
                    • [royal_blue1](Other)[/] Intel ARC or others: 'cpu'

                    [dim]Tip: Set 'HSA_OVERRIDE_GFX_VERSION=10.3.0' for RX 5000 Series[/]
                """, dedent=True)

                try:
                    from rich.prompt import Prompt

                    flavor = TorchFlavor.get(Prompt.ask(
                        prompt="\n:: What PyTorch flavor do you want to install?\n\n",
                        choices=list(x.lower() for x in TorchFlavor.keys() if x != "MACOS"),
                        default="cuda121"
                    ).upper())
                    print()
                except KeyboardInterrupt:
                    exit(0)

        # Non-macos versions are flavored
        if (not BrokenPlatform.OnMacOS):
            version += f"+{flavor.value}"

        if (installed != version):
            log.special(f"Installing PyTorch version ({version})")

            # Pytorch releases flavors on their own custom index
            index = ("https://download.pytorch.org/whl/" + (flavor or ''))

            # Remove previous version, install new
            shell(Tools.pip, "uninstall", "--quiet",
                "torch", "torchvision", "torchaudio")
            shell(Tools.pip, "install",
                f"torch=={version}", "torchvision", "torchaudio",
                ("--index-url", index)*(not BrokenPlatform.OnMacOS))
            shell(Tools.pip, "install", "transformers")
        else:
            log.special(f"PyTorch version ({version}) is already installed")

# Rename the method for CLI usage
BrokenTorch.install.__name__ = "torch"
