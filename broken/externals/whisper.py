from __future__ import annotations

import site
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional, Union

import numpy as np
from halo import Halo
from intervaltree import IntervalTree
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from typer import Option

from broken.enumx import BrokenEnum
from broken.externals import ExternalModelsBase, ExternalTorchBase
from broken.path import BrokenPath
from broken.project import BROKEN
from broken.system import BrokenPlatform
from broken.utils import install, shell

if TYPE_CHECKING:
    from faster_whisper import WhisperModel
    from faster_whisper.transcribe import Segment, Word

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

    model: Annotated[Model, Option("--model", "-m",
        help="[bold green](🟢 Basic)[/] Model to use for Transcription [green](tiny, base, small, medium, large)[/]")] = \
        Field(Model.LargeV2)

    lowvram: Annotated[bool, Option("--lowvram", "-l",
        help="[bold green](🟢 Basic)[/] Use INT8 instead of FP16 for low VRAM GPUs")] = \
        Field(False)

    def _load_model(self):
        self.load_torch()
        install(package="faster_whisper")

        # Copy PyPI libcudnn to avoid setting LD_LIBRARY_PATH
        if BrokenPlatform.OnLinux:
            for target in ("libcudnn_ops_infer.so.8", "libcudnn_cnn_infer.so.8"):
                if (libcudnn := Path(f"/usr/lib/{target}")).exists():
                    continue
                for site_packages in site.getsitepackages():
                    if (pycudnn := Path(site_packages)/f"nvidia/cudnn/lib/{target}").exists():
                        logger.warn(f"Running FasterWhisper might fail, as ({libcudnn}) doesn't exist")
                        logger.warn(f"• Luckily, we can copy it from {pycudnn}")
                        shell("sudo", "cp", pycudnn, libcudnn, confirm=True)
                        break
                else:
                    raise RuntimeError(f"{target} not found in any site-packages")

        # Finally load the model
        logger.info(f"Loading OpenAI Whisper model ({self.model.value})")

        self._model = WhisperModel(
            model_size_or_path=self.model.value,
            download_root=(BROKEN.DIRECTORIES.CACHE/"Whisper"),
            compute_type=("int8" if self.lowvram else "float16"),
        )

    def transcribe(self,
        audio: Union[str, Path, np.ndarray],
        *,
        reference: Optional[str]=None
    ) -> Spoken:
        if isinstance(audio, str) or isinstance(audio, Path):
            if not (audio := BrokenPath.get(audio)).exists():
                raise RuntimeError(f"Audio file doesn't exist: {audio}")
            audio = str(audio)

        self.load_model()
        spoken = Spoken()

        with Halo(f"Transcribing audio with Whisper model ({self.model}).."):
            for segment in self._model.transcribe(
                audio=audio,
                word_timestamps=True,
                initial_prompt=reference
            )[0]:
                spoken.sentences[(segment.start) : (segment.end + 0.001)] = segment.text.strip()

                for word in segment.words:
                    spoken.words[(word.start) : (word.end + 0.001)] = word.word.strip()
        del self._model
        return spoken


class Spoken(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sentences: IntervalTree[Segment] = Field(default_factory=IntervalTree)
    words: IntervalTree[Word] = Field(default_factory=IntervalTree)
