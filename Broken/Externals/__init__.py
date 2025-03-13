# pyright: reportMissingImports=false

import inspect
import multiprocessing
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

from pydantic import ConfigDict, Field, PrivateAttr

from Broken import (
    BrokenModel,
    Environment,
    SameTracker,
)

if TYPE_CHECKING:
    import diffusers
    import torch

# ------------------------------------------------------------------------------------------------ #

class ExternalTorchBase(BrokenModel):

    @property
    def device(self) -> str:
        self.load_torch()

        if (device := Environment.get("TORCH_DEVICE")):
            return device
        if torch.cuda.is_available():
            return "cuda"
        if torch.xpu.is_available():
            return "xpu"
        if torch.mps.is_available():
            return "mps"
        return "cpu"

    def load_torch(self) -> None:
        """Install and inject torch in the caller's globals"""
        from Broken import BrokenTorch
        BrokenTorch.install(exists_ok=True)
        torch = __import__("torch")
        inspect.currentframe().f_back.f_globals["torch"] = torch
        torch.set_num_threads(multiprocessing.cpu_count())

# ------------------------------------------------------------------------------------------------ #

class ExternalModelsBase(BrokenModel, ABC):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    model: str = Field("any")

    _model: Any = PrivateAttr(None)
    """The true loaded model object"""

    _loaded: SameTracker = PrivateAttr(default_factory=SameTracker)
    """Keeps track of the current loaded model name, to avoid reloading"""

    def load_model(self) -> Self:
        if self._loaded(self.model):
            return
        if self._model:
            del self._model
        self._load_model()
        return self

    @abstractmethod
    def _load_model(self) -> None:
        ...

# ------------------------------------------------------------------------------------------------ #
