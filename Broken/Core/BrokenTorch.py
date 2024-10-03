import os
import sys
from pathlib import Path

import Broken
from Broken import BrokenEnum, BrokenPlatform, log, shell


class TorchFlavor(BrokenEnum):
    CPU   = "2.4.1+cpu@cpu"
    CUDA  = "2.4.1+cu121@cuda"
    ROCM  = "2.4.1+rocm6.1@rocm"
    MACOS = "2.4.1+ignore@mac"


class BrokenTorch:
    """
    The Bane of my Existence and the SSD Killer - Packaging PyTorch
    """

    @staticmethod
    def install():
        if os.getenv("SKIP_TORCH", "0") == "1":
            return

        import site
        current_flavor = None

        # Try getting current installed flavor, if any, without importing torch
        # Note: Reversed as Windows lists system first, and we might have multiple on Docker
        for site_packages in map(Path, reversed(site.getsitepackages())):
            if (torch_version := (site_packages/"torch"/"version.py")).exists():
                exec(torch_version.read_text(), namespace := {})
                version = namespace["__version__"]
                current_flavor = version.split("+")[1] if ("+" in version) else version
                break

        # Workaround (#pyapp): Until we can send envs to PyAapp, do this monsterous hack
        if Broken.PYAPP:
            version_flavor = os.getenv("TORCH_FLAVOR", "")
            if ("+" not in version_flavor):
                return None

        # Development mode: No PyTorch was found
        elif (current_flavor is None) or (os.getenv("MANAGE_TORCH", "0") == "1"):
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
                    "• https://brokensrc.dev/special/pytorch",
                    "",
                    "As a rule of thumb:",
                    "• [royal_blue1](Windows or Linux)[reset] NVIDIA GPU (>= GTX 700): 'cuda'",
                    "• [royal_blue1](Linux)[reset] AMD GPU (>= Radeon RX 5000): 'rocm'",
                    "• [royal_blue1](Other)[reset] Intel ARC, No discrete GPU: 'cpu'",
                    "",
                    "Tip: You can use 'SKIP_TORCH=1' to bypass this check next time",
                    "Tip: You can use 'MANAGE_TORCH=1' to get back here next time",
                    "Tip: Set 'HSA_OVERRIDE_GFX_VERSION=10.3.0' for RX 5000 Series"
                ))),
                try:
                    version_flavor = Prompt.ask(
                        "\n:: What PyTorch flavor do you want to install?\n\n",
                        choices=[f"{flavor.name.lower()}" for flavor in TorchFlavor if flavor != TorchFlavor.MACOS],
                        default="cuda"
                    )
                    print()
                except KeyboardInterrupt:
                    exit(0)
        else:
            return

        # Must be a valid Enum item of TorchFlavor
        if not (version_flavor := TorchFlavor.get(version_flavor)):
            raise ValueError(f"Invalid PyTorch Flavor ({version_flavor})")

        # Remove the @ prefix for unique enums, get version and /whl/${flavor}
        version, flavor = version_flavor.value.split("@")[0].split("+")

        # Use UV for faster pip installs 😉
        PIP = (sys.executable, "-m", "uv", "pip")

        # MacOS flavors aren't 'vendored'
        if BrokenPlatform.OnMacOS:
            shell(PIP, "uninstall", "torch", "--quiet")
            shell(PIP, "install", f"torch=={version}", "torchvision", "torchaudio")
            shell(PIP, "install", "transformers")

        # If flavors mismatch, install the correct one
        elif (current_flavor != flavor):
            log.info(f"Installing PyTorch Flavor ({version_flavor}), current is ({current_flavor})")
            source_url = f"https://download.pytorch.org/whl/{flavor}"
            shell(PIP, "uninstall", "torch", "--quiet")
            shell(PIP, "install", f"torch=={version}+{flavor}", "torchvision", "torchaudio", "--index-url", source_url)
            shell(PIP, "install", "transformers")
        else:
            log.info(f"PyTorch Flavor ({version_flavor}) already installed")
