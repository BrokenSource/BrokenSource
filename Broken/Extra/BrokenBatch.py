# Todo: My brain melts trying to work in this file and thinking
# how similar it is to Broken.Extra.BrokenLoaders, perhaps unite them?
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
from os import PathLike
from pathlib import Path
from typing import Any, Self

from attr import define, field

from Broken import flatten
from Broken.Core.BrokenPath import BrokenPath

# ------------------------------------------------------------------------------------------------ #

class BaseHandler(ABC):
    ...

    # @abstractmethod
    # def get()

class ImageHandler(BaseHandler):
    ...

class VideoHandler(BaseHandler):
    ...

# ------------------------------------------------------------------------------------------------ #

@define(slots=False)
class BrokenBatch(ABC):
    loader: BaseHandler
    export: BaseHandler

    def __iter__(self,
        inputs: Any,
        output: Any,
    ) -> Iterable[tuple[Any, Path]]:

        for item in flatten(inputs):
            ...

    # @abstractmethod
    # def process(self, item: Any) -> tuple[Any, Path]:
    #     ...

# ------------------------------------------------------------------------------------------------ #

batch = BrokenBatch(
    loader=ImageHandler("~/Public/Images"),
    export=VideoHandler("~/Public/Output"),
)
