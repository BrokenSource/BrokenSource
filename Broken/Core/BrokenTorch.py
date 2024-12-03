import site
import sys
from pathlib import Path
from typing import Annotated, Optional

from typer import Option

from Broken import (
    BrokenEnum,
    BrokenPlatform,
    BrokenThread,
    Native,
    Runtime,
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

class BrokenTorch:

    @staticmethod
    def current() -> Optional[str]:
        """Get the current installed flavor without importing torch"""

        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (torch_version := (site_packages/"torch"/"version.py")).exists():
                exec(torch_version.read_text(), namespace := {})
                return namespace["__version__"]

    @BrokenThread.easy_lock
    @staticmethod
    def install(
        version: Annotated[str,
            Option("--version", "-v",
            help="Torch version to install (found in https://pypi.org/project/torch/#history)"
        )]="2.5.1",

        flavor: Annotated[Optional[TorchFlavor],
            Option("--flavor", "-f",
            help="Torch flavor to install. 'None' to ask interactively"
        )]=None,

        exists_ok: bool=False
    ) -> None:
        """📦 Install or modify PyTorch versions"""
        installed = BrokenTorch.current()

        # Only skip if installed and exists_ok, but not 'torch' in sys.argv
        if (exists_ok and (installed or "torch" in sys.argv)):
            return None

        log.special(f"Current PyTorch version: {installed}")

        # Ask interactively if no flavor was provided
        if not (flavor := TorchFlavor.get(flavor)):

            # Assume it's a Linux server on NVIDIA
            if (not Runtime.Interactive):
                flavor = TorchFlavor.CUDA121

            # Pick your GPU on non-macos
            elif (not BrokenPlatform.OnMacOS):
                if installed:
                    log.special("""
                    PyTorch is installed, now managing package versions!
                    """, dedent=True)
                else:
                    log.special("""
                    This project requires PyTorch, but it's not installed
                    • Checked all site.getsitepackages() locations
                    """, dedent=True)

                log.special("""
                    Chose one for your platform and hardware:
                    • [royal_blue1](Windows or Linux)[/] NVIDIA GPU: 'cuda'
                    • [royal_blue1](Linux)[/] AMD GPU (>= RX 5000): 'rocm'
                    • [royal_blue1](Other)[/] Intel ARC or Others: 'cpu'

                    Tip: Set 'HSA_OVERRIDE_GFX_VERSION=10.3.0' for RX 5000 Series
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

            # Pytorch releases different build under their own urls
            index = ("https://download.pytorch.org/whl/" + (flavor or ''))

            # Remove previous version, install new
            shell(Native.pip, "uninstall", "--quiet",
                "torch", "torchvision", "torchaudio")
            shell(Native.pip, "install",
                f"torch=={version}", "torchvision", "torchaudio",
                ("--index-url", index)*(not BrokenPlatform.OnMacOS))
            shell(Native.pip, "install", "transformers")
        else:
            log.special(f"PyTorch version ({version}) is already installed")

# Rename the method for CLI usage
BrokenTorch.install.__name__ = "torch"
