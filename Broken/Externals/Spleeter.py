# pyright: reportMissingImports=false

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from pydantic import Field
from typer import Option

from Broken import BROKEN, install
from Broken.Externals import ExternalModelsBase, ExternalTorchBase

if TYPE_CHECKING:
    import audio_separator
    import torch

class BrokenSpleeter(ExternalModelsBase, ExternalTorchBase):
    cache: Annotated[Path, Option("--cache", "-c",
        help="[bold green](🟢 Basic)[/] Output directory for the stems, works as cache")] = \
        BROKEN.DIRECTORIES.SYSTEM_TEMP/"Spleeter"

    format: Annotated[str, Option("--format", "-f",
        help="[bold green](🟢 Basic)[/] Output format for the stems")] = \
        Field("ogg")

    def _load_model(self) -> None:
        self.load_torch()
        gpu = ("[gpu]" if torch.cuda.is_available() else "")
        install(packages="audio_separator", pypi=f"audio_separator{gpu}")

        from audio_separator.separator import Separator

        self._model = Separator(
            output_format=self.format,
            output_dir=self.cache,
        )
        self._model.load_model()

    def separate(self, audio: Path, *, cache: bool=True) -> tuple[Path, Path]:
        if not (audio := Path(audio).expanduser().resolve()).exists():
            raise FileNotFoundError(f"File not found: {audio}")

        # Build the expected output paths for this audio
        identifier = f"{audio.stem}-{str(hashlib.md5(audio.read_bytes()).hexdigest())[0:8]}"
        instrumental = (self.cache/identifier).with_suffix(f".instrumental.{self.format}")
        vocals = (self.cache/identifier).with_suffix(f".vocals.{self.format}")

        # Early return if already previously inferenced
        if (cache and instrumental.exists() and vocals.exists()):
            return instrumental, vocals

        self.load_model()

        # Inference and place on the proper cache
        _instrumental, _vocals = self._model.separate(audio)

        (self.cache/_instrumental).rename(instrumental)
        (self.cache/_vocals).rename(vocals)

        return instrumental, vocals
