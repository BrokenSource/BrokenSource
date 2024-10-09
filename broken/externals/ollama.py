import shutil
import subprocess
from typing import Annotated

import ollama
import typer
from halo import Halo
from pydantic import Field

from broken import BrokenPath, BrokenSystem, log, shell
from broken.externals import ExternalModelsBase


class BrokenOllama(ExternalModelsBase):
    model: Annotated[str, typer.Option("--model", "-m",
        help="[bold green](🟢 Basic)[/] Any valid model name from https://ollama.com/library")] = \
        Field(default="qwen2")

    def install(self):
        if bool(shutil.which("ollama")):
            return

        log.warning("Ollama binary [green]'ollama'[/] wasn't found on PATH, installing..")

        if BrokenSystem.OnMacOS:
            raise RuntimeError("Ollama installaion on macOS is untested, please get it at their website")
            url = "https://github.com/ollama/ollama/releases/latest/download/Ollama-darwin.zip"

        elif BrokenSystem.OnWindows:
            url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"

        elif BrokenSystem.OnLinux:
            log.warning("")
            log.warning("The installation on Linux is slightly non-trivial, and it's better to use their official script")
            log.warning("• Please, get it at their website https://ollama.com/download/linux")
            log.warning("• Hint: run [green]'curl -fsSL https://ollama.com/install.sh | sh'[/]")
            log.warning("• Alternatively, install from your distro's package manager")
            exit(0)

        BrokenPath.get_external(url)

    def _load_model(self):
        self.install()

        # Download the model if it isn't found (external call for progress bars)
        if shell("ollama", "show", self.model, echo=False, stdout=subprocess.DEVNULL).returncode != 0:
            if shell("ollama", "pull", self.model).returncode != 0:
                raise RuntimeError(f"Couldn't pull model {self.model}")

    def prompt(self,
        prompt: str,
        *,
        system: str="",
        temperature: float=0.6,
        # top_k: int=10,
        # top_p: float=0.3,
    ) -> str:
        self.load_model()

        with Halo(f"Ollama model ({self.model}) is thinking.."):
            return ollama.generate(
                model=self.model,
                prompt=prompt,
                system=system,
                keep_alive=1,
                options=dict(
                    num_tokens=(2**10)*(2**4),
                    temperature=temperature,
                    num_ctx=4096,
                    # top_k=top_k,
                    # top_p=top_p,
                )
            )["response"]

