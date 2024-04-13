import sys
from pathlib import Path
from typing import Optional

from loguru import logger as log

from Broken import BrokenEnum, BrokenPath, shell


class TorchFlavor(BrokenEnum):
    # BASE = ""
    CPU  = "cpu"
    CUDA = "cu121"
    ROCM = "rocm5.7"

class BrokenTorch:
    """
    The Bane of my Existence and the SSD Killer - Packaging PyTorch
    """

    flavor_file: str = "PyTorch.txt"
    """A relative path to a Project's Resources defining the PyTorch Flavor"""

    version: str = "2.2.1"
    """Version of Torch to install"""

    @staticmethod
    def manage(resources: Path):

        # Maybe install a PyTorch flavor
        if (pytorch := BrokenPath(resources/BrokenTorch.flavor_file).valid()):
            full = pytorch.read_text().strip()
            version, flavor = full.split("+")

            if not TorchFlavor.get(flavor):
                raise ValueError(f"Invalid PyTorch Flavor ({flavor})")

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
                shell(PIP, "uninstall", "torch", "torchvision", "torchaudio", "-y")
                shell(PIP, "install", f"torch=={version}", "torchvision", "torchaudio", "--index-url", source_url)
            else:
                log.info(f"PyTorch Flavor ({full}) already installed")

    @staticmethod
    def write_flavor(resources: Path, flavor: Optional[TorchFlavor]) -> Optional[Path]:
        if not bool(flavor):
            return None
        flavor = (f"+{flavor.value}" * bool(flavor.value))
        file = (resources/BrokenTorch.flavor_file)
        file.write_text(BrokenTorch.version + flavor)
        return file

    @staticmethod
    def remove_flavor(resources: Path) -> None:
        for file in resources.rglob(BrokenTorch.flavor_file):
            BrokenPath.remove(file)
