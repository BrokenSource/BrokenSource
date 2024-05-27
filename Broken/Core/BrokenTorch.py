from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as log

import Broken
from Broken import BrokenEnum, BrokenPath, BrokenPlatform, shell


class TorchFlavor(BrokenEnum):
    CPU   = "2.2.1+cpu"
    CUDA  = "2.2.1+cu121"
    ROCM  = "2.2.1+rocm6.0"
    MACOS = ""

class BrokenTorch:
    """
    The Bane of my Existence and the SSD Killer - Packaging PyTorch
    """

    flavor_file: str = "PyTorch.txt"
    """A relative path to a Project's Resources defining the PyTorch Flavor"""

    @staticmethod
    def manage(resources: Path):
        import site

        # Try getting current installed flavor, if any, without loading torch
        site_packages = Path(site.getsitepackages()[-1])
        if (torch_version := (site_packages/"torch"/"version.py")).exists():
            exec(torch_version.read_text(), namespace := {})
            current_flavor = namespace["__version__"].split("+")[1]
        else:
            current_flavor = None

        # Workaround (#pyapp): Until we can send envs to PyAapp, do this monsterous hack
        if Broken.PYAPP:
            version_flavor = os.environ.get("PYAPP_COMMAND_NAME", "")
            if ("+" not in version_flavor):
                return None
        elif (current_flavor is None) or (os.environ.get("MANAGE_TORCH", "0") == "1"):
            from rich.prompt import Prompt
            log.warning("This project requires PyTorch but it is not installed.")

            if BrokenPlatform.OnMacOS:
                version_flavor = TorchFlavor.MACOS
            else:
                version_flavor = Prompt.ask("\n".join((
                        "\nCheck Hardware/Platform availability at:",
                        "• (https://pytorch.org/get-started/locally)",
                        "• (https://brokensrc.dev/get/pytorch)",
                        "\n:: What PyTorch flavor do you want to use?"
                    )),
                    choices=[f"{flavor.name.lower()}" for flavor in TorchFlavor],
                    default="cpu",
                )
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
            shell(PIP, "install", f"torch=={version}", "--index-url", source_url)
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
