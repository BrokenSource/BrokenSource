from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import Broken
from Broken import BrokenEnum, BrokenPath, BrokenPlatform, log, shell


class TorchFlavor(BrokenEnum):
    CPU   = "2.3.0+cpu"
    CUDA  = "2.3.0+cu121"
    ROCM  = "2.3.0+rocm6.0"
    MACOS = ""

class BrokenTorch:
    """
    The Bane of my Existence and the SSD Killer - Packaging PyTorch
    """

    flavor_file: str = "PyTorch.txt"
    """A relative path to a Project's Resources defining the PyTorch Flavor"""

    @staticmethod
    def manage(resources: Path):
        if os.environ.get("SKIP_TORCH", "0") == "1":
            return

        import site
        current_flavor = None

        # Try getting current installed flavor, if any, without importing torch
        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (torch_version := (site_packages/"torch"/"version.py")).exists():
                exec(torch_version.read_text(), namespace := {})
                current_flavor = namespace["__version__"].split("+")[1]
                break

        # Workaround (#pyapp): Until we can send envs to PyAapp, do this monsterous hack
        if Broken.PYAPP:
            version_flavor = os.environ.get("PYAPP_COMMAND_NAME", "")
            if ("+" not in version_flavor):
                return None

        # Development mode: No PyTorch was found
        elif (current_flavor is None) or (os.environ.get("MANAGE_TORCH", "0") == "1"):
            from rich.prompt import Prompt
            log.warning("")

            if BrokenPlatform.OnMacOS:
                version_flavor = TorchFlavor.MACOS
            else:
                log.warning("\n".join((
                    "This project requires PyTorch, but it was not found",
                    "• Checked all site.getsitepackages() locations",
                    "",
                    "Check Hardware/Platform availability at:",
                    "• https://pytorch.org/get-started/locally",
                    "• https://brokensrc.dev/get/pytorch",
                    "",
                    "As a rule of thumb:",
                    "• [royal_blue1](Windows + Linux)[/royal_blue1] NVIDIA GPU (>= GTX 700): 'cuda'",
                    "• [royal_blue1](Linux)[/royal_blue1] AMD GPU (>= Radeon RX 5000): 'rocm'",
                    "• [royal_blue1](Other)[/royal_blue1] Intel ARC, No discrete GPU: 'cpu'",
                    "",
                    "Tip: You can use 'SKIP_TORCH=1' to bypass this check next time",
                    "Tip: You can use 'MANAGE_TORCH=1' to get back here next time",
                    "Tip: Set 'HSA_OVERRIDE_GFX_VERSION=10.3.0' for RX 5000 Series"
                ))),
                try:
                    version_flavor = Prompt.ask(
                        "\n:: What PyTorch flavor do you want to install?\n\n",
                        choices=[f"{flavor.name.lower()}" for flavor in TorchFlavor],
                        default="cpu"
                    )
                except KeyboardInterrupt:
                    exit(0)
        else:
            return

        # Must be a valid Enum item of TorchFlavor
        if not (version_flavor := TorchFlavor.get(version_flavor)):
            raise ValueError(f"Invalid PyTorch Flavor ({version_flavor})")

        version, flavor = version_flavor.value.split("+")

        # If flavors mismatch, install the correct one
        if (current_flavor != flavor):
            log.info(f"Installing PyTorch Flavor ({version_flavor}), current is ({current_flavor})")
            PIP = (sys.executable, "-m", "pip")
            source_url = f"https://download.pytorch.org/whl/{flavor}"
            shell(PIP, "uninstall", "torch", "-y")
            shell(PIP, "install", f"torch=={version}", "torchvision", "--index-url", source_url)
            shell(PIP, "install", "transformers")
        else:
            log.info(f"PyTorch Flavor ({version_flavor}) already installed")

    @staticmethod
    def season(resources: Path, flavor: Optional[TorchFlavor]) -> Optional[Path]:
        if not bool(flavor):
            return None
        flavor = (f"+{flavor.value}" * bool(flavor.value))
        file = (resources/BrokenTorch.flavor_file)
        file.write_text(BrokenTorch.version + flavor)
        return file

    @staticmethod
    def unseason(resources: Path) -> None:
        for file in resources.rglob(BrokenTorch.flavor_file):
            BrokenPath.remove(file)
