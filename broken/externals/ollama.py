import shutil
import subprocess
from typing import Annotated

import ollama
from halo import Halo
from pydantic import Field
from typer import Option

from broken import BrokenPath, BrokenPlatform, log, shell
from broken.externals import ExternalModelsBase


class BrokenOllama(ExternalModelsBase):
    model: Annotated[str, Option("--model", "-m",
        help="[bold green](🟢 Basic)[/] Any valid model name from https://ollama.com/library")] = \
        Field("qwen2")

    def install(self):
        if bool(shutil.which("ollama")):
            return

        log.warn("Ollama binary [green]'ollama'[/] wasn't found on PATH, installing..")

        if BrokenPlatform.OnMacOS:
            raise RuntimeError("Ollama installaion on macOS is untested, please get it at their website")
            url = "https://github.com/ollama/ollama/releases/latest/download/Ollama-darwin.zip"

        elif BrokenPlatform.OnWindows:
            url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"

        elif BrokenPlatform.OnLinux:
            log.warn("")
            log.warn("The installation on Linux is slightly non-trivial, and it's better to use their official script")
            log.warn("• Please, get it at their website https://ollama.com/download/linux")
            log.warn("• Hint: run [green]'curl -fsSL https://ollama.com/install.sh | sh'[/]")
            log.warn("• Alternatively, install from your distro's package manager")
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

