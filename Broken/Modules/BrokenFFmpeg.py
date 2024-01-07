"""State of the art FFmpeg class. See BrokenFFmpeg for more info"""
from __future__ import annotations

from . import *

# ----------------------------------------------|
# Resolution

@define
class FFmpegResolution:
    width:  int = field(converter=int)
    height: int = field(converter=int)

    @width.validator
    @height.validator
    def check(self, attribute, value):
        if value < 0:
            raise ValueError(f"FFmpegResolution {attribute.name} must be positive")

    def __mul__(self, ratio: float) -> Self:
        return FFmpegResolution(
            width=self.width*ratio,
            height=self.height*ratio
        )

    def __truediv__(self, ratio: float) -> Self:
        return self.__mul__(1/ratio)

    def aspect_ratio(self) -> float:
        return self.width / self.height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

class FFmpegResolutionEnum(BrokenEnum):
    """
    Common resolutions for videos and images enumerator

    Aspect ratios:
        - Standard:  4:3
        - Wide:      16:9 or 16:10
        - UltraWide: 21:9
        - SuperWide: 32:9
        - Univisium: 2:1

    Resolutions:
        - SD:   480p
        - HD:   720p
        - FHD: 1080p
        - QHD: 1440p
        - 4K:  2160p
        - 8K:  4320p
        - 16K: 8640p
    """

    # 480p
    Standard_480p_SD     = FFmpegResolution(  640,  480)
    Wide16x9_480p_SD     = FFmpegResolution(  854,  480)
    Wide16x10_480p_SD    = FFmpegResolution(  720,  534)
    UltraWide_480p_SD    = FFmpegResolution( 1140,  480)
    SuperWide_480p_SD    = FFmpegResolution( 1706,  480)
    Univisium_480p_SD    = FFmpegResolution(  960,  480)

    # 720p
    Standard_720p_HD     = FFmpegResolution(  960,  720)
    Wide16x9_720p_HD     = FFmpegResolution( 1280,  720)
    Wide16x10_720p_HD    = FFmpegResolution( 1280,  800)
    UltraWide_720p_HD    = FFmpegResolution( 1720,  720)
    SuperWide_720p_HD    = FFmpegResolution( 2560,  720)
    Univisium_720p_HD    = FFmpegResolution( 1440,  720)

    # 1080p
    Standard_1080p_FHD   = FFmpegResolution( 1440, 1080)
    Wide16x9_1080p_FHD   = FFmpegResolution( 1920, 1080)
    Wide16x10_1080p_FHD  = FFmpegResolution( 1920, 1200)
    UltraWide_1080p_FHD  = FFmpegResolution( 2560, 1080)
    SuperWide_1080p_FHD  = FFmpegResolution( 3840, 1080)
    Univisium_1080p_FHD  = FFmpegResolution( 2160, 1080)

    # 1440p
    Standard_1440p_QHD   = FFmpegResolution( 1920, 1440)
    Wide16x9_1440p_QHD   = FFmpegResolution( 2560, 1440)
    Wide16x10_1440p_QHD  = FFmpegResolution( 2560, 1600)
    UltraWide_1440p_QHD  = FFmpegResolution( 3440, 1440)
    SuperWide_1440p_QHD  = FFmpegResolution( 5120, 1440)
    Univisium_1440p_QHD  = FFmpegResolution( 2880, 1440)

    # 2160p
    Standard_2160p_4K    = FFmpegResolution( 2880, 2160)
    Wide16x9_2160p_4K    = FFmpegResolution( 3840, 2160)
    Wide16x10_2160p_4K   = FFmpegResolution( 3840, 2400)
    UltraWide_2160p_4K   = FFmpegResolution( 5120, 2160)
    SuperWide_2160p_4K   = FFmpegResolution( 7680, 2160)
    Univisium_2160p_4K   = FFmpegResolution( 4320, 2160)

    # 4320p
    Standard_4320p_8K    = FFmpegResolution( 5760, 4320)
    Wide16x9_4320p_8K    = FFmpegResolution( 7680, 4320)
    Wide16x10_4320p_8K   = FFmpegResolution( 7680, 4800)
    UltraWide_4320p_8K   = FFmpegResolution(10240, 4320)
    SuperWide_4320p_8K   = FFmpegResolution(15360, 4320)
    Univisium_4320p_8K   = FFmpegResolution( 8640, 4320)

    # 8640p
    Standard_8640p_16K   = FFmpegResolution(11520, 8640)
    Wide16x9_8640p_16K   = FFmpegResolution(15360, 8640)
    Wide16x10_8640p_16K  = FFmpegResolution(15360, 9600)
    UltraWide_8640p_16K  = FFmpegResolution(20480, 8640)
    SuperWide_8640p_16K  = FFmpegResolution(30720, 8640)
    Univisium_8640p_16K  = FFmpegResolution(17280, 8640)

# ----------------------------------------------|
# Codecs

class FFmpegVideoCodec(BrokenEnum):
    """-c:v ffmpeg option"""
    # H264, AVC - Advanced Video Coding
    H264       = "libx264"
    H264_NVENC = "h264_nvenc"

    # H265, HEVC - High Efficiency Video Encoding
    H265       = "libx265"
    H265_NVENC = "hevc_nvenc"

    # Alliance for Open Media Video Codec - AV1
    AV1        = "libaom-av1"
    AV1_NVENC  = "av1_nvenc"

    # Raw, special
    Rawvideo   = "rawvideo"
    Copy       = "copy"

    @staticmethod
    def is_nvenc(option: FFmpegVideoCodec):
        option = FFmpegVideoCodec.smart(option)
        return "nvenc" in option.value

class FFmpegAudioCodec(BrokenEnum):
    """-c:a ffmpeg option"""
    AAC    = "aac"
    MP3    = "libmp3lame"
    VORBIS = "libvorbis"
    OPUS   = "libopus"
    FLAC   = "flac"
    AC3    = "ac3"
    Copy   = "copy"

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
# Generic NVENC

class FFmpegNVENC_Preset(BrokenEnum):
    """-preset h264_nvenc ffmpeg option"""
    # Default is P4
    Default = "default"

    # Similar to H264 Software
    HQ2PassesSlow = "slow"
    HQ1PassMedium = "medium"
    HP1PassFast   = "fast"

    HP = "hp"
    HQ = "hq"
    BD = "bd"

    # Streaming ones
    LowLatency   = "ll"
    LowLatencyHQ = "llhq"
    LowLatencyHP = "llhp"
    Lossless     = "lossless"
    LosslessHP   = "losslesshp"

    # "Common" ones
    Fastest = "p1"
    Faster  = "p2"
    Fast    = "p3"
    Medium  = "p4"
    Slow    = "p5"
    Slower  = "p6"
    Slowest = "p7"

class FFmpegNVENC_Tune(BrokenEnum):
    """-tune h264_nvenc ffmpeg option"""
    HighQuality     = "hq"
    LowLatency      = "ll"
    UltraLowLatency = "ull"
    Lossless        = "lossless"

class FFmpegNVENC_Level(BrokenEnum):
    """-level h264_nvenc ffmpeg option"""
    Auto    = "auto"
    Level10 = "1"
    Level1b = "1b"
    Level11 = "1.1"
    Level12 = "1.2"
    Level13 = "1.3"
    Level20 = "2.0"
    Level21 = "2.1"
    Level22 = "2.2"
    Level30 = "3.0"
    Level31 = "3.1"
    Level32 = "3.2"
    Level40 = "4.0"
    Level41 = "4.1"
    Level42 = "4.2"
    Level50 = "5.0"
    Level51 = "5.1"
    Level52 = "5.2"
    Level60 = "6.0"
    Level61 = "6.1"
    Level62 = "6.2"

class FFmpegNVENC_RC(BrokenEnum):
    """-rc h264_nvenc ffmpeg option"""
    ConstantQP                 = "constqp"
    VariableBitrate            = "vbr"
    VariableBitrateHighQuality = "vbr_hq"
    ConstantBitrate            = "cbr"
    ConstantBitrateHighQuality = "cbr_hq"

class FFmpegNVENC_B_Ref_Mode(BrokenEnum):
    Disabled = "disabled"
    Each     = "each"
    Middle   = "middle"

# ----------------------------------------------|
# H264 NVENC

class FFmpegH264_NVENC_Profile(BrokenEnum):
    """-profile h264_nvenc ffmpeg option"""
    Baseline = "baseline"
    Main     = "main"
    High     = "high"
    High444  = "high444"

# ----------------------------------------------|
# H265 NVENC

class FFmpegH265_NVENC_Profile(BrokenEnum):
    """-profile hevc_nvenc ffmpeg option"""
    Main   = "main"
    Main10 = "main10"
    Rext   = "rext"

class FFmpegH265_NVENC__Tier(BrokenEnum):
    """-tier hevc_nvenc ffmpeg option"""
    Main = "main"
    High = "high"

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

    def flip_vertical() -> str:
        return "vflip"

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

    def __call__(self, *args, **kwargs) -> Self:
        return self

    def __init__(self):
        self.options = DotMap()
        self.set_ffmpeg_binary()
        self.__command__ = []
        self.filters = []

        # Add default available options
        self.__add_option__(
            self.__custom__,
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
            self.__audio_codec__,
        )

    def set_ffmpeg_binary(self, binary: Path=None) -> Self:
        """Set the ffmpeg binary to use, by default it is 'ffmpeg'"""
        if binary:
            log.info(f"Using custom FFmpeg binary {binary}")
        elif (binary := shutil.which("ffmpeg")):
            log.info(f"Using system FFmpeg binary at [{binary}]")
        if not binary:
            import imageio_ffmpeg
            binary = Path(imageio_ffmpeg.get_ffmpeg_exe())
            log.info(f"Using ImageIO FFmpeg binary at [{binary}]")
        if not binary:
            log.error(f"Could not find (FFmpeg) binary on PATH and don't have (ImageIO FFmpeg) package, please install it")
            exit(1)

        self.__ffmpeg__ = binary
        return self

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
        log.warning(f"Skipped Fluent Option with args {a} and kwargs {k}")
        return self

    def __smart__(self,
        *items: list[Any],
        delete: Union[callable, list[callable]]=None,
        add:    Union[callable, list[callable]]=None,
    ) -> Self:
        """Append items to the command, maybe delete or add new callbacks to the options"""
        log.debug(f"BrokenFFmpeg Append: {items}")
        self.__command__ += items
        self.__del_option__(delete)
        self.__add_option__(add)
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
    # Custom

    def __custom__(self, *command: list[str]) -> Self:
        """Add an custom command on the pipeline"""
        self.__command__ += command
        return self

    # ---------------------------------------------------------------------------------------------|
    # Formats

    def __pixel__(self, option: FFmpegPixelFormat) -> Self:
        return self.__smart__("-pix_fmt", FFmpegPixelFormat.smart(option), delete=self.__pixel__)

    def __format__(self, option: FFmpegFormat) -> Self:
        return self.__smart__("-f", FFmpegFormat.smart(option), delete=self.__format__)

    # ---------------------------------------------------------------------------------------------|
    # Loglevel, stats

    def __loglevel__(self, option: FFmpegLogLevel=FFmpegLogLevel.Error) -> Self:
        return self.__smart__("-loglevel", FFmpegLogLevel.smart(option), delete=self.__loglevel__)

    def __quiet__(self) -> Self:
        """Shorthand for loglevel error and hide banner"""
        self.__loglevel__(FFmpegLogLevel.Error)
        self.__hide_banner__()
        return self

    def __stats__(self) -> Self:
        """Shorthand for only showing important stats"""
        self.__loglevel__(FFmpegLogLevel.Error)
        self.__hide_banner__()
        return self.__smart__("-stats", delete=self.__stats__)

    def __hide_banner__(self) -> Self:
        return self.__smart__("-hide_banner", delete=self.__hide_banner__)

    # ---------------------------------------------------------------------------------------------|
    # Bitrates

    def __audio_bitrate__(self, option: int) -> Self:
        return self.__smart__("-b:a", str(option), delete=self.__audio_bitrate__)

    def __video_bitrate__(self, option: int) -> Self:
        return self.__smart__("-b:v", str(option), delete=self.__video_bitrate__)

    # ---------------------------------------------------------------------------------------------|
    # Special

    def __hwaccel__(self, option: FFmpegHWAccel=FFmpegHWAccel.Auto) -> Self:
        return self.__smart__("-hwaccel", FFmpegHWAccel.smart(option), delete=self.__hwaccel__)

    def __overwrite__(self) -> Self:
        return self.__smart__("-y", delete=self.__overwrite__)

    def __shortest__(self) -> Self:
        return self.__smart__("-shortest", delete=self.__shortest__)

    def __no_audio__(self) -> Self:
        return self.__smart__("-an", delete=self.__no_audio__)

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
        self.__smart__("-i", path, add=(
            self.__resolution__,
            self.__video_codec__,
            self.__framerate__,
            self.__audio_bitrate__,
            self.__video_bitrate__,
            self.__map__,
            self.__pixel__,
        ))
        return self

    def __output__(self, path: str) -> Self:
        """Output some audio file, video file"""
        BrokenPath.mkdir(Path(path).parent, echo=False)

        # Add video filters
        if self.filters:
            log.debug(f"BrokenFFmpeg Filters:")
            for filter in self.filters:
                log.debug(f"• {filter}")
            self.__command__ += ["-vf", ",".join(self.filters)]

        # Add command
        self.__no_option__()
        return self.__smart__(path, delete=self.__overwrite__)

    # ---------------------------------------------------------------------------------------------|
    # Sizes, framerates, filter

    def __filter__(self, *filters: str) -> Self:
        """Send filters strings from FFmpegFilterFactory or manually (advanced)"""
        self.filters.extend(filters)
        return self

    def __resolution__(self, width: FFmpegResolution | int, height: int=None) -> Self:
        if isinstance(width, (list, tuple)):
            width, height = width
        if not isinstance(width, FFmpegResolution):
            width = FFmpegResolution(width, height)
        return self.__smart__("-s", str(width), delete=self.__resolution__)

    def __framerate__(self, option: int) -> Self:
        return self.__smart__("-framerate", option, delete=self.__framerate__)

    def __vsync__(self, option: FFmpegVsync=FFmpegVsync.ConstantFramerate) -> Self:
        return self.__smart__("-vsync", option, delete=self.__vsync__)

    # ---------------------------------------------------------------------------------------------|
    # Base codecs

    def __video_codec__(self, codec: FFmpegVideoCodec=FFmpegVideoCodec.H264) -> Self:
        codec = FFmpegVideoCodec.smart(codec)

        # Add codec parameters options based on selected
        if codec == FFmpegVideoCodec.H264:
            self.__add_option__(
                self.__preset__h264,
                self.__tune__h264,
                self.__profile__h264,
                self.__quality__h264,
            )
        elif FFmpegVideoCodec.is_nvenc(codec):
            self.__add_option__(
                self.__preset__nvenc,
                self.__tune__nvenc,
                self.__level__nvenc,
                self.__rc__nvenc,
                self.__gpu__nvenc,
                self.__rate_control_lookahead__nvenc,
                self.__surfaces__nvenc,
                self.__qp__nvenc,
                self.__bref_mode__nvenc,
            )
            if codec == FFmpegVideoCodec.H264_NVENC:
                self.__add_option__(
                    self.__profile__h264_nvenc,
                )
            elif codec == FFmpegVideoCodec.H265_NVENC:
                self.__add_option__(
                    self.__profile__h265_nvenc,
                    self.__tier__h265_nvenc,
                )
            elif codec == FFmpegVideoCodec.AV1_NVENC:
                log.error(f"We don't have any RTX 4000 card to test AV1 NVENC")
                return self.__skip__

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
            pass # Copy is self contained
        elif codec == FFmpegVideoCodec.Rawvideo:
            pass # Configured with format
        else:
            log.error(f"Video codec {codec} not supported")
            return self.__skip__

        return self.__smart__("-c:v", codec, delete=(
            self.__video_codec__,
            self.__hwaccel__,
        ))

    def __audio_codec__(self, codec: FFmpegAudioCodec=FFmpegAudioCodec.AAC) -> Self:
        return self.__smart__("-c:a", FFmpegAudioCodec.smart(codec), delete=self.__audio_codec__)

    # ---------------------------------------------------------------------------------------------|
    # Generic NVENC

    def __gpu__nvenc(self, option: int=0) -> Self:
        return self.__smart__("-gpu", option, delete=self.__gpu__nvenc)

    def __rate_control_lookahead__nvenc(self, option: int=0) -> Self:
        return self.__smart__("-rc-lookahead", option, delete=self.__rate_control_lookahead__nvenc)

    def __surfaces__nvenc(self, option: Union[int, range(0, 65)]=0) -> Self:
        return self.__smart__("-surfaces", min(max(option, 0), 64), delete=self.__surfaces__nvenc)

    def __qp__nvenc(self, option: Union[int, range(-1, 51)]=-1) -> Self:
        return self.__smart__("-qp", option, delete=self.__qp__nvenc)

    def __bref_mode__nvenc(self, option: FFmpegNVENC_B_Ref_Mode=FFmpegNVENC_B_Ref_Mode.Disabled) -> Self:
        log.warning("B Frames requires Turing or newer architecture (RTX 2000+)")
        return self.__smart__("-b_ref_mode", FFmpegNVENC_B_Ref_Mode.smart(option), delete=self.__bref_mode__nvenc)

    def __preset__nvenc(self, option: FFmpegNVENC_Preset=FFmpegNVENC_Preset.Slower) -> Self:
        return self.__smart__("-preset", FFmpegNVENC_Preset.smart(option), delete=self.__preset__nvenc)

    def __tune__nvenc(self, option: FFmpegNVENC_Tune=FFmpegNVENC_Tune.HighQuality) -> Self:
        return self.__smart__("-tune", FFmpegNVENC_Tune.smart(option), delete=self.__tune__nvenc)

    def __level__nvenc(self, option: FFmpegNVENC_Level=FFmpegNVENC_Level.Auto) -> Self:
        return self.__smart__("-level", FFmpegNVENC_Level.smart(option), delete=self.__level__nvenc)

    def __rc__nvenc(self, option: FFmpegNVENC_RC=FFmpegNVENC_RC.VariableBitrateHighQuality) -> Self:
        return self.__smart__("-rc", FFmpegNVENC_RC.smart(option), delete=self.__rc__nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H264 NVENC

    def __profile__h264_nvenc(self, option: FFmpegH264_NVENC_Profile=FFmpegH264_NVENC_Profile.Main) -> Self:
        return self.__smart__("-profile", FFmpegH264_NVENC_Profile.smart(option), delete=self.__profile__h264_nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H265 NVENC

    def __profile__h265_nvenc(self, option: FFmpegH265_NVENC_Profile=FFmpegH265_NVENC_Profile.Main) -> Self:
        return self.__smart__("-profile", FFmpegH265_NVENC_Profile.smart(option), delete=self.__profile__h265_nvenc)

    def __tier__h265_nvenc(self, option: FFmpegH265_NVENC__Tier=FFmpegH265_NVENC__Tier.Main) -> Self:
        return self.__smart__("-tier", FFmpegH265_NVENC__Tier.smart(option), delete=self.__tier__h265_nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H264

    def __preset__h264(self, option: FFmpegH264Preset=FFmpegH264Preset.Slow) -> Self:
        return self.__smart__("-preset", FFmpegH264Preset.smart(option), delete=self.__preset__h264)

    def __tune__h264(self, option: FFmpegH264Tune=FFmpegH264Tune.Film) -> Self:
        return self.__smart__("-tune", FFmpegH264Tune.smart(option), delete=self.__tune__h264)

    def __profile__h264(self, option: FFmpegH264Profile=FFmpegH264Profile.Main) -> Self:
        return self.__smart__("-profile:v", FFmpegH264Profile.smart(option), delete=self.__profile__h264)

    def __quality__h264(self, option: FFmpegH264Quality=FFmpegH264Quality.High) -> Self:
        return self.__smart__("-crf", FFmpegH264Quality.smart(option), delete=self.__quality__h264)

    # ---------------------------------------------------------------------------------------------|
    # H265

    def __preset__h265(self, option: FFmpegH265Preset=FFmpegH265Preset.Slow) -> Self:
        return self.__smart__("-preset", FFmpegH265Preset.smart(option), delete=self.__preset__h265)

    def __tune__h265(self, option: FFmpegH265Tune) -> Self:
        return self.__smart__("-tune", FFmpegH265Tune.smart(option), delete=self.__tune__h265)

    def __profile__h265(self, option: FFmpegH265Profile=FFmpegH265Profile.Main) -> Self:
        return self.__smart__("-profile:v", FFmpegH265Profile.smart(option), delete=self.__profile__h265)

    def __quality__h265(self, option: FFmpegH264Quality.High) -> Self:
        return self.__smart__("-crf", FFmpegH264Quality.smart(option), delete=self.__quality__h265)

    # ---------------------------------------------------------------------------------------------|
    # End user manual actions

    @property
    def command(self) -> List[str]:
        return BrokenUtils.denum(BrokenUtils.flatten([self.__ffmpeg__] + self.__command__))

    def run(self) -> subprocess.CompletedProcess:
        return shell(self.command)

    def popen(self) -> subprocess.stdin:
        return shell(self.command, Popen=True)

    def pipe(self, open: bool=True, buffer: int=100):
        """Spawns a Popen process of BrokenFFmpeg that is buffered, use .write(data: bytes) and .close()"""
        if not open: return

        # Spawn subprocess
        ffmpeg = shell(self.command, Popen=True, stdin=subprocess.PIPE)

        @define
        class BrokenFFmpegBuffered:
            ffmpeg: subprocess.Popen
            buffer: int
            frames: List[bytes] = Factory(list)
            __stop__: bool = False

            def __attrs_post_init__(self):
                """Starts worker thread"""
                BrokenUtils.better_thread(self.__worker__)

            def write(self, frame: bytes):
                """Write a frame to the pipe, if the buffer is full, wait for it to be empty"""
                self.frames.append(frame)
                while len(self.frames) > self.buffer:
                    time.sleep(0.01)

            def close(self):
                """Wait for all frames to be written and close the pipe"""
                self.__stop__ = True
                with halo.Halo() as spinner:
                    while self.frames:
                        spinner.text = f"Waiting for ({len(self.frames):4}) frames to be written to FFmpeg"
                        time.sleep(0.05)
                with halo.Halo("Waiting FFmpeg process to finish rendering") as spinner:
                    while not self.ffmpeg.stdin.closed:
                        time.sleep(0.05)

            def __worker__(self):
                while True:
                    # If there is frames to write, write them
                    if self.frames:
                        self.ffmpeg.stdin.write(self.frames.pop(0))
                        continue
                    if self.__stop__:
                        break
                    time.sleep(0.01)
                self.ffmpeg.stdin.close()

        return BrokenFFmpegBuffered(ffmpeg=ffmpeg, buffer=buffer)

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

