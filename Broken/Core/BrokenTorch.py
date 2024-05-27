from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as log

from Broken import BrokenEnum, BrokenPath, shell


class TorchFlavor(BrokenEnum):
    CPU  = "2.2.1+cpu"
    CUDA = "2.2.1+cu121"
    ROCM = "2.2.1+rocm6.0"

class BrokenTorch:
    """
    The Bane of my Existence and the SSD Killer - Packaging PyTorch
    """

    flavor_file: str = "PyTorch.txt"
    """A relative path to a Project's Resources defining the PyTorch Flavor"""

    @staticmethod
    def manage(resources: Path):

        # Workaround (#pyapp): Until we can send envs to PyAapp, do this monsterous hack
        full = os.environ.get("PYAPP_COMMAND_NAME", "")

        if ("+" not in full):
            return None
        if not TorchFlavor.get(full):
            raise ValueError(f"Invalid PyTorch Flavor ({full})")

        version, flavor = full.split("+")

        # Try getting current installed flavor, if any, without loading torch
        site_packages = Path(__import__("site").getsitepackages()[0])
        if (torch_version := (site_packages/"torch"/"version.py")).exists():
            exec(torch_version.read_text(), namespace := {})
            current_flavor = namespace["__version__"].split("+")[1]
        else:
            current_flavor = None

        # If flavors mismatch, install the correct one
        if (current_flavor != flavor):
            log.info(f"Installing PyTorch Flavor ({full}), current is ({current_flavor})")
            PIP = (sys.executable, "-m", "pip")
            source_url = f"https://download.pytorch.org/whl/{flavor}"
            shell(PIP, "uninstall", "torch", "-y")
            shell(PIP, "install", f"torch=={version}", "--index-url", source_url)
            shell(PIP, "install", "transformers")
        else:
            log.info(f"PyTorch Flavor ({full}) already installed")

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
