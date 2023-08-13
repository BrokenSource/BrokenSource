"""State of the art FFmpeg class. See BrokenFFmpeg for more info"""
from . import *

# ----------------------------------------------|
# Codecs

class FFmpegVideoCodec(BrokenEnum):
    """-c:v ffmpeg option"""
    H264       = "libx264"
    H265       = "libx265"
    H264_NVENC = "h264_nvenc"
    H265_NVENC = "hevc_nvenc"
    AV1        = "libaom-av1"
    Rawvideo   = "rawvideo"
    Copy       = "copy"

class FFmpegAudioCodec(BrokenEnum):
    """-c:a ffmpeg option"""
    AAC    = "aac"
    MP3    = "libmp3lame"
    VORBIS = "libvorbis"
    OPUS   = "libopus"
    FLAC   = "flac"
    AC3    = "ac3"

# ----------------------------------------------|
# H264

class FFmpegH264Preset(BrokenEnum):
    """-preset ffmpeg option"""
    Ultrafast = "ultrafast"
    Superfast = "superfast"
    Veryfast  = "veryfast"
    Faster    = "faster"
    Fast      = "fast"
    Medium    = "medium"
    Slow      = "slow"
    Slower    = "slower"
    Veryslow  = "veryslow"

class FFmpegH264Tune(BrokenEnum):
    """-tune ffmpeg option"""
    Film        = "film"
    Animation   = "animation"
    Grain       = "grain"
    Stillimage  = "stillimage"
    PSNR        = "psnr"
    SSIM        = "ssim"
    Fastdecode  = "fastdecode"
    Zerolatency = "zerolatency"

class FFmpegH264Profile(BrokenEnum):
    """-profile:v ffmpeg option"""
    Baseline  = "baseline"
    Main      = "main"
    High      = "high"
    High10    = "high10"
    High422   = "high422"
    High444   = "high444"
    High444p  = "high444predictive"
    High444ip = "high444intra"

class FFmpegH264Quality(BrokenEnum):
    """-crf ffmpeg option"""
    Low      = 51
    Medium   = 23
    High     = 18
    Veryhigh = 15
    Ultra    = 10
    Lossless = 0

# ----------------------------------------------|
# H265

class FFmpegH265Preset(BrokenEnum):
    """-preset ffmpeg option"""
    Ultrafast = "ultrafast"
    Superfast = "superfast"
    Veryfast  = "veryfast"
    Faster    = "faster"
    Fast      = "fast"
    Medium    = "medium"
    Slow      = "slow"
    Slower    = "slower"
    Veryslow  = "veryslow"

class FFmpegH265Tune(BrokenEnum):
    """-tune ffmpeg option"""
    PSNR        = "psnr"
    SSIM        = "ssim"
    Grain       = "grain"
    Fastdecode  = "fastdecode"
    Zerolatency = "zerolatency"

class FFmpegH265Profile(BrokenEnum):
    """-profile:v ffmpeg option"""
    Main   = "main"
    Main10 = "main10"
    Main12 = "main12"

class FFmpegH265Quality(BrokenEnum):
    """-crf ffmpeg option"""
    Low      = 51
    Medium   = 23
    High     = 18
    Veryhigh = 15
    Ultra    = 10
    Lossless = 0

# ----------------------------------------------|
# Formats

class FFmpegPixelFormat(BrokenEnum):
    """-pix_fmt ffmpeg option"""
    RGB24   = "rgb24"
    YUV420P = "yuv420p"
    YUV422P = "yuv422p"
    YUV444P = "yuv444p"

class FFmpegFormat(BrokenEnum):
    """-f ffmpeg option"""
    Rawvideo   = "rawvideo"
    Null       = "null"
    Image2pipe = "image2pipe"

# ----------------------------------------------|
# Loglevel

class FFmpegLogLevel(BrokenEnum):
    """-loglevel ffmpeg option"""
    Quiet   = "quiet"
    Panic   = "panic"
    Fatal   = "fatal"
    Error   = "error"
    Warning = "warning"
    Info    = "info"
    Verbose = "verbose"
    Debug   = "debug"
    Trace   = "trace"

# ----------------------------------------------|
# Filters

class FFmpegFilterFactory:
    def scale(width: int, height: int, filter: str="lanczos") -> str:
        return f"scale={width}:{height}:flags={filter}"

# ----------------------------------------------|
# Vsync

class FFmpegVsync(BrokenEnum):
    """-vsync ffmpeg option"""
    # "Each frame is passed with its timestamp from the demuxer to the muxer"
    Passthrough = "passthrough"

    # "Frames will be duplicated and dropped to achieve exactly the requested constant framerate"
    ConstantFramerate = "cfr"

    # "Frames are passed through with their timestamp or dropped so as to prevent 2 frames from having the same timestamp"
    VariableFramerate = "vfr"

    # "As passthrough but destroys all timestamps, making the muxer generate fresh timestamps based on frame-rate."
    Drop = "drop"

    # "Chooses between 1 and 2 depending on muxer capabilities."
    Auto = "auto"

# ----------------------------------------------|
# Hardware acceleration

class FFmpegHWAccel(BrokenEnum):
    """-hwaccel ffmpeg option"""
    Auto         = "auto"
    CUVID        = "cuvid"
    DXVA2        = "dxva2"
    QSV          = "qsv"
    VDPAU        = "vdpau"
    VAAPI        = "vaapi"

# -------------------------------------------------------------------------------------------------|

class BrokenFFmpeg:
    """
    Your Premium Fluent FFmpeg Class 💎

    The way it works is that it keeps a list of "options" that can be called in a fluent way.
    · On any given moment, only some options are available, depending on the previous options called.
    · If you try to call an option that is not available, it will print a list of available options.
    · Ideally all options have fail safes and input checking, for example .input() must be a valid file.

    It is quite hard defining what options to remove at any point, feel free to refine the class
    and send a pull request if you think you can improve it.

    # Example usage:

    ```python

    # Get video basic information
    print("Video frames:    ", BrokenFFmpeg.video_total_frames("input.mp4"))
    print("Video resolution:", BrokenFFmpeg.video_resolution("input.mp4"))

    # Iterate on all video frames as buffers
    for i, frame in enumerate(BrokenFFmpeg.video_frames("input.mp4")):
        print("Read frame", i)

    # Video transcoding with filters
    ffmpeg = (
        BrokenFFmpeg()
        .overwrite()
        .stats()
        .input("input.mp4")
        .video_codec(FFmpegVideoCodec.H264)
        .pixel(FFmpegPixelFormat.YUV444P)
        .preset(FFmpegH264Preset.Slow)
        .quality(FFmpegH264Quality.Ultra)
        .filter(FFmpegFilterFactory.scale(1280, 720))
        .output("output.mp4")
    ).run()
    """

    def __private_to_option__(self, string: str) -> str:
        """Option commands are the string between the first two dunders"""
        return string.split("__")[1]

    def __new__(cls) -> Self:
        """Creates an instance of self and returns it, allows for Class().option()"""
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        self.options = DotMap()
        self.__command__ = ["ffmpeg"]
        self.filters = []

        # Add default available options
        self.__add_option__(
            self.__input__,
            self.__resolution__,
            self.__hwaccel__,
            self.__pixel__,
            self.__output__,
            self.__loglevel__,
            self.__hide_banner__,
            self.__quiet__,
            self.__framerate__,
            self.__overwrite__,
            self.__shortest__,
            self.__stats__,
            self.__filter__,
            self.__format__,
            self.__vsync__,
            self.__no_audio__,
            self.__advanced__,
        )

    # ---------------------------------------------------------------------------------------------|
    # Options related

    def __add_option__(self, *options: callable) -> Self:
        """Add a private callback as an option for the next allowed command pipeline"""
        for option in BrokenUtils.flatten(options):
            self.options[self.__private_to_option__(option.__name__)] = option
        return self

    def __del_option__(self, *options: callable) -> Self:
        """Remove a private callback as an option for the next allowed command pipeline"""
        for option in BrokenUtils.flatten(options):
            self.options.pop(self.__private_to_option__(option.__name__))
        return self

    def __option_exists__(self, option: str) -> bool:
        """Check if an option exists, for fail safes for example"""
        return option in self.options

    def __no_option__(self) -> Self:
        """Make no option available (reset), useful after all inputs are set"""
        self.options = DotMap()
        return self

    def __skip__(self, *a, **k):
        """
        Some Fluent option errored out, continue the chain
        · It is dangerous, can yield to unexpected results and broken commands, but we shouldn't exit()
        """
        log.warning(f"BrokenFFmpeg skipped Fluent Option with args {a} and kwargs {k}")
        return self

    # # Deal with next option - to call it or list available options

    def log_options(self, _error: str=None):
        """Log available next commands"""
        _log = log.error if _error else log.info

        if _error:
            _log(f"Fluent BrokenFFmpeg has no attribute [{_error}] at this point. Available attributes are:")
        else:
            _log(f"Fluent BrokenFFmpeg has the following options available:")

        for key, callable in self.options.items():
            _log(f"• {str(key).ljust(16)} {inspect.signature(callable)}: {callable.__doc__}")

    def __getattr__(self, name) -> Self:
        """
        Returns a callable on Options if it exists, else errors out
        · This is done such that users cannot access private methods, only allowed ones
        · Private methods namings are defined on the self.__private_to_option__ method
        """
        # Next command exists and is allowed
        if callable := self.options.get(name):
            return callable

        # Command not allowed or doesn't exist
        self.log_options(_error=name)

        # Skip this fluent command
        return self.__skip__

    # ---------------------------------------------------------------------------------------------|
    # Formats

    def __pixel__(self, format: FFmpegPixelFormat) -> Self:
        """Set the pixel format for the next input"""
        format = FFmpegPixelFormat.smart(format)
        log.debug(f"BrokenFFmpeg Pixel Format: {format}")
        self.__command__ += ["-pix_fmt", format]
        return self

    def __format__(self, format: FFmpegFormat) -> Self:
        """Set the format for the next input"""
        format = FFmpegFormat.smart(format)
        log.debug(f"BrokenFFmpeg Format: {format}")
        self.__command__ += ["-f", format]
        return self

    # ---------------------------------------------------------------------------------------------|
    # Loglevel, stats

    def __loglevel__(self, loglevel: FFmpegLogLevel=FFmpegLogLevel.Error) -> Self:
        """Set the loglevel for the next input"""
        loglevel = FFmpegLogLevel.smart(loglevel)
        log.debug(f"BrokenFFmpeg Log Level: {loglevel}")
        self.__command__ += ["-loglevel", loglevel]
        self.__del_option__(self.__loglevel__)
        return self

    def __quiet__(self) -> Self:
        """Shorthand for loglevel error and hide banner"""
        self.__loglevel__(FFmpegLogLevel.Error)
        self.__hide_banner__()
        return self

    def __stats__(self) -> Self:
        """Shorthand for only showing important stats"""
        self.__loglevel__(FFmpegLogLevel.Error)
        self.__hide_banner__()
        self.__command__ += ["-stats"]
        return self

    def __hide_banner__(self) -> Self:
        """Hide the banner for the next input"""
        log.debug(f"BrokenFFmpeg Hide Banner")
        self.__command__ += ["-hide_banner"]
        self.__del_option__(self.__hide_banner__)
        return self

    # ---------------------------------------------------------------------------------------------|
    # Bitrates

    def __audio_bitrate__(self, bitrate: int) -> Self:
        """Set the audio bitrate for the next input"""
        log.debug(f"BrokenFFmpeg Audio Bitrate: {bitrate}")
        self.__command__ += ["-b:a", str(bitrate)]
        self.__del_option__(self.__audio_bitrate__)
        return self

    def __video_bitrate__(self, bitrate: int) -> Self:
        """Set the video bitrate for the next input"""
        log.debug(f"BrokenFFmpeg Video Bitrate: {bitrate}")
        self.__command__ += ["-b:v", str(bitrate)]
        self.__del_option__(self.__video_bitrate__)
        return self

    # ---------------------------------------------------------------------------------------------|
    # Special

    def __hwaccel__(self, hwaccel: str="auto") -> Self:
        """Set hardware acceleration"""
        self.__command__ += ["-hwaccel", hwaccel]
        return self

    def __overwrite__(self) -> Self:
        """Overwrite output files"""
        self.__command__ += ["-y"]
        self.__del_option__(self.__overwrite__)
        return self

    def __shortest__(self) -> Self:
        """Stop encoding when the shortest input ends"""
        self.__command__ += ["-shortest"]
        self.__del_option__(self.__shortest__)
        return self

    def __no_audio__(self) -> Self:
        """Do not include audio in the output"""
        self.__command__ += ["-an"]
        self.__del_option__(self.__no_audio__)
        return self

    def __map__(self, input_stream: int, stream: Option["v", "a"], output_stream: int) -> Self:
        """
        Map input stream to output stream, for example `-map 0:v:0 -map 1:a:0 maps` does:
        - Input (v)ideo stream 0, to output (v)ideo stream 0
        - Input (a)udio stream 1, to output (a)udio stream 0
        """
        self.__command__ += ["-map", f"{input_stream}:{stream}:{output_stream}"]
        return self

    def __advanced__(self, *command: list[str]) -> Self:
        """Add an custom advanced command on the pipeline"""
        self.__command__ += command
        return self

    # ---------------------------------------------------------------------------------------------|
    # Input, output

    def __input__(self, path: str) -> Self:
        """Input some audio file, video file, or pipe '-' from stdin"""

        # Allow pipe from stdin
        if path == "-":
            pass

        elif not (path := Path(path)).exists():
            log.error(f"Input file {path} does not exist")
            return self

        # Add command
        log.debug(f"BrokenFFmpeg Input: [{path}]")
        self.__command__ += ["-i", path]
        self.__add_option__(
            self.__resolution__,
            self.__video_codec__,
            self.__framerate__,
            self.__audio_bitrate__,
            self.__video_bitrate__,
        )
        return self

    def __output__(self, path: str) -> Self:
        """Output some audio file, video file"""
        BrokenPath.mkdir(Path(path).parent)

        # Add video filters
        if self.filters:
            filters = ",".join(self.filters)
            log.debug(f"BrokenFFmpeg Filters: {filters}")
            self.__command__ += ["-vf", filters]

        # Add command
        log.debug(f"BrokenFFmpeg Output: [{path}]")
        self.__command__ += [path]
        self.__no_option__()
        return self

    # ---------------------------------------------------------------------------------------------|
    # Sizes, framerates, filter

    def __filter__(self, *filters: str) -> Self:
        """Send filters strings from FFmpegFilterFactory or manually (advanced)"""
        self.filters.extend(filters)
        return self

    def __resolution__(self, width: int, height: int) -> Self:
        """Set the next input or output resolution"""
        log.debug(f"BrokenFFmpeg Resolution: {width}x{height}")
        self.__command__ += ["-s", f"{int(width)}x{int(height)}"]
        self.__del_option__(self.__resolution__)
        return self

    def __framerate__(self, framerate: int) -> Self:
        """Set the framerate for the next input"""
        log.debug(f"BrokenFFmpeg Framerate: {framerate}")
        self.__command__ += ["-r", framerate]
        self.__del_option__(self.__framerate__)
        return self

    def __vsync__(self, vsync: FFmpegVsync=FFmpegVsync.ConstantFramerate) -> Self:
        """Set the vsync for the next input"""
        vsync = FFmpegVsync.smart(vsync)
        log.debug(f"BrokenFFmpeg Vsync: {vsync}")
        self.__command__ += ["-vsync", vsync]
        self.__del_option__(self.__vsync__)
        return self

    # ---------------------------------------------------------------------------------------------|
    # Base codecs

    def __video_codec__(self, codec: FFmpegVideoCodec=FFmpegVideoCodec.H264) -> Self:
        """Set the video codec"""
        codec = FFmpegVideoCodec.smart(codec)

        log.debug(f"BrokenFFmpeg Video Codec: {codec}")

        if codec == FFmpegVideoCodec.H264:
            self.__add_option__(
                self.__preset__h264,
                self.__tune__h264,
                self.__profile__h264,
                self.__quality__h265,
            )
        elif codec == FFmpegVideoCodec.H265:
            self.__add_option__(
                self.__preset__h265,
                self.__tune__h265,
                self.__profile__h265,
                self.__quality__h265,
            )
        elif codec == FFmpegVideoCodec.AV1:
            raise NotImplementedError("AV1 is not supported yet")
        elif codec == FFmpegVideoCodec.Copy:
            pass
        elif codec == FFmpegVideoCodec.Rawvideo:
            pass
        else:
            log.error(f"Video codec {codec} not supported")
            return self.__skip__

        self.__command__ += ["-c:v", codec]
        self.__del_option__(
            self.__video_codec__,
            self.__hwaccel__,
        )
        return self

    def __audio_codec__(self, codec: FFmpegAudioCodec=FFmpegAudioCodec.AAC) -> Self:
        """Set the audio codec"""
        codec = FFmpegAudioCodec.smart(codec)
        log.debug(f"BrokenFFmpeg Audio Codec: {codec}")
        self.__command__ += ["-c:a", codec]
        self.__del_option__(self.__audio_codec__)
        return self

    # ---------------------------------------------------------------------------------------------|
    # H264

    def __preset__h264(self, preset: FFmpegH264Preset=FFmpegH264Preset.Slow) -> Self:
        """Set the next h264 preset"""
        preset = FFmpegH264Preset.smart(preset)
        log.debug(f"BrokenFFmpeg H264 Preset: {preset}")
        self.__command__ += ["-preset", preset]
        self.__del_option__(self.__preset__h264)
        return self

    def __tune__h264(self, tune: FFmpegH264Tune=FFmpegH264Tune.Film) -> Self:
        """Set the next h264 tune"""
        tune = FFmpegH264Tune.smart(tune)
        log.debug(f"BrokenFFmpeg H264 Tune: {tune}")
        self.__command__ += ["-tune", tune]
        self.__del_option__(self.__tune__h264)
        return self

    def __profile__h264(self, profile: FFmpegH264Profile=FFmpegH264Profile.Main) -> Self:
        """Set the next h264 profile"""
        profile = FFmpegH264Profile.smart(profile)
        log.debug(f"BrokenFFmpeg H264 Profile: {profile}")
        self.__command__ += ["-profile:v", profile]
        self.__del_option__(self.__profile__h264)
        return self

    def __quality__h264(self, quality: FFmpegH264Quality=FFmpegH264Quality.High) -> Self:
        """Set the next h264 quality"""
        quality = FFmpegH264Quality.smart(quality)
        log.debug(f"BrokenFFmpeg H264 Quality: {quality}")
        self.__command__ += ["-crf", quality]
        self.__del_option__(self.__quality__h264)
        return self

    # ---------------------------------------------------------------------------------------------|
    # H265

    def __preset__h265(self, preset: FFmpegH265Preset=FFmpegH265Preset.Slow) -> Self:
        """Set the next H265 preset"""
        preset = FFmpegH265Preset.smart(preset)
        log.debug(f"BrokenFFmpeg H265 Preset: {preset}")
        self.__command__ += ["-preset", preset]
        self.__del_option__(self.__preset__h265)
        return self

    def __tune__h265(self, tune: FFmpegH265Tune) -> Self:
        """Set the next H265 tune"""
        tune = FFmpegH265Tune.smart(tune)
        log.debug(f"BrokenFFmpeg H265 Tune: {tune}")
        self.__command__ += ["-tune", tune]
        self.__del_option__(self.__tune__h265)
        return self

    def __profile__h265(self, profile: FFmpegH265Profile=FFmpegH265Profile.Main) -> Self:
        """Set the next H265 profile"""
        profile = FFmpegH265Profile.smart(profile)
        log.debug(f"BrokenFFmpeg H265 Profile: {profile}")
        self.__command__ += ["-profile:v", profile]
        self.__del_option__(self.__profile__h265)
        return self

    def __quality__h265(self, quality: FFmpegH264Quality.High) -> Self:
        """Set the next H265 quality"""
        quality = FFmpegH265Quality.smart(quality)
        log.debug(f"BrokenFFmpeg H265 Quality: {quality}")
        self.__command__ += ["-crf", quality]
        self.__del_option__(self.__quality__h265)
        return self

    # ---------------------------------------------------------------------------------------------|
    # End user manual actions

    @property
    def command(self) -> List[str]:
        return BrokenUtils.denum(BrokenUtils.flatten(self.__command__))

    def run(self, output: bool=False) -> Union[None, subprocess.Popen]:

        # self.ffmpeg = shell(command)
        self.ffmpeg = shell(
            self.command,
            Popen=("-i", "-") in self.command,
            stdin=PIPE,
            output=output,
        )
        return self.ffmpeg

    def close(self) -> None:
        self.ffmpeg.stdin.close()
        return self

    # ---------------------------------------------------------------------------------------------|
    # High level functions

    @staticmethod
    def video_total_frames(path: PathLike) -> Option[int, None]:
        """Count the total frames of a video FAST, returns int if video exists"""
        if not Path(path).exists():
            log.error(f"Get video total frames Path [{path}] does not exist")
            return None

        log.info(f"Finding Frame Count of video [{path}], might take a while..")

        # Build the command to be run (needed because stderr=PIPE)
        command = (
            BrokenFFmpeg()
            .vsync(FFmpegVsync.ConstantFramerate)
            .input(path)
            .format(FFmpegFormat.Null)
            .output("-")
        ).command

        # Run it, parse output
        return int(shell(command, stderr=PIPE).stderr.decode("utf-8").split("frame=")[-1].split("fps=")[0].strip())

    @staticmethod
    def video_resolution(path: Path) -> Option[Tuple[int, int], None]:
        """Get the resolution of a video SMARTLY, returns tuple if video exists"""
        if not Path(path).exists():
            log.error(f"Get video resolution Path [{path}] does not exist")
            return None

        log.info(f"Finding Resolution of video [{path}], might take a while..")

        command = (
            BrokenFFmpeg()
            .quiet()
            .input(path)
            .advanced("-vframes", "1")
            .format(FFmpegFormat.Image2pipe)
            .output("-")
        ).command

        # Build the command to be run (needed because stderr=PIPE)
        return PIL.Image.open(io.BytesIO(
            shell(command, stdout=PIPE, stderr=PIPE).stdout
        ), formats=["jpeg"]).size

    @staticmethod
    def video_frames(path: PathLike) -> Option[Iterable[numpy.ndarray], None]:
        """Generator for every frame of the video as numpy arrays, FAST!"""
        if not Path(path).exists():
            log.error(f"Get video frames Path [{path}] does not exist")
            return None

        # Get resolution of the video (so we now how many bytes to read a frame)
        (width, height) = BrokenFFmpeg.video_resolution(path)

        # Build the command to be run (needed because stderr=PIPE)
        command = (
            BrokenFFmpeg()
            .hwaccel(FFmpegHWAccel.Auto)
            .vsync(FFmpegVsync.ConstantFramerate)
            .loglevel(FFmpegLogLevel.Panic)
            .input(path)
            .video_codec(FFmpegVideoCodec.Rawvideo)
            .format(FFmpegFormat.Rawvideo)
            .pixel(FFmpegPixelFormat.RGB24)
            .no_audio()
            .output("-")
        ).command

        # Popen the frames reading FFmpeg
        ffmpeg = shell(
            command,
            Popen=True,
            stdout=PIPE,
        )

        # Keep reading frames until we run out (should be equal to video_total_frames)
        while True:
            if not (raw := ffmpeg.stdout.read(width * height * 3)):
                break
            yield numpy.frombuffer(raw, dtype=numpy.uint8).reshape((height, width, 3))

