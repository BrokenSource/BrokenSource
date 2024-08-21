# pyright: reportMissingImports=false

import site
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Union

import numpy
import typer
from pydantic import Field

from Broken import BROKEN, BrokenEnum, BrokenPath, BrokenPlatform, log, shell
from Broken.Externals import ExternalModelsBase, ExternalTorchBase

if TYPE_CHECKING:
    import torch
    import whisper

class BrokenWhisper(ExternalModelsBase, ExternalTorchBase):
    class Model(str, BrokenEnum):
        Tiny         = "tiny"
        TinyEN       = "tiny.en"
        Base         = "base"
        BaseEN       = "base.en"
        Small        = "small"
        SmallEN      = "small.en"
        SmallDistEN  = "distil-small.en"
        Medium       = "medium"
        MediumEN     = "medium.en"
        MediumDistEN = "distil-medium.en"
        LargeV1      = "large-v1"
        LargeV2      = "large-v2"
        LargeV3      = "large-v3"
        Large        = "large"
        LargeDist2   = "distil-large-v2"
        LargeDist3   = "distil-large-v3"

    model: Annotated[Model, typer.Option("--model", "-m",
        help="[bold green](🟢 Basic)[/bold green] Model to use for Transcription [green](tiny, base, small, medium, large)[/green]")] = \
        Field(default=Model.LargeV3)

    lowvram: Annotated[bool, typer.Option("--lowvram", "-l",
        help="[bold green](🟢 Basic)[/bold green] Use INT8 instead of FP16 for low VRAM GPUs")] = \
        Field(default=False)

    def _load_model(self):
        self.load_torch()

        try:
            import faster_whisper
        except ImportError:
            shell(sys.executable, "-m", "uv", "pip", "install", "faster-whisper")

        # Copy PyPI libcudnn to avoid setting LD_LIBRARY_PATH
        if BrokenPlatform.OnLinux:
            for target in ("libcudnn_ops_infer.so.8", "libcudnn_cnn_infer.so.8"):
                if (libcudnn := Path(f"/usr/lib/{target}")).exists():
                    continue

                for site_packages in site.getsitepackages():
                    if (pycudnn := Path(site_packages)/f"nvidia/cudnn/lib/{target}").exists():
                        log.warning(f"Running FasterWhisper might fail, as ({libcudnn}) doesn't exist")
                        log.warning(f"• Luckily, we can copy it from {pycudnn}")
                        shell("sudo", "cp", pycudnn, libcudnn, confirm=True)
                        break
                else:
                    raise RuntimeError(f"{target} not found in any site-packages")

        # Finally load the model
        log.info(f"Loading OpenAI Whisper model ({self.model.value})")

        from faster_whisper import WhisperModel

        self._model = WhisperModel(
            model_size_or_path=self.model.value,
            download_root=BROKEN.DIRECTORIES.CACHE/"Whisper",
            compute_type=("int8" if self.lowvram else "float16"),
        )

    def transcribe(self, audio: Union[str, Path, numpy.ndarray]):
        if isinstance(audio, str) or isinstance(audio, Path):
            if not (audio := BrokenPath(audio, valid=True)):
                raise RuntimeError(f"Audio file doesn't exist: {audio}")
            audio = str(audio)

        inference, info = self._model.transcribe(
            audio=audio,
            word_timestamps=True,
            length_penalty=0.2,
        )

        # Todo: Pack on a class / IntervalTree structure and return
        for segment in inference:
            print(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}")

            for word in segment.words:
                print(f"  [{word.start:.2f} - {word.end:.2f}] {word.word}")
