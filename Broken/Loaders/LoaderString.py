from . import *


@define
class LoaderString(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[str]:
        if not value:
            return ""

        elif isinstance(value, str):
            return value

        elif (path := BrokenPath(value, valid=True)):
            return path.read_text()

        elif isinstance(value, bytes):
            return value.decode()

        return None
