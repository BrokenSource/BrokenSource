# pyright: reportMissingImports=false

import functools
import inspect
from abc import ABC, abstractmethod
from threading import Lock
from typing import TYPE_CHECKING, Any, Self

from halo import Halo
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from Broken import (
    BrokenTorch,
    SameTracker,
)

if TYPE_CHECKING:
    import diffusers
    import torch

# ------------------------------------------------------------------------------------------------ #

class ExternalTorchBase(BaseModel):

    _lock: Lock = PrivateAttr(default_factory=Lock)
    """Calling PyTorch in a multi-threaded environment isn't safe, so lock before any inference"""

    @property
    def device(self) -> str:
        self.load_torch()
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def load_torch(self) -> None:
        global torch
        BrokenTorch.install()
        with Halo(text="Importing PyTorch..."):
            import torch

        # Inject torch in the caller's global namespace
        inspect.currentframe().f_back.f_globals["torch"] = torch

# ------------------------------------------------------------------------------------------------ #

class ExternalModelsBase(BaseModel, ABC):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    model: str = Field(default="any")

    _model: Any = PrivateAttr(default=None)
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

    @functools.wraps(load_model)
    @abstractmethod
    def _load_model(self) -> None:
        ...

# ------------------------------------------------------------------------------------------------ #
