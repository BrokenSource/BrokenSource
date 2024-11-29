from __future__ import annotations

import functools
import io
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen
from typing import (
    Annotated,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Self,
    Tuple,
    TypeAlias,
    Union,
)

import numpy
import typer
from attrs import define
from halo import Halo
from pydantic import ConfigDict, Field, field_validator
from typer import Option

from Broken import (
    BrokenBaseModel,
    BrokenEnum,
    BrokenFluent,
    BrokenPath,
    BrokenPlatform,
    BrokenTyper,
    denum,
    every,
    flatten,
    log,
    nearest,
    shell,
)
from Broken.Types import Bytes, Hertz, Seconds

# ------------------------------------------------------------------------------------------------ #

class FFmpegModuleBase(BrokenBaseModel, ABC):
    model_config = ConfigDict(
        use_attribute_docstrings=True,
        validate_assignment=True,
    )

    @abstractmethod
    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        ...

# ------------------------------------------------------------------------------------------------ #

# Fixme: Remove workaround https://github.com/fastapi/typer/pull/429#issuecomment-2491043848
# everywhere until PR https://github.com/fastapi/typer/pull/429 is merged

class FFmpegInputPath(FFmpegModuleBase):
    type: Annotated[Literal["path"], BrokenTyper.exclude()] = "path"
    path: Path

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        return ("-i", self.path)


class FFmpegInputPipe(FFmpegModuleBase):
    type: Annotated[Literal["pipe"], BrokenTyper.exclude()] = "pipe"

    class Format(str, BrokenEnum):
        Rawvideo   = "rawvideo"
        Image2Pipe = "image2pipe"
        Null       = "null"

    format: Annotated[Optional[Format],
        Option("--format", "-f")] = \
        Field(Format.Rawvideo)

    class PixelFormat(str, BrokenEnum):
        YUV420P = "yuv420p"
        YUV444P = "yuv444p"
        RGB24   = "rgb24"
        RGBA    = "rgba"

    pixel_format: Annotated[PixelFormat,
        Option("--pixel-format", "-p")] = \
        Field(PixelFormat.RGB24)

    width: int = Field(1920, gt=0)
    height: int = Field(1080, gt=0)
    framerate: float = Field(60.0, ge=1.0)

    @field_validator("framerate", mode="plain")
    def validate_framerate(cls, value: Union[float, str]) -> float:
        return eval(str(value))

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-f", denum(self.format))
        yield ("-s", f"{self.width}x{self.height}")
        yield ("-pix_fmt", denum(self.pixel_format))
        yield ("-r", self.framerate)
        yield ("-i", "-")


FFmpegInputType: TypeAlias = Union[
    FFmpegInputPath,
    FFmpegInputPipe,
]

# ------------------------------------------------------------------------------------------------ #

class FFmpegOutputPath(FFmpegModuleBase):
    type: Annotated[Literal["path"], BrokenTyper.exclude()] = "path"

    overwrite: Annotated[bool,
        Option("--overwrite", "-y", " /--no-overwrite", " /-n")] = \
        Field(True)

    path: Annotated[Path,
        typer.Argument(help="The output file path")] = \
        Field(...)

    class PixelFormat(str, BrokenEnum):
        YUV420P = "yuv420p"
        YUV444P = "yuv444p"

    pixel_format: Annotated[Optional[PixelFormat],
        Option("--pixel-format", "-p")] = \
        Field(PixelFormat.YUV420P)

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-pix_fmt", denum(self.pixel_format))
        yield (self.path, self.overwrite*"-y")


class FFmpegOutputPipe(FFmpegModuleBase):
    type: Annotated[Literal["pipe"], BrokenTyper.exclude()] = "pipe"

    class Format(str, BrokenEnum):
        Rawvideo   = "rawvideo"
        Image2Pipe = "image2pipe"
        Null       = "null"

    format: Annotated[Optional[Format],
        Option("--format", "-f")] = \
        Field(None)

    class PixelFormat(str, BrokenEnum):
        RGB24 = "rgb24"
        RGBA  = "rgba"

    pixel_format: Annotated[Optional[PixelFormat],
        Option("--pixel-format", "-p")] = \
        Field(PixelFormat.RGB24)

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-f", denum(self.format))
        yield every("-pix_fmt", denum(self.pixel_format))
        yield "-"


FFmpegOutputType = Union[
    FFmpegOutputPipe,
    FFmpegOutputPath,
]

# ------------------------------------------------------------------------------------------------ #

# Note: See full help with `ffmpeg -h encoder=h264`
class FFmpegVideoCodecH264(FFmpegModuleBase):
    """Use [bold orange3][link=https://www.videolan.org/developers/x264.html]VideoLAN's[/link][/] [blue][link=https://trac.ffmpeg.org/wiki/Encode/H.264]libx264[/link][/]"""
    type: Annotated[Literal["h264"], BrokenTyper.exclude()] = "h264"

    class Preset(str, BrokenEnum):
        None_     = None
        UltraFast = "ultrafast"
        SuperFast = "superfast"
        VeryFast  = "veryfast"
        Faster    = "faster"
        Fast      = "fast"
        Medium    = "medium"
        Slow      = "slow"
        Slower    = "slower"
        VerySlow  = "veryslow"

    preset: Annotated[Optional[Preset],
        Option("--preset", "-p")] = \
        Field(Preset.Slow)
    """How much time to spend on encoding. Slower options gives better compression
    [blue link=https://trac.ffmpeg.org/wiki/Encode/H.264#Preset]→ Documentation[/]"""

    class Tune(str, BrokenEnum):
        None_       = None
        Film        = "film"
        Animation   = "animation"
        Grain       = "grain"
        StillImage  = "stillimage"
        FastDecode  = "fastdecode"
        ZeroLatency = "zerolatency"

    tune: Annotated[Optional[Tune],
        Option("--tune", "-t")] = \
        Field(None)
    """Tune x264 to keep and optimize for certain aspects of the input media
    [blue link=https://trac.ffmpeg.org/wiki/Encode/H.264#Tune]→ Documentation[/]"""

    class Profile(str, BrokenEnum):
        None_    = None
        Baseline = "baseline"
        Main     = "main"
        High     = "high"
        High10   = "high10"
        High422  = "high422"
        High444p = "high444p"

    profile: Annotated[Optional[Profile],
        Option("--profile", "-p")] = \
        Field(None)
    """How many features the encoder can use, the playback device must support them
    [blue link=https://trac.ffmpeg.org/wiki/Encode/H.264#Profile]→ Documentation[/]"""

    faststart: Annotated[bool,
        Option("--faststart", " /--no-faststart", hidden=True)] = \
        Field(True)
    """Move the index (moov atom) to the beginning of the file for faster initial playback"""

    rgb: Annotated[bool,
        Option("--rgb", " /--yuv")] = \
        Field(False)
    """Use RGB colorspace instead of YUV"""

    crf: int = Field(20, ge=0, le=51)
    """Constant Rate Factor. 0 is lossless, 51 is the worst quality
    [blue link=https://trac.ffmpeg.org/wiki/Encode/H.264#a1.ChooseaCRFvalue]→ Documentation[/]"""

    crf: Annotated[int,
        Option("--crf", "-c", min=0, max=51)] = \
        Field(20, ge=0, le=51)
    """Constant Rate Factor. 0 is lossless, 51 is the worst quality
    [blue link=https://trac.ffmpeg.org/wiki/Encode/H.264#a1.ChooseaCRFvalue]→ Documentation[/]"""

    bitrate: Annotated[Optional[int],
        Option("--bitrate", "-b", min=0)] = \
        Field(None, ge=0)
    """Bitrate in kilobits per second, the higher the better quality and file size"""

    x264params: Annotated[Optional[List[str]],
        Option("--x264-params", hidden=True)] = \
        Field(default_factory=list)
    """Additional options to pass to x264"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:v", "libx264rgb" if self.rgb else "libx264")
        yield every("-movflags", "+faststart"*self.faststart)
        yield every("-profile", denum(self.profile))
        yield every("-preset", denum(self.preset))
        yield every("-tune", denum(self.tune))
        yield every("-b:v", self.bitrate)
        yield every("-crf", self.crf)
        yield every("-x264opts", ":".join(self.x264params or []))


# Note: See full help with `ffmpeg -h encoder=h264_nvenc`
class FFmpegVideoCodecH264_NVENC(FFmpegModuleBase):
    """Use [bold green][link=https://en.wikipedia.org/wiki/Nvidia_NVENC]NVIDIA[/link][/] [blue][link=https://trac.ffmpeg.org/wiki/HWAccelIntro]NVENC H.264[/link][/]"""
    type: Annotated[Literal["h264-nvenc"], BrokenTyper.exclude()] = "h264-nvenc"

    class Preset(str, BrokenEnum):
        None_                     = None
        HighQuality2Passes        = "slow"
        HighQuality1Pass          = "medium"
        HighPerformance1Pass      = "fast"
        HighPerformance           = "hp"
        HighQuality               = "hq"
        Balanced                  = "bd"
        LowLatency                = "ll"
        LowLatencyHighQuality     = "llhq"
        LowLatencyHighPerformance = "llhp"
        Lossless                  = "lossless"
        LosslessHighPerformance   = "losslesshp"
        Fastest                   = "p1"
        Faster                    = "p2"
        Fast                      = "p3"
        Medium                    = "p4"
        Slow                      = "p5"
        Slower                    = "p6"
        Slowest                   = "p7"

    preset: Annotated[Optional[Preset],
        Option("--preset", "-p")] = \
        Field(Preset.Medium)
    """How much time to spend on encoding. Slower options gives better compression"""

    class Tune(str, BrokenEnum):
        None_           = None
        HighQuality     = "hq"
        LowLatency      = "ll"
        UltraLowLatency = "ull"
        Lossless        = "lossless"

    tune: Annotated[Optional[Tune],
        Option("--tune", "-t")] = \
        Field(Tune.HighQuality)
    """Tune the encoder for a specific tier of performance"""

    class Profile(str, BrokenEnum):
        None_    = None
        Baseline = "baseline"
        Main     = "main"
        High     = "high"
        High444p = "high444p"

    profile: Annotated[Optional[Profile],
        Option("--profile", "-p")] = \
        Field(Profile.High)
    """How many features the encoder can use, the playback device must support them"""

    class RateControl(str, BrokenEnum):
        None_ = None
        ConstantBitrateHighQuality = "cbr_hq"
        VariableBitrateHighQuality = "vbr_hq"
        ConstantQuality = "constqp"
        VariableBitrate = "vbr"
        ConstantBitrate = "cbr"

    rate_control: Annotated[Optional[RateControl],
        Option("--rc", "-r", hidden=True)] = \
        Field(RateControl.VariableBitrateHighQuality)
    """Rate control mode of the bitrate"""

    rc_lookahead: Annotated[Optional[int],
        Option("--rc-lookahead", "-l", hidden=True, min=0)] = \
        Field(32, ge=0)
    """Number of frames to look ahead for the rate control"""

    cbr: Annotated[bool,
        Option("--cbr", "-c", " /--no-cbr", " /-nc", hidden=True)] = \
        Field(False)
    """Enable Constant Bitrate mode"""

    gpu: Annotated[Optional[int],
        Option("--gpu", "-g", min=0)] = \
        Field(0, ge=0)
    """Use the Nth NVENC capable GPU for encoding, 0 for first available"""

    cq: Annotated[Optional[int],
        Option("--cq", "-q", min=0)] = \
        Field(25, ge=0)
    """(VBR) Similar to CRF, 0 is automatic, 1 is 'lossless', 51 is the worst quality"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:v", "h264_nvenc")
        yield every("-b:v", 0)
        yield every("-preset", denum(self.preset))
        yield every("-tune", denum(self.tune))
        yield every("-profile", denum(self.profile))
        yield every("-rc", denum(self.rate_control))
        yield every("-rc-lookahead", self.rc_lookahead)
        yield every("-cbr", int(self.cbr))
        yield every("-cq", self.cq)
        yield every("-gpu", self.gpu)


class FFmpegVideoCodecH264_QSV(FFmpegModuleBase):
    ... # Todo


class FFmpegVideoCodecH264_AMF(FFmpegModuleBase):
    ... # Todo


# Note: See full help with `ffmpeg -h encoder=libx265`
class FFmpegVideoCodecH265(FFmpegModuleBase):
    """Use [bold orange3][link=https://www.videolan.org/developers/x265.html]VideoLAN's[/link][/] [blue][link=https://trac.ffmpeg.org/wiki/Encode/H.265]libx265[/link][/]"""
    type: Annotated[Literal["h265"], BrokenTyper.exclude()] = "h265"

    crf: Annotated[int,
        Option("--crf", "-c", min=0, max=51)] = \
        Field(25, ge=0, le=51)
    """Constant Rate Factor. 0 is lossless, 51 is the worst quality"""

    bitrate: Annotated[Optional[int],
        Option("--bitrate", "-b", min=0)] = \
        Field(None, ge=1)
    """Bitrate in kilobits per second, the higher the better quality and file size"""

    class Preset(str, BrokenEnum):
        None_     = None
        UltraFast = "ultrafast"
        SuperFast = "superfast"
        VeryFast  = "veryfast"
        Faster    = "faster"
        Fast      = "fast"
        Medium    = "medium"
        Slow      = "slow"
        Slower    = "slower"
        VerySlow  = "veryslow"

    preset: Annotated[Optional[Preset],
        Option("--preset", "-p")] = \
        Field(Preset.Slow)
    """How much time to spend on encoding. Slower options gives better compression"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:v", "libx265")
        yield every("-preset", denum(self.preset))
        yield every("-crf", self.crf)
        yield every("-b:v", self.bitrate)


# Note: See full help with `ffmpeg -h encoder=hevc_nvenc`
class FFmpegVideoCodecH265_NVENC(FFmpegVideoCodecH265):
    """Use [bold green][link=https://en.wikipedia.org/wiki/Nvidia_NVENC]NVIDIA[/link][/] [blue][link=https://trac.ffmpeg.org/wiki/HWAccelIntro]NVENC H.265[/link][/]"""
    type: Annotated[Literal["h265-nvenc"], BrokenTyper.exclude()] = "h265-nvenc"

    class Preset(str, BrokenEnum):
        HighQuality2Passes        = "slow"
        HighQuality1Pass          = "medium"
        HighPerformance1Pass      = "fast"
        HighPerformance           = "hp"
        HighQuality               = "hq"
        Balanced                  = "bd"
        LowLatency                = "ll"
        LowLatencyHighQuality     = "llhq"
        LowLatencyHighPerformance = "llhp"
        Lossless                  = "lossless"
        LosslessHighPerformance   = "losslesshp"
        Fastest                   = "p1"
        Faster                    = "p2"
        Fast                      = "p3"
        Medium                    = "p4"
        Slow                      = "p5"
        Slower                    = "p6"
        Slowest                   = "p7"

    preset: Annotated[Preset,
        Option("--preset", "-p")] = \
        Field(Preset.Medium)
    """How much time to spend on encoding. Slower options gives better compression"""

    class Tune(str, BrokenEnum):
        None_           = None
        HighQuality     = "hq"
        LowLatency      = "ll"
        UltraLowLatency = "ull"
        Lossless        = "lossless"

    tune: Annotated[Optional[Tune],
        Option("--tune", "-t")] = \
        Field(Tune.HighQuality)

    class Profile(str, BrokenEnum):
        None_  = None
        Main   = "main"
        Main10 = "main10"
        ReXT   = "rext"

    profile: Annotated[Optional[Profile],
        Option("--profile", "-p")] = \
        Field(Profile.Main)

    class Tier(str, BrokenEnum):
        None_ = None
        Main  = "main"
        High  = "high"

    tier: Annotated[Optional[Tier],
        Option("--tier", "-t")] = \
        Field(Tier.High)

    class RateControl(str, BrokenEnum):
        None_           = None
        ConstantQuality = "constqp"
        VariableBitrate = "vbr"
        ConstantBitrate = "cbr"

    rate_control: Annotated[Optional[RateControl],
        Option("--rc", "-r", hidden=True)] = \
        Field(RateControl.VariableBitrate)

    rc_lookahead: Annotated[Optional[int],
        Option("--rc-lookahead", "-l", hidden=True)] = \
        Field(10, ge=1)
    """Number of frames to look ahead for the rate control"""

    cbr: Annotated[bool,
        Option("--cbr", "-c", " /--vbr", " /-v", hidden=True)] = \
        Field(False)
    """Use Constant Bitrate mode"""

    gpu: Annotated[int,
        Option("--gpu", "-g", min=0)] = \
        Field(0, ge=0)
    """Use the Nth NVENC capable GPU for encoding"""

    cq: Annotated[int,
        Option("--cq", "-q", min=0)] = \
        Field(25, ge=0)
    """(VBR) Similar to CRF, 0 is automatic, 1 is 'lossless', 51 is the worst quality"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:v", "hevc_nvenc")
        yield every("-preset", denum(self.preset))
        yield every("-tune", denum(self.tune))
        yield every("-profile", denum(self.profile))
        yield every("-tier", denum(self.tier))
        yield every("-rc", denum(self.rate_control))
        yield every("-rc-lookahead", self.rc_lookahead)
        yield every("-cbr", int(self.cbr))
        yield every("-cq", self.cq)
        yield every("-gpu", self.gpu)


class FFmpegVideoCodecH265_QSV(FFmpegModuleBase):
    ... # Todo


class FFmpegVideoCodecH265_AMF(FFmpegModuleBase):
    ... # Todo


# Note: See full help with `ffmpeg -h encoder=libvpx-vp9`
class FFmpegVideoCodecVP9(FFmpegModuleBase):
    """Use [blue][link=https://trac.ffmpeg.org/wiki/Encode/VP9]libvpx-vp9[/link][/] for VP9 encoding"""
    type: Annotated[Literal["vp9"], BrokenTyper.exclude()] = "vp9"

    crf: Annotated[int,
        Option("--crf", "-c", min=1, max=63)] = \
        Field(30, ge=1, le=64)
    """Constant Rate Factor (0-63). Lower values mean better quality, recommended (15-31)
    [blue link=https://trac.ffmpeg.org/wiki/Encode/VP9#constantq]→ Documentation[/]"""

    speed: Annotated[int,
        Option("--speed", "-s", min=1, max=6)] = \
        Field(4, ge=1, le=6)
    """Speed level (0-6). Higher values yields faster encoding but innacuracies in rate control
    [blue link=https://trac.ffmpeg.org/wiki/Encode/VP9#CPUUtilizationSpeed]→ Documentation[/]"""

    class Deadline(str, BrokenEnum):
        Good     = "good"
        Best     = "best"
        Realtime = "realtime"

    deadline: Annotated[Deadline,
        Option("--deadline", "-d")] = \
        Field(Deadline.Good)
    """Tweak the encoding time philosophy for better quality or faster encoding
    [blue link=https://trac.ffmpeg.org/wiki/Encode/VP9#DeadlineQuality]→ Documentation[/]"""

    row_multithreading: Annotated[bool,
        Option("--row-multithreading", "-rmt", " /--no-row-multithreading", " /-rmt")] = \
        Field(True)
    """Faster encodes by splitting rows into multiple threads
    [blue link=https://trac.ffmpeg.org/wiki/Encode/VP9#rowmt]→ Documentation[/]"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "libvpx-vp9")
        yield ("-crf", self.crf)
        yield ("-b:v", 0)
        yield ("-deadline", denum(self.deadline))
        yield ("-cpu-used", self.speed)
        yield ("-row-mt", "1") * self.row_multithreading


# Note: See full help with `ffmpeg -h encoder=libaom-av1`
class FFmpegVideoCodecAV1_LIBAOM(FFmpegModuleBase):
    """The reference encoder for AV1. Similar to VP9, not the fastest current implementation
    • https://trac.ffmpeg.org/wiki/Encode/AV1#libaom
    """
    type: Annotated[Literal["libaom-av1"], BrokenTyper.exclude()] = "libaom-av1"

    crf: Annotated[int,
        Option("--crf", "-c", min=1, max=63)] = \
        Field(23, ge=1, le=63)
    """Constant Rate Factor (0-63). Lower values mean better quality, AV1 CRF 23 == x264 CRF 19
    [blue link=https://trac.ffmpeg.org/wiki/Encode/AV1#ConstantQuality]→ Documentation[/]"""

    speed: Annotated[int,
        Option("--speed", "-s", min=1, max=6)] = \
        Field(3, ge=1, le=6)
    """Speed level (0-6). Higher values yields faster encoding but innacuracies in rate control
    [blue link=https://trac.ffmpeg.org/wiki/Encode/AV1#ControllingSpeedQuality]→ Documentation[/]"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "libaom-av1")
        yield ("-crf", self.crf)
        yield ("-cpu-used", self.speed)
        yield ("-row-mt", 1)
        yield ("-tiles", "2x2")


# Note: See full help with `ffmpeg -h encoder=libsvtav1`
class FFmpegVideoCodecAV1_SVT(FFmpegModuleBase):
    """Use [bold orange3][link=https://gitlab.com/AOMediaCodec/SVT-AV1]AOM's[/link][/] [blue][link=https://www.ffmpeg.org/ffmpeg-all.html#libsvtav1]SVT-AV1[/link][/]"""
    type: Annotated[Literal["libsvtav1"], BrokenTyper.exclude()] = "libsvtav1"

    crf: Annotated[int,
        Option("--crf", "-c", min=1, max=63)] = \
        Field(25, ge=1, le=63)
    """Constant Rate Factor (0-63). Lower values mean better quality
    [blue link=https://trac.ffmpeg.org/wiki/Encode/AV1#CRF]→ Documentation[/]"""

    preset: Annotated[int,
        Option("--preset", "-p", min=1, max=8)] = \
        Field(3, ge=1, le=8)
    """The speed of the encoding, 0 is slowest, 8 is fastest. Decreases compression efficiency.
    [blue link=https://trac.ffmpeg.org/wiki/Encode/AV1#Presetsandtunes]→ Documentation[/]"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "libsvtav1")
        yield ("-crf", self.crf)
        yield ("-preset", self.preset)
        yield ("-svtav1-params", "tune=0")


# Note: See full help with `ffmpeg -h encoder=librav1e`
class FFmpegVideoCodecAV1_RAV1E(FFmpegModuleBase):
    """Use [bold orange3][link=https://github.com/xiph/rav1e]Xiph's[/link][/] [blue][link=https://www.ffmpeg.org/ffmpeg-all.html#librav1e]RAV1E AV1[/link][/]"""
    type: Annotated[Literal["librav1e"], BrokenTyper.exclude()] = "librav1e"

    qp: Annotated[int,
        Option("--qp", "-q", min=-1)] = \
        Field(80, ge=-1)
    """Constant quantizer mode (from -1 to 255). Smaller values are higher quality"""

    speed: Annotated[int,
        Option("--speed", "-s", min=1, max=10)] = \
        Field(4, ge=1, le=10)
    """What speed preset to use (from -1 to 10) (default -1)"""

    tile_rows: Annotated[int,
        Option("--tile-rows", "-tr", min=-1)] = \
        Field(4, ge=-1)
    """Number of tile rows to encode with (from -1 to I64_MAX) (default 0)"""

    tile_columns: Annotated[int,
        Option("--tile-columns", "-tc", min=-1)] = \
        Field(4, ge=-1)
    """Number of tile columns to encode with (from -1 to I64_MAX) (default 0)"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "librav1e")
        yield ("-qp", self.qp)
        yield ("-speed", self.speed)
        yield ("-tile-rows", self.tile_rows)
        yield ("-tile-columns", self.tile_columns)


# Note: See full help with `ffmpeg -h encoder=av1_nvenc`
class FFmpegVideoCodecAV1_NVENC(FFmpegModuleBase):
    """Use [bold green][link=https://en.wikipedia.org/wiki/Nvidia_NVENC]NVIDIA[/link][/] [blue][link=https://trac.ffmpeg.org/wiki/Encode/AV1]NVENC AV1[/link][/] [dim light_coral](RTX 4000+ GPU)[/]"""
    type: Annotated[Literal["av1-nvenc"], BrokenTyper.exclude()] = "av1-nvenc"

    class Preset(str, BrokenEnum):
        Default              = "default"
        HighQuality2Passes   = "slow"
        HighQuality1Pass     = "medium"
        HighPerformance1Pass = "fast"
        Fastest              = "p1"
        Faster               = "p2"
        Fast                 = "p3"
        Medium               = "p4"
        Slow                 = "p5"
        Slower               = "p6"
        Slowest              = "p7"

    preset: Annotated[Preset,
        Option("--preset", "-p")] = \
        Field(Preset.Slow)
    """How much time to spend on encoding. Slower options gives better compression"""

    class Tune(str, BrokenEnum):
        HighQuality      = "hq"
        LowLatency       = "ll"
        UltraLowLatency  = "ull"
        Lossless         = "lossless"

    tune: Annotated[Optional[Tune],
        Option("--tune", "-t")] = \
        Field(Tune.HighQuality)
    """Tune the encoder for a specific tier of performance"""

    class RateControl(str, BrokenEnum):
        None_           = None
        ConstantQuality = "constqp"
        VariableBitrate = "vbr"
        ConstantBitrate = "cbr"

    rate_control: Annotated[Optional[RateControl],
        Option("--rc", "-r", hidden=True)] = \
        Field(RateControl.VariableBitrate)

    class Multipass(str, BrokenEnum):
        None_    = None
        Disabled = "disabled"
        Quarter  = "qres"
        Full     = "fullres"

    multipass: Annotated[Optional[Multipass],
        Option("--multipass", "-m", hidden=True)] = \
        Field(Multipass.Full)

    tile_rows: Annotated[Optional[int],
        Option("--tile-rows", "-tr", min=1, max=64)] = \
        Field(2, ge=1, le=64)
    """Number of encoding tile rows, similar to -row-mt"""

    tile_columns: Annotated[Optional[int],
        Option("--tile-columns", "-tc", min=1, max=64)] = \
        Field(2, ge=1, le=64)
    """Number of encoding tile columns, similar to -col-mt"""

    rc_lookahead: Annotated[Optional[int],
        Option("--rc-lookahead", "-l", hidden=True)] = \
        Field(10, ge=1)
    """Number of frames to look ahead for the rate control"""

    gpu: Annotated[int,
        Option("--gpu", "-g", min=0)] = \
        Field(0, ge=0)
    """Use the Nth NVENC capable GPU for encoding"""

    cq: int = Field(25, ge=1)
    """Set the Constant Quality factor in a Variable Bitrate mode (similar to -crf)"""

    cq: Annotated[Optional[int],
        Option("--cq", "-q", min=0)] = \
        Field(25, ge=0)
    """Set the Constant Quality factor in a Variable Bitrate mode (similar to -crf)"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:v", "av1_nvenc")
        yield every("-preset", denum(self.preset))
        yield every("-tune", denum(self.tune))
        yield every("-rc", denum(self.rate_control))
        yield every("-rc-lookahead", self.rc_lookahead)
        yield every("-cq", self.cq)
        yield every("-gpu", self.gpu)


class FFmpegVideoCodecAV1_QSV(FFmpegModuleBase):
    ... # Todo


class FFmpegVideoCodecAV1_AMF(FFmpegModuleBase):
    ... # Todo


class FFmpegVideoCodecRawvideo(FFmpegModuleBase):
    type: Annotated[Literal["rawvideo"], BrokenTyper.exclude()] = "rawvideo"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "rawvideo")


class FFmpegVideoCodecNoVideo(FFmpegModuleBase):
    type: Annotated[Literal["null"], BrokenTyper.exclude()] = "null"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "null")


class FFmpegVideoCodecCopy(FFmpegModuleBase):
    type: Annotated[Literal["copy"], BrokenTyper.exclude()] = "copy"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:v", "copy")


FFmpegVideoCodecType: TypeAlias = Union[
    FFmpegVideoCodecH264,
    FFmpegVideoCodecH264_NVENC,
    FFmpegVideoCodecH265,
    FFmpegVideoCodecH265_NVENC,
    FFmpegVideoCodecVP9,
    FFmpegVideoCodecAV1_LIBAOM,
    FFmpegVideoCodecAV1_SVT,
    FFmpegVideoCodecAV1_NVENC,
    FFmpegVideoCodecAV1_RAV1E,
    FFmpegVideoCodecRawvideo,
    FFmpegVideoCodecNoVideo,
    FFmpegVideoCodecCopy,
]

# ------------------------------------------------------------------------------------------------ #

class FFmpegAudioCodecAAC(FFmpegModuleBase):
    """Use the [blue][link=https://trac.ffmpeg.org/wiki/Encode/AAC]Advanced Audio Codec (AAC)[/link][/]"""
    type: Annotated[Literal["aac"], BrokenTyper.exclude()] = "aac"

    bitrate: Annotated[int,
        Option("--bitrate", "-b", min=1)] = \
        Field(192, ge=1)
    """Bitrate in kilobits per second. This value is shared between all audio channels"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:a", "aac")
        yield every("-b:a", f"{self.bitrate}k")


class FFmpegAudioCodecMP3(FFmpegModuleBase):
    """Use the [blue][link=https://trac.ffmpeg.org/wiki/Encode/MP3]MPEG Audio Layer 3 (MP3)[/link][/]"""
    type: Annotated[Literal["mp3"], BrokenTyper.exclude()] = "mp3"

    bitrate: Annotated[int,
        Option("--bitrate", "-b", min=1)] = \
        Field(192, ge=1)
    """Bitrate in kilobits per second. This value is shared between all audio channels"""

    qscale: Annotated[int,
        Option("--qscale", "-q", min=1)] = \
        Field(2, ge=1)
    """Quality scale, 0-9, Variable Bitrate"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:a", "libmp3lame")
        yield every("-b:a", f"{self.bitrate}k")
        yield every("-qscale:a", self.qscale)


class FFmpegAudioCodecOpus(FFmpegModuleBase):
    """Use the [blue][link=https://en.wikipedia.org/wiki/Opus_(audio_format)]Opus[/link][/] audio codec"""
    type: Annotated[Literal["opus"], BrokenTyper.exclude()] = "opus"

    bitrate: Annotated[int,
        Option("--bitrate", "-b", min=1)] = \
        Field(192, ge=1)
    """Bitrate in kilobits per second. This value is shared between all audio channels"""

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:a", "libopus")
        yield every("-b:a", f"{self.bitrate}k")


class FFmpegAudioCodecFLAC(FFmpegModuleBase):
    """Use the [blue][link=https://xiph.org/flac/]Free Lossless Audio Codec (FLAC)[/link][/]"""
    type: Annotated[Literal["flac"], BrokenTyper.exclude()] = "flac"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield every("-c:a", "flac")


class FFmpegAudioCodecCopy(FFmpegModuleBase):
    """Copy the inputs' audio streams"""
    type: Annotated[Literal["copy"], BrokenTyper.exclude()] = "copy"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:a", "copy")


class FFmpegAudioCodecNone(FFmpegModuleBase):
    """Remove all audio tracks from the output"""
    type: Annotated[Literal["none"], BrokenTyper.exclude()] = "none"

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-an")


class FFmpegAudioCodecEmpty(FFmpegModuleBase):
    """Adds a silent stereo audio track"""
    type: Annotated[Literal["empty"], BrokenTyper.exclude()] = "empty"

    samplerate: Annotated[float,
        Option("--samplerate", "-r", min=1)] = \
        Field(44100, ge=1)

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-f", "lavfi")
        yield ("-t", ffmpeg.time) * bool(ffmpeg.time)
        yield ("-i", f"anullsrc=channel_layout=stereo:sample_rate={self.samplerate}")


class FFmpegPCM(BrokenEnum):
    """Raw pcm formats `ffmpeg -formats | grep PCM`"""
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

    @property
    @functools.lru_cache
    def size(self) -> int:
        return int(''.join(filter(str.isdigit, self.value)))//8

    @property
    @functools.lru_cache
    def endian(self) -> str:
        return ("<" if ("le" in self.value) else ">")

    @property
    @functools.lru_cache
    def dtype(self) -> numpy.dtype:
        return numpy.dtype(f"{self.endian}{self.value[4]}{self.size}")


class FFmpegAudioCodecPCM(FFmpegModuleBase):
    """Raw pcm formats `ffmpeg -formats | grep PCM`"""
    type: Annotated[Literal["pcm"], BrokenTyper.exclude()] = "pcm"

    format: Annotated[FFmpegPCM,
        Option("--format", "-f")] = \
        Field(FFmpegPCM.PCM_FLOAT_32_BITS_LITTLE_ENDIAN)

    def command(self, ffmpeg: BrokenFFmpeg) -> Iterable[str]:
        yield ("-c:a", self.format.value, "-f", self.format.value.removeprefix("pcm_"))


FFmpegAudioCodecType: TypeAlias = Union[
    FFmpegAudioCodecAAC,
    FFmpegAudioCodecMP3,
    FFmpegAudioCodecOpus,
    FFmpegAudioCodecFLAC,
    FFmpegAudioCodecCopy,
    FFmpegAudioCodecNone,
    FFmpegAudioCodecEmpty,
    FFmpegAudioCodecPCM,
]

# ------------------------------------------------------------------------------------------------ #

class FFmpegFilterBase(BrokenBaseModel, ABC):

    @abstractmethod
    def string(self) -> Iterable[str]:
        ...

    def __str__(self) -> str:
        return self.string()

class FFmpegFilterScale(FFmpegFilterBase):
    type: Annotated[Literal["scale"], BrokenTyper.exclude()] = "scale"

    width: int = Field(gt=0)
    height: int = Field(gt=0)

    class Resample(str, BrokenEnum):
        Bilinear   = "bilinear"
        Nearest    = "nearest"
        Oversample = "oversample"
        Lanczos    = "lanczos"
        Spline     = "spline36"
        EwaLanczos = "ewa_lanczos"
        Gaussian   = "gaussian"
        Mitchell   = "mitchell"

    resample: Annotated[Resample,
        Option("--resample", "-r")] = \
        Field(Resample.Lanczos)

    def string(self) -> str:
        return f"scale={self.width}:{self.height}:flags={denum(self.resample)}"

class FFmpegFilterVerticalFlip(FFmpegFilterBase):
    type: Annotated[Literal["vflip"], BrokenTyper.exclude()] = "vflip"

    def string(self) -> str:
        return "vflip"

class FFmpegFilterCustom(FFmpegFilterBase):
    type: Annotated[Literal["custom"], BrokenTyper.exclude()] = "custom"

    content: str

    def string(self) -> str:
        return self.content

FFmpegFilterType: TypeAlias = Union[
    FFmpegFilterScale,
    FFmpegFilterVerticalFlip,
    FFmpegFilterCustom
]

# ------------------------------------------------------------------------------------------------ #

class BrokenFFmpeg(BrokenBaseModel, BrokenFluent):
    """💎 Your premium FFmpeg class, serializable, sane defaults, safety"""

    # ------------------------------------------|
    # Make all class available on BrokenFFmpeg.*

    class Input:
        Path = FFmpegInputPath
        Pipe = FFmpegInputPipe

    class Output:
        Path = FFmpegOutputPath
        Pipe = FFmpegOutputPipe

    class VideoCodec:
        H264       = FFmpegVideoCodecH264
        H264_NVENC = FFmpegVideoCodecH264_NVENC
        H265       = FFmpegVideoCodecH265
        H265_NVENC = FFmpegVideoCodecH265_NVENC
        VP9        = FFmpegVideoCodecVP9
        AV1_LIBAOM = FFmpegVideoCodecAV1_LIBAOM
        AV1_SVT    = FFmpegVideoCodecAV1_SVT
        AV1_NVENC  = FFmpegVideoCodecAV1_NVENC
        AV1_RAV1E  = FFmpegVideoCodecAV1_RAV1E
        Rawvideo   = FFmpegVideoCodecRawvideo
        NoVideo    = FFmpegVideoCodecNoVideo
        Copy       = FFmpegVideoCodecCopy

    class AudioCodec:
        AAC   = FFmpegAudioCodecAAC
        MP3   = FFmpegAudioCodecMP3
        Opus  = FFmpegAudioCodecOpus
        FLAC  = FFmpegAudioCodecFLAC
        Copy  = FFmpegAudioCodecCopy
        None_ = FFmpegAudioCodecNone
        Empty = FFmpegAudioCodecEmpty
        PCM   = FFmpegAudioCodecPCM

    class Filter:
        Scale        = FFmpegFilterScale
        VerticalFlip = FFmpegFilterVerticalFlip
        Custom       = FFmpegFilterCustom

    # ------------------------------------------|

    hide_banner: bool = True
    """Hides the compilation information of FFmpeg from the output"""

    shortest: bool = False
    """
    Ends the output at the shortest stream duration. For example, if the input is an 30s audio and
    a 20s video, and we're joining the two, the final video will be 20s. Or piping frames, 30s

    [**FFmpeg docs**](https://ffmpeg.org/ffmpeg.html#toc-Advanced-options)
    """

    stream_loop: int = Field(0)
    """Loops the input stream N times to the right. Zero '0' is no loop, one '1' doubles the length"""

    time: float = Field(0.0)
    """If greater than zero, stops encoding at the specified time. `-t` option of FFmpeg"""

    vsync: Literal["auto", "passthrough", "cfr", "vfr"] = Field("cfr")
    """
    The video's framerate mode, applied to all subsequent output targets. `-vsync` option of FFmpeg

    - `auto`: FFmpeg default, choses between constant and variable framerate based on muxer support
    - `cfr`: Constant Frame Rate, where frames are droped or duped to precisely match frametimes
    - `vfr`: Variable Frame Rate, static frames are kept, no two frames have the same timestemp
    - `passthrough`: The frames are passed through without modification on their timestamp

    [**FFmpeg docs**](https://ffmpeg.org/ffmpeg.html#Advanced-options)
    """

    class LogLevel(str, BrokenEnum):
        Error   = "error"
        Info    = "info"
        Verbose = "verbose"
        Debug   = "debug"
        Warning = "warning"
        Panic   = "panic"
        Fatal   = "fatal"

    loglevel: Annotated[LogLevel,
        Option("--loglevel", "-log")] = \
        Field(LogLevel.Info)

    class HardwareAcceleration(str, BrokenEnum):
        Auto   = "auto"
        CUDA   = "cuda"
        NVDEC  = "nvdec"
        Vulkan = "vulkan"

    hwaccel: Annotated[Optional[HardwareAcceleration],
        Option("--hwaccel", "-hw")] = \
        Field(None)
    """
    What device to bootstrap, for decoding with hardware acceleration. In practice, it's only useful
    when decoding from a source video file, might cause overhead on pipe input mode

    - `auto`: Finds up the best device to use, more often than not nvdec or cuvid

    TODO: Add the required initializers on the final command per option

    [**FFmpeg docs**](https://trac.ffmpeg.org/wiki/HWAccelIntro)
    """

    threads: int = Field(0, ge=0)
    """
    The number of threads the codecs should use (). Generally speaking, more threads drastically
    improves performance, at the cost of worse quality and compression ratios. It's not that bad though. Some
    codecs might not use all available CPU threads. '0' finds the optimal amount automatically

    [**FFmpeg docs**](https://ffmpeg.org/ffmpeg-codecs.html#toc-Codec-Options)
    """

    inputs: List[FFmpegInputType] = Field(default_factory=list)

    filters: List[FFmpegFilterType] = Field(default_factory=list)

    outputs: List[FFmpegOutputType] = Field(default_factory=list)
    """A list of outputs. Yes, FFmpeg natively supports multi-encoding targets"""

    video_codec: Optional[FFmpegVideoCodecType] = Field(default_factory=FFmpegVideoCodecH264)
    """The video codec to use and its configuration"""

    audio_codec: Optional[FFmpegAudioCodecType] = Field(None)
    """The audio codec to use and its configuration"""

    def quiet(self) -> Self:
        self.hide_banner = True
        self.loglevel = "error"
        return self

    # ---------------------------------------------------------------------------------------------|
    # Recycling

    def clear_inputs(self) -> Self:
        self.inputs = list()
        return self

    def clear_filters(self) -> Self:
        self.filters = list()
        return self

    def clear_outputs(self) -> Self:
        self.outputs = list()
        return self

    def clear_video_codec(self) -> Self:
        self.video_codec = None
        return self

    def clear_audio_codec(self) -> Self:
        self.audio_codec = None
        return self

    def clear(self,
        inputs: bool=True,
        filters: bool=True,
        outputs: bool=True,
        video_codec: bool=True,
        audio_codec: bool=True,
    ) -> Self:
        if inputs:      self.clear_inputs()
        if filters:     self.clear_filters()
        if outputs:     self.clear_outputs()
        if video_codec: self.clear_video_codec()
        if audio_codec: self.clear_audio_codec()
        return self

    # ---------------------------------------------------------------------------------------------|
    # Wrappers for all classes

    # Inputs and Outputs

    def add_input(self, input: FFmpegInputType) -> Self:
        self.inputs.append(input)
        return self

    @functools.wraps(FFmpegInputPath)
    def input(self, path: Path, **options) -> Self:
        return self.add_input(FFmpegInputPath(path=path, **options))

    @functools.wraps(FFmpegInputPipe)
    def pipe_input(self, **options) -> Self:
        return self.add_input(FFmpegInputPipe(**options))

    def typer_inputs(self, typer: BrokenTyper) -> None:
        with typer.panel("📦 (FFmpeg) Input"):
            typer.command(FFmpegInputPath, post=self.add_input, name="ipath")
            typer.command(FFmpegInputPipe, post=self.add_input, name="ipipe")

    def add_output(self, output: FFmpegOutputType) -> Self:
        self.outputs.append(output)
        return self

    @functools.wraps(FFmpegOutputPath)
    def output(self, path: Path, **options) -> Self:
        return self.add_output(FFmpegOutputPath(path=path, **options))

    @functools.wraps(FFmpegOutputPipe)
    def pipe_output(self, **options) -> Self:
        return self.add_output(FFmpegOutputPipe(**options))

    def typer_outputs(self, typer: BrokenTyper) -> None:
        with typer.panel("📦 (FFmpeg) Output"):
            typer.command(FFmpegOutputPath, post=self.add_output, name="opath")
            typer.command(FFmpegOutputPipe, post=self.add_output, name="opipe")

    # Video codecs

    def set_video_codec(self, codec: FFmpegVideoCodecType) -> Self:
        self.video_codec = codec
        return self

    @functools.wraps(FFmpegVideoCodecH264)
    def h264(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecH264(**options))

    @functools.wraps(FFmpegVideoCodecH264_NVENC)
    def h264_nvenc(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecH264_NVENC(**options))

    @functools.wraps(FFmpegVideoCodecH265)
    def h265(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecH265(**options))

    @functools.wraps(FFmpegVideoCodecH265_NVENC)
    def h265_nvenc(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecH265_NVENC(**options))

    @functools.wraps(FFmpegVideoCodecVP9)
    def vp9(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecVP9(**options))

    @functools.wraps(FFmpegVideoCodecAV1_LIBAOM)
    def av1_aom(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecAV1_LIBAOM(**options))

    @functools.wraps(FFmpegVideoCodecAV1_SVT)
    def av1_svt(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecAV1_SVT(**options))

    @functools.wraps(FFmpegVideoCodecAV1_NVENC)
    def av1_nvenc(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecAV1_NVENC(**options))

    @functools.wraps(FFmpegVideoCodecAV1_RAV1E)
    def av1_rav1e(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecAV1_RAV1E(**options))

    @functools.wraps(FFmpegVideoCodecRawvideo)
    def rawvideo(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecRawvideo(**options))

    @functools.wraps(FFmpegVideoCodecCopy)
    def copy_video(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecCopy(**options))

    @functools.wraps(FFmpegVideoCodecNoVideo)
    def no_video(self, **options) -> Self:
        return self.set_video_codec(FFmpegVideoCodecNoVideo(**options))

    def typer_vcodecs(self, typer: BrokenTyper) -> None:
        with typer.panel("📦 (Exporting) Video encoder"):
            typer.command(FFmpegVideoCodecH264,       post=self.set_video_codec, name="h264")
            typer.command(FFmpegVideoCodecH264_NVENC, post=self.set_video_codec, name="h264-nvenc")
            typer.command(FFmpegVideoCodecH265,       post=self.set_video_codec, name="h265")
            typer.command(FFmpegVideoCodecH265_NVENC, post=self.set_video_codec, name="h265-nvenc")
            typer.command(FFmpegVideoCodecVP9,        post=self.set_video_codec, name="vp9", hidden=True)
            typer.command(FFmpegVideoCodecAV1_LIBAOM, post=self.set_video_codec, name="av1-aom", hidden=True)
            typer.command(FFmpegVideoCodecAV1_SVT,    post=self.set_video_codec, name="av1-svt")
            typer.command(FFmpegVideoCodecAV1_NVENC,  post=self.set_video_codec, name="av1-nvenc")
            typer.command(FFmpegVideoCodecAV1_RAV1E,  post=self.set_video_codec, name="av1-rav1e")
            typer.command(FFmpegVideoCodecRawvideo,   post=self.set_video_codec, name="rawvideo", hidden=True)
            typer.command(FFmpegVideoCodecCopy,       post=self.set_video_codec, name="video-copy", hidden=True)
            typer.command(FFmpegVideoCodecNoVideo,    post=self.set_video_codec, name="video-none", hidden=True)

    # Audio codecs

    def set_audio_codec(self, codec: FFmpegAudioCodecType) -> Self:
        self.audio_codec = codec
        return self

    @functools.wraps(FFmpegAudioCodecAAC)
    def aac(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecAAC(**options))

    @functools.wraps(FFmpegAudioCodecMP3)
    def mp3(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecMP3(**options))

    @functools.wraps(FFmpegAudioCodecOpus)
    def opus(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecOpus(**options))

    @functools.wraps(FFmpegAudioCodecFLAC)
    def flac(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecFLAC(**options))

    @functools.wraps(FFmpegAudioCodecPCM)
    def pcm(self, format: FFmpegAudioCodecPCM="pcm_f32le") -> Self:
        return self.set_audio_codec(FFmpegAudioCodecPCM(format=format))

    @functools.wraps(FFmpegAudioCodecCopy)
    def copy_audio(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecCopy(**options))

    @functools.wraps(FFmpegAudioCodecNone)
    def no_audio(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecNone(**options))

    @functools.wraps(FFmpegAudioCodecEmpty)
    def empty_audio(self, **options) -> Self:
        return self.set_audio_codec(FFmpegAudioCodecEmpty(**options))

    def typer_acodecs(self, typer: BrokenTyper) -> None:
        with typer.panel("📦 (Exporting) Audio encoder"):
            typer.command(FFmpegAudioCodecAAC,   post=self.set_audio_codec, name="aac")
            typer.command(FFmpegAudioCodecMP3,   post=self.set_audio_codec, name="mp3")
            typer.command(FFmpegAudioCodecOpus,  post=self.set_audio_codec, name="opus")
            typer.command(FFmpegAudioCodecFLAC,  post=self.set_audio_codec, name="flac")
            typer.command(FFmpegAudioCodecCopy,  post=self.set_audio_codec, name="audio-copy")
            typer.command(FFmpegAudioCodecNone,  post=self.set_audio_codec, name="audio-none")
            typer.command(FFmpegAudioCodecEmpty, post=self.set_audio_codec, name="audio-empty")

    # Filters

    def add_filter(self, filter: FFmpegFilterType) -> Self:
        self.filters.append(filter)
        return self

    @functools.wraps(FFmpegFilterScale)
    def scale(self, **options) -> Self:
        return self.add_filter(FFmpegFilterScale(**options))

    @functools.wraps(FFmpegFilterVerticalFlip)
    def vflip(self, **options) -> Self:
        return self.add_filter(FFmpegFilterVerticalFlip(**options))

    @functools.wraps(FFmpegFilterCustom)
    def filter(self, content: str) -> Self:
        return self.add_filter(FFmpegFilterCustom(content=content))

    def typer_filters(self, typer: BrokenTyper) -> None:
        with typer.panel("📦 (FFmpeg) Filters"):
            typer.command(FFmpegFilterScale,        post=self.add_filter, name="scale")
            typer.command(FFmpegFilterVerticalFlip, post=self.add_filter, name="vflip")
            typer.command(FFmpegFilterCustom,       post=self.add_filter, name="filter")

    # ---------------------------------------------------------------------------------------------|
    # Command building and running

    @property
    def command(self) -> List[str]:
        BrokenFFmpeg.install()

        if (not self.inputs):
            raise ValueError("At least one input is required for FFmpeg")
        if (not self.outputs):
            raise ValueError("At least one output is required for FFmpeg")

        command = deque()

        def extend(*objects: Union[FFmpegModuleBase, Iterable[FFmpegModuleBase]]):
            for item in flatten(objects):
                if isinstance(item, FFmpegModuleBase):
                    command.extend(flatten(item.command(self)))
                else:
                    command.append(item)

        extend(shutil.which("ffmpeg"))
        extend(("-stream_loop", self.stream_loop)*bool(self.stream_loop))
        extend("-threads", self.threads)
        extend("-hide_banner"*self.hide_banner)
        extend("-loglevel", denum(self.loglevel))
        extend(("-hwaccel", denum(self.hwaccel))*bool(self.hwaccel))
        extend(self.inputs)

        # Note: https://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
        for output in self.outputs:
            extend(self.audio_codec)
            extend(self.video_codec)
            extend(("-vf", ",".join(map(str, self.filters)))*bool(self.filters))
            extend(output)

        extend("-shortest"*self.shortest)
        extend(("-t", self.time)*bool(self.time))
        return list(map(str, denum(flatten(command))))

    def run(self, **options) -> subprocess.CompletedProcess:
        return shell(self.command, **options)

    def popen(self, **options) -> subprocess.Popen:
        return shell(self.command, Popen=True, **options)

    # ---------------------------------------------------------------------------------------------|
    # High level functions

    @staticmethod
    def install(raises: bool=True) -> None:
        if all(map(BrokenPath.which, ("ffmpeg", "ffprobe"))):
            return None

        if (not BrokenPlatform.OnMacOS):
            log.info("FFmpeg wasn't found on System Path, will download a BtbN's Build")
            BrokenPath.get_external(''.join((
                "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/",
                "ffmpeg-master-latest-",
                BrokenPlatform.System.value.replace("windows", "win"),
                BrokenPlatform.Arch.replace("amd64", "64"),
                ("-gpl.zip" if BrokenPlatform.OnWindows else "-gpl.tar.xz")
            )))
        else:
            log.info("FFmpeg wasn't found on System Path, will download a EverMeet's Build")
            ffprobe = BrokenPath.get_external("https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip", redirect=True)
            ffmpeg  = BrokenPath.get_external("https://evermeet.cx/ffmpeg/getrelease/zip", redirect=True)

            # Shutil doesn't preserve executable attributes
            for file in ffprobe.rglob("ffprobe*"):
                BrokenPath.make_executable(file)
            for file in ffmpeg.rglob("ffmpeg*"):
                BrokenPath.make_executable(file)

        # Ensure the binaries are available
        if raises and (not all(map(BrokenPath.which, ("ffmpeg", "ffprobe")))):
            raise FileNotFoundError("FFmpeg wasn't found on the system after an attempt to download it")

    # # Video

    @staticmethod
    @functools.lru_cache
    def get_video_resolution(path: Path, *, echo: bool=True) -> Optional[Tuple[int, int]]:
        """Get the resolution of a video in a smart way"""
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Video Resolution of ({path})", echo=echo)
        import PIL
        return PIL.Image.open(io.BytesIO(shell(
            shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error",
            "-i", path, "-vframes", "1", "-f", "image2pipe", "-",
            stdout=PIPE, echo=echo
        ).stdout), formats=["jpeg"]).size

    @staticmethod
    def iter_video_frames(path: Path, *, skip: int=0, echo: bool=True) -> Optional[Iterable[numpy.ndarray]]:
        """Generator for every frame of the video as numpy arrays, FAST!"""
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        (width, height) = BrokenFFmpeg.get_video_resolution(path)
        log.minor(f"Streaming Video Frames from file ({path}) @ ({width}x{height})", echo=echo)
        ffmpeg = (BrokenFFmpeg(vsync="cfr")
            .quiet()
            .input(path=path)
            .filter(content=f"select='gte(n\\,{skip})'")
            .rawvideo()
            .no_audio()
            .pipe_output(format="rawvideo")
        ).popen(stdout=PIPE, echo=echo)

        # Keep reading frames until we run out, each pixel is 3 bytes !
        while (raw := ffmpeg.stdout.read(width * height * 3)):
            yield numpy.frombuffer(raw, dtype=numpy.uint8).reshape((height, width, 3))

    @staticmethod
    def is_valid_video(path: Path, *, echo: bool=True) -> bool:
        if not (path := BrokenPath.get(path, exists=True)):
            return False
        BrokenFFmpeg.install()
        return (shell(
            shutil.which("ffmpeg"),
            "-hide_banner", "-loglevel", "error",
            "-i", path, "-f", "null", "-", echo=echo,
            stderr=DEVNULL, stdout=DEVNULL
        ).returncode == 0)

    @staticmethod
    @functools.lru_cache
    def get_video_total_frames(path: Path, *, echo: bool=True) -> Optional[int]:
        """Count the total frames of a video by decode voiding and parsing stats output"""
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        with Halo(log.minor(f"Getting total frames of video ({path}) by decoding every frame, might take a while..")):
            return int(re.compile(r"frame=\s*(\d+)").findall((
                BrokenFFmpeg(vsync="cfr")
                .input(path=path)
                .pipe_output(format="null")
            ).run(stderr=PIPE, echo=echo).stderr.decode())[-1])

    @staticmethod
    @functools.lru_cache
    def get_video_duration(path: Path, *, echo: bool=True) -> Optional[float]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Video Duration of file ({path})", echo=echo)
        return float(shell(
            BrokenPath.which("ffprobe"),
            "-i", path,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ))

    @staticmethod
    @functools.lru_cache
    def get_video_framerate(path: Path, *, precise: bool=False, echo: bool=True) -> Optional[float]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Video Framerate of file ({path})", echo=echo)
        if precise:
            A = BrokenFFmpeg.get_video_total_frames(path, echo=False)
            B = BrokenFFmpeg.get_video_duration(path, echo=False)
            return (A/B)
        else:
            return float(flatten(eval(shell(
                BrokenPath.which("ffprobe"),
                "-i", path,
                "-show_entries", "stream=r_frame_rate",
                "-v", "quiet", "-of", "csv=p=0",
                output=True, echo=echo
            ).splitlines()[0]))[0])

    # # Audio

    @staticmethod
    @functools.lru_cache
    def get_audio_samplerate(path: Path, *, stream: int=0, echo: bool=True) -> Optional[float]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Audio Samplerate of file ({path})", echo=echo)
        return int(shell(
            BrokenPath.which("ffprobe"),
            "-i", path,
            "-show_entries", "stream=sample_rate",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ).strip().splitlines()[stream])

    @staticmethod
    @functools.lru_cache
    def get_audio_channels(path: Path, *, stream: int=0, echo: bool=True) -> Optional[int]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Audio Channels of file ({path})", echo=echo)
        return int(shell(
            BrokenPath.which("ffprobe"),
            "-i", path,
            "-show_entries", "stream=channels",
            "-v", "quiet", "-of", "csv=p=0",
            output=True, echo=echo
        ).strip().splitlines()[stream])

    @staticmethod
    def get_audio_duration(path: Path, *, echo: bool=True) -> Optional[float]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        try:
            generator = BrokenAudioReader(path=path, chunk=10).stream
            while next(generator) is not None: ...
        except StopIteration as result:
            return result.value

    @staticmethod
    def get_audio_numpy(path: Path, *, echo: bool=True) -> Optional[numpy.ndarray]:
        if not (path := BrokenPath.get(path, exists=True)):
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Audio as Numpy Array of file ({path})", echo=echo)
        return numpy.concatenate(list(BrokenAudioReader(path=path, chunk=10).stream))

# ------------------------------------------------------------------------------------------------ #
# BrokenFFmpeg Spin-offs

@define
class BrokenAudioReader:
    path:        Path
    chunk:       Seconds     = 0.1
    format:      FFmpegPCM   = FFmpegPCM.PCM_FLOAT_32_BITS_LITTLE_ENDIAN
    echo:        bool        = False
    _read:       Bytes       = 0
    _channels:   int         = None
    _samplerate: Hertz       = None
    _dtype:      numpy.dtype = None
    _size:       int         = 4
    _ffmpeg:     Popen       = None

    @property
    def time(self) -> Seconds: # noqa
        return self._read / self.bytes_per_second

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def samplerate(self) -> Hertz:
        return self._samplerate

    @property
    def dtype(self) -> numpy.dtype:
        return self._dtype

    @property
    def size(self) -> int:
        return self._size

    @property
    def bytes_per_second(self) -> int:
        return (self.size * self.channels * self.samplerate)

    @property
    def bytes_per_sample(self) -> int:
        return (self.size * self.channels)

    @property
    def stream(self) -> Generator[numpy.ndarray, None, None]:
        if not (path := BrokenPath.get(self.path, exists=True)):
            return None
        self.path = path

        # Get audio file attributes
        self._channels   = BrokenFFmpeg.get_audio_channels(self.path, echo=self.echo)
        self._samplerate = BrokenFFmpeg.get_audio_samplerate(self.path, echo=self.echo)
        self.format = FFmpegPCM.get(self.format)
        self._dtype = self.format.dtype
        self._size = self.format.size
        self._read = 0

        # Note: Stderr to null as we might not read all the audio, won't log errors
        self._ffmpeg = (
            BrokenFFmpeg()
            .quiet()
            .input(path=self.path)
            .pcm(self.format.value)
            .no_video()
            .output("-")
        ).popen(stdout=PIPE)

        """
        One could think the following code is the way, but it is not

        ```python
        while (data := ffmpeg.stdout.read(chunk*samplerate)):
            yield (...)
        ```

        Reason being:
        • Small reads yields time imprecision on sample domain vs time domain
        • Must keep track of theoretical time and real time of the read
        """
        target = 0

        while True:
            target += self.chunk

            # Calculate the length of the next read to best match the target time,
            # but do not carry over temporal conversion errors
            length = (target - self.time) * self.bytes_per_second
            length = nearest(length, self.bytes_per_sample, cast=int)
            length = max(length, self.bytes_per_sample)
            data   = self._ffmpeg.stdout.read(length)
            if len(data) == 0: break

            # Increment precise time and read time
            yield numpy.frombuffer(data, dtype=self.dtype).reshape(-1, self.channels)
            self._read += len(data)

        return self.time
