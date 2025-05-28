# Todo: My brain melts trying to work in this file and thinking
# how similar it is to Broken.extra.loaders, perhaps unite them?
from abc import ABC
from collections.abc import  Iterable
from pathlib import Path
from typing import Any

from attr import define

from broken import flatten

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
