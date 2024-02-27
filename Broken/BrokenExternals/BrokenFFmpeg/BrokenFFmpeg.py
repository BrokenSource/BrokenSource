"""State of the art FFmpeg class. See BrokenFFmpeg for more info"""
from __future__ import annotations

from . import *

# ----------------------------------------------|
# Resolution

@define
class FFmpegResolution:
    width:  int = Field(converter=int)
    height: int = Field(converter=int)

    @width.validator
    @height.validator
    def check(self, attribute, value):
        if value < 0:
            raise ValueError(f"FFmpegResolution {attribute.name} must be positive")

    def __mul__(self, ratio: float) -> Self:
        self.width  *= ratio
        self.height *= ratio
        return self

    def __truediv__(self, ratio: float) -> Self:
        self.width  /= ratio
        self.height /= ratio
        return self

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
        option = FFmpegVideoCodec.get(option)
        return "nvenc" in option.value

class FFmpegPCM(BrokenEnum):
    # Raw pcm formats `ffmpeg -formats | grep PCM`
    PCM_FLOAT_32_BITS_BIG_ENDIAN       = "f32be"
    PCM_FLOAT_32_BITS_LITTLE_ENDIAN    = "f32le"
    PCM_FLOAT_64_BITS_BIG_ENDIAN       = "f64be"
    PCM_FLOAT_64_BITS_LITTLE_ENDIAN    = "f64le"
    PCM_SIGNED_16_BITS_BIG_ENDIAN      = "s16be"
    PCM_SIGNED_16_BITS_LITTLE_ENDIAN   = "s16le"
    PCM_SIGNED_24_BITS_BIG_ENDIAN      = "s24be"
    PCM_SIGNED_24_BITS_LITTLE_ENDIAN   = "s24le"
    PCM_SIGNED_32_BITS_BIG_ENDIAN      = "s32be"
    PCM_SIGNED_32_BITS_LITTLE_ENDIAN   = "s32le"
    PCM_UNSIGNED_16_BITS_BIG_ENDIAN    = "u16be"
    PCM_UNSIGNED_16_BITS_LITTLE_ENDIAN = "u16le"
    PCM_UNSIGNED_24_BITS_BIG_ENDIAN    = "u24be"
    PCM_UNSIGNED_24_BITS_LITTLE_ENDIAN = "u24le"
    PCM_UNSIGNED_32_BITS_BIG_ENDIAN    = "u32be"
    PCM_UNSIGNED_32_BITS_LITTLE_ENDIAN = "u32le"
    PCM_UNSIGNED_8_BITS                = "u8"
    PCM_SIGNED_8_BITS                  = "s8"

class FFmpegAudioCodec(BrokenEnum):
    """-c:a ffmpeg option"""
    AAC    = "aac"
    MP3    = "libmp3lame"
    VORBIS = "libvorbis"
    OPUS   = "libopus"
    FLAC   = "flac"
    AC3    = "ac3"
    Copy   = "copy"

    # Raw pcm formats `ffmpeg -formats | grep PCM`
    PCM_FLOAT_32_BITS_BIG_ENDIAN       = "pcm_f32be"
    PCM_FLOAT_32_BITS_LITTLE_ENDIAN    = "pcm_f32le"
    PCM_FLOAT_64_BITS_BIG_ENDIAN       = "pcm_f64be"
    PCM_FLOAT_64_BITS_LITTLE_ENDIAN    = "pcm_f64le"
    PCM_SIGNED_16_BITS_BIG_ENDIAN      = "pcm_s16be"
    PCM_SIGNED_16_BITS_LITTLE_ENDIAN   = "pcm_s16le"
    PCM_SIGNED_24_BITS_BIG_ENDIAN      = "pcm_s24be"
    PCM_SIGNED_24_BITS_LITTLE_ENDIAN   = "pcm_s24le"
    PCM_SIGNED_32_BITS_BIG_ENDIAN      = "pcm_s32be"
    PCM_SIGNED_32_BITS_LITTLE_ENDIAN   = "pcm_s32le"
    PCM_UNSIGNED_16_BITS_BIG_ENDIAN    = "pcm_u16be"
    PCM_UNSIGNED_16_BITS_LITTLE_ENDIAN = "pcm_u16le"
    PCM_UNSIGNED_24_BITS_BIG_ENDIAN    = "pcm_u24be"
    PCM_UNSIGNED_24_BITS_LITTLE_ENDIAN = "pcm_u24le"
    PCM_UNSIGNED_32_BITS_BIG_ENDIAN    = "pcm_u32be"
    PCM_UNSIGNED_32_BITS_LITTLE_ENDIAN = "pcm_u32le"
    PCM_UNSIGNED_8_BITS                = "pcm_u8"
    PCM_SIGNED_8_BITS                  = "pcm_s8"

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

    # Raw pcm formats `ffmpeg -formats | grep PCM`
    PCM_FLOAT_32_BITS_BIG_ENDIAN       = "f32be"
    PCM_FLOAT_32_BITS_LITTLE_ENDIAN    = "f32le"
    PCM_FLOAT_64_BITS_BIG_ENDIAN       = "f64be"
    PCM_FLOAT_64_BITS_LITTLE_ENDIAN    = "f64le"
    PCM_SIGNED_16_BITS_BIG_ENDIAN      = "s16be"
    PCM_SIGNED_16_BITS_LITTLE_ENDIAN   = "s16le"
    PCM_SIGNED_24_BITS_BIG_ENDIAN      = "s24be"
    PCM_SIGNED_24_BITS_LITTLE_ENDIAN   = "s24le"
    PCM_SIGNED_32_BITS_BIG_ENDIAN      = "s32be"
    PCM_SIGNED_32_BITS_LITTLE_ENDIAN   = "s32le"
    PCM_UNSIGNED_16_BITS_BIG_ENDIAN    = "u16be"
    PCM_UNSIGNED_16_BITS_LITTLE_ENDIAN = "u16le"
    PCM_UNSIGNED_24_BITS_BIG_ENDIAN    = "u24be"
    PCM_UNSIGNED_24_BITS_LITTLE_ENDIAN = "u24le"
    PCM_UNSIGNED_32_BITS_BIG_ENDIAN    = "u32be"
    PCM_UNSIGNED_32_BITS_LITTLE_ENDIAN = "u32le"
    PCM_UNSIGNED_8_BITS                = "u8"
    PCM_SIGNED_8_BITS                  = "s8"

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

class FFmpegScaleFilter(BrokenEnum):
    Lanczos  = "lanczos"
    Bicubic  = "bicubic"
    Bilinear = "fast_bilinear"
    Point    = "point"
    Spline   = "spline"

class FFmpegFilterFactory:
    def scale(
        width: Union[Tuple[int, int], int],
        height: int=None,
        filter: FFmpegScaleFilter=FFmpegScaleFilter.Lanczos
    ) -> str:
        width, height = BrokenUtils.flatten(width, height)
        filter = FFmpegScaleFilter.get(filter).value
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
    Auto  = "auto"
    CUVID = "cuvid"
    DXVA2 = "dxva2"
    QSV   = "qsv"
    VDPAU = "vdpau"
    VAAPI = "vaapi"

# -------------------------------------------------------------------------------------------------|

@define
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
        .pixel_format(FFmpegPixelFormat.YUV444P)
        .preset(FFmpegH264Preset.Slow)
        .quality(FFmpegH264Quality.Ultra)
        .filter(FFmpegFilterFactory.scale(1280, 720))
        .output("output.mp4")
    ).run()
    """

    options:     DotMap    = Factory(DotMap)
    filters:     List[str] = Factory(list)
    __command__: List[str] = Factory(list)
    binary:      Path      = None

    def __private_to_option__(self, string: str) -> str:
        """Option commands are the string between the first two dunder"""
        if "__" not in string:
            return string
        return string.split("__")[1]

    def __call__(self, *args, **kwargs) -> Self:
        return self

    def __attrs_post_init__(self):
        self.set_ffmpeg_binary()

        # Add default available options
        self.__add_option__(
            self.custom,
            self.input,
            self.resolution,
            self.hwaccel,
            self.pixel_format,
            self.output,
            self.loglevel,
            self.hide_banner,
            self.quiet,
            self.framerate,
            self.overwrite,
            self.shortest,
            self.stats,
            self.filter,
            self.format,
            self.vsync,
            self.no_audio,
            self.advanced,
            self.audio_codec,
        )

    def set_ffmpeg_binary(self, binary: Path=None) -> Self:
        """Set the ffmpeg binary to use, by default it is 'ffmpeg'"""
        if binary:
            log.debug(f"Using custom FFmpeg binary at ({binary})")
        elif (binary := shutil.which("ffmpeg")):
            log.debug(f"Using system FFmpeg binary at ({binary})")
        if not binary:
            import imageio_ffmpeg
            binary = Path(imageio_ffmpeg.get_ffmpeg_exe())
            log.debug(f"Using ImageIO FFmpeg binary at ({binary})")
        if not binary:
            log.error(f"Could not find (FFmpeg) binary on PATH and don't have (ImageIO FFmpeg) package, please install it")
            exit(1)

        self.binary = binary
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
        self.__command__ = BrokenUtils.flatten(self.__command__, items)
        self.__del_option__(delete)
        self.__add_option__(add)
        return self

    # # Deal with next option - to call it or list available options

    def log_options(self, _error: str=None):
        """Log available next commands"""
        _log = log.error if _error else log.info

        if _error:
            _log(f"Fluent BrokenFFmpeg has no attribute ({_error}) at this point. Available attributes are:")
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

    def custom(self, *command: list[str]) -> Self:
        """Add an custom command on the pipeline"""
        self.__command__ += command
        return self

    # ---------------------------------------------------------------------------------------------|
    # Formats

    def pixel_format(self, option: FFmpegPixelFormat) -> Self:
        return self.__smart__("-pix_fmt", FFmpegPixelFormat.get(option), delete=self.pixel_format)

    def format(self, option: FFmpegFormat) -> Self:
        return self.__smart__("-f", FFmpegFormat.get(option), delete=self.format)

    # ---------------------------------------------------------------------------------------------|
    # Loglevel, stats

    def loglevel(self, option: FFmpegLogLevel=FFmpegLogLevel.Error) -> Self:
        return self.__smart__("-loglevel", FFmpegLogLevel.get(option), delete=self.loglevel)

    def quiet(self) -> Self:
        """Shorthand for loglevel error and hide banner"""
        self.loglevel(FFmpegLogLevel.Error)
        self.hide_banner()
        return self

    def stats(self) -> Self:
        """Shorthand for only showing important stats"""
        self.loglevel(FFmpegLogLevel.Error)
        self.hide_banner()
        return self.__smart__("-stats", delete=self.stats)

    def hide_banner(self) -> Self:
        return self.__smart__("-hide_banner", delete=self.hide_banner)

    # ---------------------------------------------------------------------------------------------|
    # Bitrate

    def audio_bitrate(self, option: int) -> Self:
        return self.__smart__("-b:a", str(option), delete=self.audio_bitrate)

    def video_bitrate(self, option: int) -> Self:
        return self.__smart__("-b:v", str(option), delete=self.video_bitrate)

    # ---------------------------------------------------------------------------------------------|
    # Special

    def hwaccel(self, option: FFmpegHWAccel=FFmpegHWAccel.Auto) -> Self:
        return self.__smart__("-hwaccel", FFmpegHWAccel.get(option), delete=self.hwaccel)

    def overwrite(self) -> Self:
        return self.__smart__("-y", delete=self.overwrite)

    def shortest(self) -> Self:
        return self.__smart__("-shortest", delete=self.shortest)

    def no_audio(self) -> Self:
        return self.__smart__("-an", delete=self.no_audio)

    def map(self, input_stream: int, stream: Option["v", "a"], output_stream: int) -> Self:
        """
        Map input stream to output stream, for example `-map 0:v:0 -map 1:a:0 maps` does:
        - Input (v)ideo stream 0, to output (v)ideo stream 0
        - Input (a)udio stream 1, to output (a)udio stream 0
        """
        self.__command__ += ["-map", f"{input_stream}:{stream}:{output_stream}"]
        return self

    def advanced(self, *command: list[str]) -> Self:
        """Add an custom advanced command on the pipeline"""
        self.__command__ += command
        return self

    def empty_audio_track(self, samplerate: Hertz) -> Self:
        return self.__smart__(
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate={samplerate}",
        )

    # ---------------------------------------------------------------------------------------------|
    # Input, output

    def input(self, path: str) -> Self:
        """Input some audio file, video file, or pipe '-' from stdin"""

        # Allow pipe from stdin
        if path == "-":
            pass

        elif not (path := BrokenPath(path)).exists():
            log.error(f"Input file ({path}) does not exist")
            return self

        # Add command
        self.__smart__("-i", path, add=(
            self.resolution,
            self.video_codec,
            self.framerate,
            self.audio_bitrate,
            self.video_bitrate,
            self.map,
            self.pixel_format,
            self.no_video
        ))
        return self

    def output(self, path: str) -> Self:
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
        return self.__smart__(path, delete=self.overwrite)

    # ---------------------------------------------------------------------------------------------|
    # Sizes, framerates, filter

    def filter(self, *filters: str) -> Self:
        """Send filters strings from FFmpegFilterFactory or manually (advanced)"""
        self.filters.extend(filters)
        return self

    def resolution(self, width: FFmpegResolution | int, height: int=None) -> Self:
        if isinstance(width, (list, tuple)):
            width, height = width
        if not isinstance(width, FFmpegResolution):
            width = FFmpegResolution(width, height)
        return self.__smart__("-s", str(width), delete=self.resolution)

    def framerate(self, option: int) -> Self:
        return self.__smart__("-framerate", option, delete=self.framerate)

    def vsync(self, option: FFmpegVsync=FFmpegVsync.ConstantFramerate) -> Self:
        return self.__smart__("-vsync", option, delete=self.vsync)

    def no_video(self) -> Self:
        """More like NVIDIA"""
        return self.__smart__("-vn", delete=self.no_video)

    # ---------------------------------------------------------------------------------------------|
    # Base codecs

    def video_codec(self, codec: FFmpegVideoCodec=FFmpegVideoCodec.H264) -> Self:
        codec = FFmpegVideoCodec.get(codec)

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
            self.video_codec,
            self.hwaccel,
        ))

    def audio_codec(self, codec: FFmpegAudioCodec=FFmpegAudioCodec.AAC) -> Self:
        return self.__smart__("-c:a", FFmpegAudioCodec.get(codec), delete=self.audio_codec)

    # ---------------------------------------------------------------------------------------------|
    # Generic NVENC

    def __gpu__nvenc(self, option: int=0) -> Self:
        return self.__smart__("-gpu", option, delete=self.__gpu__nvenc)

    def __rate_control_lookahead__nvenc(self, option: int=0) -> Self:
        return self.__smart__("-rc-lookahead", option, delete=self.__rate_control_lookahead__nvenc)

    def __surfaces__nvenc(self, option: Union[int, Range(0, 65)]=0) -> Self:
        return self.__smart__("-surfaces", min(max(option, 0), 64), delete=self.__surfaces__nvenc)

    def __qp__nvenc(self, option: Union[int, Range(-1, 51)]=-1) -> Self:
        return self.__smart__("-qp", option, delete=self.__qp__nvenc)

    def __bref_mode__nvenc(self, option: FFmpegNVENC_B_Ref_Mode=FFmpegNVENC_B_Ref_Mode.Disabled) -> Self:
        log.warning("B Frames requires Turing or newer architecture (RTX 2000+)")
        return self.__smart__("-b_ref_mode", FFmpegNVENC_B_Ref_Mode.get(option), delete=self.__bref_mode__nvenc)

    def __preset__nvenc(self, option: FFmpegNVENC_Preset=FFmpegNVENC_Preset.Slower) -> Self:
        return self.__smart__("-preset", FFmpegNVENC_Preset.get(option), delete=self.__preset__nvenc)

    def __tune__nvenc(self, option: FFmpegNVENC_Tune=FFmpegNVENC_Tune.HighQuality) -> Self:
        return self.__smart__("-tune", FFmpegNVENC_Tune.get(option), delete=self.__tune__nvenc)

    def __level__nvenc(self, option: FFmpegNVENC_Level=FFmpegNVENC_Level.Auto) -> Self:
        return self.__smart__("-level", FFmpegNVENC_Level.get(option), delete=self.__level__nvenc)

    def __rc__nvenc(self, option: FFmpegNVENC_RC=FFmpegNVENC_RC.VariableBitrateHighQuality) -> Self:
        return self.__smart__("-rc", FFmpegNVENC_RC.get(option), delete=self.__rc__nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H264 NVENC

    def __profile__h264_nvenc(self, option: FFmpegH264_NVENC_Profile=FFmpegH264_NVENC_Profile.Main) -> Self:
        return self.__smart__("-profile", FFmpegH264_NVENC_Profile.get(option), delete=self.__profile__h264_nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H265 NVENC

    def __profile__h265_nvenc(self, option: FFmpegH265_NVENC_Profile=FFmpegH265_NVENC_Profile.Main) -> Self:
        return self.__smart__("-profile", FFmpegH265_NVENC_Profile.get(option), delete=self.__profile__h265_nvenc)

    def __tier__h265_nvenc(self, option: FFmpegH265_NVENC__Tier=FFmpegH265_NVENC__Tier.Main) -> Self:
        return self.__smart__("-tier", FFmpegH265_NVENC__Tier.get(option), delete=self.__tier__h265_nvenc)

    # ---------------------------------------------------------------------------------------------|
    # H264

    def __preset__h264(self, option: FFmpegH264Preset=FFmpegH264Preset.Slow) -> Self:
        return self.__smart__("-preset", FFmpegH264Preset.get(option), delete=self.__preset__h264)

    def __tune__h264(self, option: FFmpegH264Tune=FFmpegH264Tune.Film) -> Self:
        return self.__smart__("-tune", FFmpegH264Tune.get(option), delete=self.__tune__h264)

    def __profile__h264(self, option: FFmpegH264Profile=FFmpegH264Profile.Main) -> Self:
        return self.__smart__("-profile:v", FFmpegH264Profile.get(option), delete=self.__profile__h264)

    def __quality__h264(self, option: FFmpegH264Quality=FFmpegH264Quality.High) -> Self:
        return self.__smart__("-crf", FFmpegH264Quality.get(option), delete=self.__quality__h264)

    # ---------------------------------------------------------------------------------------------|
    # H265

    def __preset__h265(self, option: FFmpegH265Preset=FFmpegH265Preset.Slow) -> Self:
        return self.__smart__("-preset", FFmpegH265Preset.get(option), delete=self.__preset__h265)

    def __tune__h265(self, option: FFmpegH265Tune) -> Self:
        return self.__smart__("-tune", FFmpegH265Tune.get(option), delete=self.__tune__h265)

    def __profile__h265(self, option: FFmpegH265Profile=FFmpegH265Profile.Main) -> Self:
        return self.__smart__("-profile:v", FFmpegH265Profile.get(option), delete=self.__profile__h265)

    def __quality__h265(self, option: FFmpegH264Quality.High) -> Self:
        return self.__smart__("-crf", FFmpegH264Quality.get(option), delete=self.__quality__h265)

    # ---------------------------------------------------------------------------------------------|
    # End user manual actions

    @property
    def command(self) -> List[str]:
        return list(map(BrokenUtils.denum, BrokenUtils.flatten(self.binary, self.__command__)))

    def run(self, **kwargs) -> subprocess.CompletedProcess:
        return shell(self.command, **kwargs)

    def popen(self, **kwargs) -> subprocess.Popen:
        return shell(self.command, Popen=True, **kwargs)

    def pipe(self, *args, **kwargs) -> BrokenFFmpegPopenBuffered:
        """Spawns a Popen process of BrokenFFmpeg that is buffered, use .write(data: bytes) and .close()"""

        @define
        class BrokenFFmpegPopenBuffered:
            ffmpeg: subprocess.Popen
            buffer: int          = 50
            frames: Deque[bytes] = Factory(deque)
            thread: Thread       = None

            # ZeroMQ
            zmq_enable:    bool  = (os.environ.get('ZMQ', '1') == '1')
            zmq_context:   Any   = None
            zmq_socket:    Any   = None
            zmq_tcp:       str   = None
            zmq_socket_id: bytes = None

            @property
            def zmq(self) -> bool:
                return (self.zmq_socket is not None)

            def __attrs_post_init__(self):
                command = self.ffmpeg.command

                # Configure FFmpeg command to read from a ZeroMQ socket
                try:
                    if BrokenPlatform.OnLinux and self.zmq_enable:
                        globals()['zmq'] = __import__('zmq')
                    log.success("ZeroMQ is Enabled. Behold Fastest Pipes in the West 🌵")
                    self.zmq_context = zmq.Context()
                    self.zmq_socket = self.zmq_context.socket(zmq.STREAM)
                    self.zmq_tcp = f"tcp://127.0.0.1:{BrokenUtils.get_free_tcp_port()}"
                    self.zmq_socket.connect(self.zmq_tcp)
                    self.zmq_socket.setsockopt(zmq.SNDHWM, self.buffer)
                    self.zmq_socket_id = self.zmq_socket.getsockopt(zmq.IDENTITY)
                    command = list(map(lambda item: f"{self.zmq_tcp}?listen=1" if (item == "-") else item, command))
                except ImportError:
                    log.minor("ZeroMQ is not supported or installed, fallback to normal pipe")

                # Start FFmpeg subprocess
                self.ffmpeg = shell(command, Popen=True, stdin=PIPE)
                self.thread = BrokenThread.new(self.__worker__)

            def write(self, frame: bytes):
                """Write a frame to the pipe, if the buffer is full, wait for it to be empty"""
                self.frames.append(frame)
                while len(self.frames) >= self.buffer:
                    time.sleep(0.001)

            __stop__: bool = False

            def close(self):
                """Wait for all frames to be written and close the pipe"""
                self.__stop__ = True
                with Halo() as spinner:
                    while self.frames:
                        spinner.text = f"BrokenFFmpeg: Waiting for ({len(self.frames):4}) frames to be written to FFmpeg"
                        time.sleep(0.016)
                    spinner.text = f"BrokenFFmpeg: Waiting FFmpeg process to Finish"
                    while self.ffmpeg.poll() is None:
                        time.sleep(0.016)

            def __worker__(self):
                while self.frames or (not self.__stop__):
                    try:
                        frame = self.frames.popleft()
                        if not self.zmq:
                            self.ffmpeg.stdin.write(frame)
                        else:
                            self.zmq_socket.send(self.zmq_socket_id, zmq.SNDMORE)
                            self.zmq_socket.send(frame)
                    except IndexError:
                        time.sleep(0.01)

                (self.zmq_socket or self.ffmpeg.stdin).close()

        return BrokenFFmpegPopenBuffered(ffmpeg=self, *args, **kwargs)

    # ---------------------------------------------------------------------------------------------|
    # High level functions

    @staticmethod
    @functools.lru_cache
    def get_resolution(path: Path, *, echo: bool=True) -> Optional[Tuple[int, int]]:
        """Get the resolution of a video in a smart way"""
        path = BrokenPath(path)
        log.minor(f"Getting video resolution of ({path})")
        return PIL.Image.open(io.BytesIO(
            shell((
                BrokenFFmpeg()
                .quiet()
                .input(path)
                .advanced("-vframes", "1")
                .format(FFmpegFormat.Image2pipe)
                .output("-")
            ).command,
            stdout=PIPE,
            stderr=PIPE,
            echo=echo,
        ).stdout), formats=["jpeg"]).size

    @staticmethod
    @functools.lru_cache
    def get_frames(path: PathLike, *, echo: bool=True) -> Iterable[numpy.ndarray]:
        """Generator for every frame of the video as numpy arrays, FAST!"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Yielding video frames of ({path})")

        import numpy

        # Get resolution of the video (so we now how many bytes to read a frame)
        (width, height) = BrokenFFmpeg.get_resolution(path)

        # Popen the frames reading FFmpeg
        ffmpeg = shell((
                BrokenFFmpeg()
                .hwaccel(FFmpegHWAccel.Auto)
                .vsync(FFmpegVsync.ConstantFramerate)
                .loglevel(FFmpegLogLevel.Panic)
                .input(path)
                .video_codec(FFmpegVideoCodec.Rawvideo)
                .format(FFmpegFormat.Rawvideo)
                .pixel_format(FFmpegPixelFormat.RGB24)
                .no_audio()
                .output("-")
            ).command,
            Popen=True,
            stdout=PIPE,
            echo=echo,
        )

        # Keep reading frames until we run out (should be equal to video_total_frames)
        while (raw := ffmpeg.stdout.read(width * height * 3)):
            yield numpy.frombuffer(raw, dtype=numpy.uint8).reshape((height, width, 3))

    @staticmethod
    @functools.lru_cache
    def get_total_frames(path: PathLike, *, echo: bool=True) -> Optional[int]:
        """Count the total frames of a video"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Getting video total frames of ({path})")

        # Read all frames from the video but don't process them
        info = shell((
                BrokenFFmpeg()
                .vsync(FFmpegVsync.ConstantFramerate)
                .input(path)
                .format(FFmpegFormat.Null)
                .output("-")
            ).command,
            stderr=PIPE,
            echo=echo,
        ).stderr.decode()

        # Search for the last frame=(number)
        return int(re.compile(r"frame=\s*(\d+)").findall(info)[-1])

    @staticmethod
    @functools.lru_cache
    def get_video_duration(path: PathLike, *, echo: bool=True) -> Optional[Seconds]:
        """Get the duration of a video"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Getting Video Duration of file ({path})")
        return float(shell("ffprobe",
            "-i", path,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ))

    @staticmethod
    @functools.lru_cache
    def get_framerate(path: PathLike, *, echo: bool=True) -> Optional[Hertz]:
        """Get the framerate of a video"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Getting Video Framerate of file ({path})", echo=echo)
        return BrokenFFmpeg.get_total_frames(path, echo=False)/BrokenFFmpeg.get_video_duration(path, echo=False)

    @staticmethod
    @functools.lru_cache
    def get_samplerate(path: PathLike, *, stream: int=0, echo: bool=True) -> Optional[Hertz]:
        """Get the samplerate of a audio file"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Getting Audio Samplerate of file ({path})", echo=echo)
        return int(shell("ffprobe",
            "-i", path,
            "-show_entries", "stream=sample_rate",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ).strip().splitlines()[stream])

    @staticmethod
    @functools.lru_cache
    def get_audio_channels(path: PathLike, *, stream: int=0, echo: bool=True) -> Optional[int]:
        """Get the number of channels of a audio file"""
        if not (path := BrokenPath(path, valid=True)):
            return
        log.minor(f"Getting Audio Channels of file ({path})", echo=echo)
        return int(shell("ffprobe",
            "-i", path,
            "-show_entries", "stream=channels",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ).strip().splitlines()[stream])

    @staticmethod
    def get_raw_audio(
        path: PathLike,
        *,
        format: FFmpegPCM=FFmpegPCM.PCM_FLOAT_32_BITS_LITTLE_ENDIAN,
        chunk: Seconds=0.1,
        echo: bool=True
    ) -> Optional[Generator[numpy.ndarray, None, Seconds]]:

        if not (path := BrokenPath(path, valid=True)):
            return

        import numpy

        # Get basic information
        channels:   int = BrokenFFmpeg.get_audio_channels(path, echo=echo)
        samplerate: int = BrokenFFmpeg.get_samplerate(path, echo=echo)

        # An example format of "f32le" will have:
        # • Size, Endian, Type, dtype = 4, "<", "f", "<f4"
        format: str = FFmpegPCM.get(format).value
        size:   int = int(re.sub(r"\D", "", format)) // 8
        endian: str = re.sub(r".*\d", "", format).replace("le", "<").replace("be", ">")
        type:   str = re.match(r"[^\d]+", format).group(0)
        dtype:  str = f"{endian}{type}{size}"

        # Note: Stderr to null as we might not read all the audio
        ffmpeg = (
            BrokenFFmpeg()
            .quiet()
            .input(path)
            .audio_codec(f"pcm_{format}")
            .format(format)
            .no_video()
            .custom("-ar", samplerate)
            .custom("-ac", channels)
            .output("-")
        ).popen(stdout=PIPE, stderr=DEVNULL)

        """
        One would think the following code is the way, but it is not

        ```python
        while (data := ffmpeg.stdout.read(chunk*samplerate)):
            yield (...)
        ```

        Reason being:
        • Small reads yields time imprecision on sample domain vs time domain
        • Must keep track of theoretical time and real time of the read
        """

        # Keep track of theoretical and read time
        bytes_per_second: int = (size * channels * samplerate)
        bytes_per_sample: int = (size * channels)
        stream_time:    float = 0

        for target_time in itertools.count(chunk, chunk):

            # Calculate the length of the next read to best match the target time
            length = (target_time - stream_time) * bytes_per_second
            length = BrokenUtils.round(length, bytes_per_sample, type=int)

            # The next chunk might overshoot or undershoot, and it's ok
            if not (data := ffmpeg.stdout.read(length)):
                break

            # Increment precise time and read time
            stream_time += len(data)/bytes_per_second
            yield numpy.frombuffer(data, dtype=dtype).reshape(-1, channels)

        return stream_time

    @staticmethod
    def get_audio_duration(path: PathLike, *, echo: bool=True) -> Optional[Seconds]:
        if not (path := BrokenPath(path, valid=True)):
            return
        try:
            generator = BrokenFFmpeg.get_raw_audio(path, chunk=10, echo=echo)
            while next(generator) is not None: ...
        except StopIteration as result:
            return result.value
