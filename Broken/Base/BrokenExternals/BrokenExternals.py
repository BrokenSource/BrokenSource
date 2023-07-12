from . import *


class BrokenExternal:
    FFmpeg = "ffmpeg"

    # Nihui ncnn
    RealSR  = "realsr-ncnn-vulkan"
    Waifu2x = "waifu2x-ncnn-vulkan"

    # Downloads
    ytdlp = "yt-dlp"


class BrokenExternals:
    def get_external(external: Union[BrokenExternal, str], echo=True):
        MAX_ATTEMPTS = 3

        for attempt in itertools.count(1):

            # Try finding the binary
            with BrokenPath.PATH(BROKEN_DIRECTORIES.EXTERNALS):
                binary = BrokenPath.get_binary(external, echo=echo)

            # Break if found
            if binary is not None:
                break

            # Install it
            BrokenExternals.install(external)

        info(f"Binary [{external}] is on PATH at [{binary}]", echo=echo)

    def install(external: Union[BrokenExternal, str], echo=True):
        ...
