from . import *

# FIXME: This file is not ported yet from old Protostar


class BrokenFFmpeg(BrokenExternalABC):

    @property
    def binary_name(self) -> str: return "ffmpeg"

    def install(self, directories: BrokenDirectories) -> Union[Path, None]:
        ...

    def get_binary(self, directories: BrokenDirectories):
        BrokenNeedImport("imageio_ffmpeg")
        return imageio_ffmpeg.get_ffmpeg_exe()

    # ---------------------------------------------------------------------------------------------|

    def get_total_frames(self, path: PathLike) -> int:
        command = self.__base_command__ + ["-vsync", "1", "-i", str(path), "-f", "null", "-"]
        logInfo(f"Finding Frame Count via null decoding (accurate), May take a while for longer videos..")
        logTrace(f"command: {command}")
        with Halo(text="Waiting for command to finish..", spinner="dots"):
            Parse = subprocess.run(command, stdout=PIPE, stderr=PIPE)
        return int(Parse.stderr.decode("utf-8").split("frame=")[-1].split("fps=")[0].strip())

    def get_video_resolution(self, filePath) -> (int, int):
        FFmpegcommand = self.__base_command__ + ["-i", str(filePath), "-vframes", "1", "-f", "image2pipe", "-"]
        Parse = subprocess.run(FFmpegcommand, stdout=PIPE, stderr=PIPE)
        Frame = Image.open(io.BytesIO(Parse.stdout), formats=["jpeg"])
        return (Frame.width, Frame.height)

    def _GetRawFrames(self, filePath):
        """Pipes the raw frames to stdout, converts the bytes to numpy arrays of RGB data.
        This is a generator so usage is (for Frame in self._GetRawFrames(Video))"""
        FFmpeg = shell(
            FFmpegBinary, "-vsync", "1", "-loglevel", "panic",
            "-i", str(filePath), "-c:v", "rawvideo", "-f", "rawvideo",
            "-pix_fmt", "rgb24", "-an",  "-"
        , Popen=True, stdout=PIPE)

        while True:
            if not (Raw := FFmpeg.stdout.read(self.Width * self.Height * 3)): break
            yield numpy.frombuffer(Raw, dtype=self.dtype).reshape((self.Height, self.Width, -1))
