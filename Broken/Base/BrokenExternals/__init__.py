from .. import *

# FIXME: This whole BrokenExternals needs to be carefully thought for extensibility
# Is this mock-up good enough?

class BrokenExternalABC(ABC):
    """Abstract Base Class for some Broken Externals"""

    @property
    @abstractmethod
    def binary_name(self) -> str:
        """The name of the binary to be searched for on PATH"""
        return None

    def get_binary(self, directories: BrokenDirectories):
        """Default ABC implementation of finding the binary on PATH"""
        with BrokenPath.PATH(directories.EXTERNALS):
            binary = BrokenPath.get_binary(self.binary_name)
        return binary

    @abstractmethod
    def install(self, directories: BrokenDirectories):
        """Download, extract the external automatically"""
        ...

# -------------------------------------------------------------------------------------------------|

from .BrokenFFmpeg import *
from .BrokenStableDiffusion import *
from .BrokenNihui import *

BROKEN_STR_TO_EXTERNAL_MAP = {
    "ffmpeg": BrokenFFmpeg,
    "stable_diffusion": BrokenStableDiffusion,

    # Nihui
    "waifu2x": BrokenWaifu2x,
    "realsr": BrokenRealsr,
    "srmd": BrokenSRMD,
}

# -------------------------------------------------------------------------------------------------|

class BrokenExternals:
    def __init__(self, directories: BrokenDirectories=BROKEN_DIRECTORIES):
        self.DIRECTORIES = directories

    def get(self, external: str, max_attempts: int=3, echo=True):
        external = BROKEN_STR_TO_EXTERNAL_MAP.get(external, None)

        if external is None:
            error(f"Unknown external [{external}], known values ({BROKEN_STR_TO_EXTERNAL_MAP})", echo=echo)
            return None

        # Initialize the external class
        external = external()

        for attempt in range(max_attempts):

            # Find the binary, return if found
            if (binary := external.get_binary(self.DIRECTORIES)) is not None:
                return binary

            # Install the external
            info(f"• Installing External [{external.binary_name}] (attempt {attempt + 1}/{max_attempts})", echo=echo)
            external.install(self.DIRECTORIES)

        error(f"Failed to find binary [{external}] on PATH", echo=echo)
        return None

# broken_external = BrokenExternals()
# broken_external.get("ffmpeg")
# broken_external.get("waifu2x")
# broken_external.get("realsr")
# broken_external.get("srmd")

