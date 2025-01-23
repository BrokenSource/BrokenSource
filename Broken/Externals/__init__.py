# pyright: reportMissingImports=false

import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

from pydantic import ConfigDict, Field, PrivateAttr

from Broken import (
    BrokenModel,
    BrokenTorch,
    BrokenWorker,
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
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def load_torch(self) -> None:
        """Install and inject torch in the caller's globals"""
        BrokenTorch.install(exists_ok=True)
        inspect.currentframe().f_back.f_globals["torch"] = __import__("torch")

# ------------------------------------------------------------------------------------------------ #

class ExternalModelsBase(BrokenModel, ABC):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    model: str = Field("any")

    _model: Any = PrivateAttr(None)
    """The true loaded model object"""

    _loaded: SameTracker = PrivateAttr(default_factory=SameTracker)
    """Keeps track of the current loaded model name, to avoid reloading"""

    @BrokenWorker.easy_lock
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
