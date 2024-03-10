from . import *


@define
class LoaderString(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[str]:
        if not value:
            return ""

        elif isinstance(value, str):
            return value

        elif isinstance(value, bytes):
            return value.decode(encoding="utf-8")

        elif (path := BrokenPath(value, valid=True)):
            return path.read_text(encoding="utf-8")

        return None
