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
import PIL
import PIL.Image
from attrs import define
from pydantic import BaseModel, Field, field_validator

from Broken import (
    BrokenEnum,
    BrokenPath,
    BrokenPlatform,
    BrokenSpinner,
    flatten,
    log,
    nearest,
    shell,
)
from Broken.Types import Bytes, Hertz, Seconds

# -------------------------------------------------------------------------------------------------|
# Enum's land

class FFmpegPCM(BrokenEnum):
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

    @property
    @functools.lru_cache
    def size(self) -> int:
        return int(''.join(filter(str.isdigit, self.value)))//8

    @property
    @functools.lru_cache
    def endian(self) -> str:
        return "<" if ("le" in self.value) else ">"

    @property
    @functools.lru_cache
    def dtype(self) -> numpy.dtype:
        type = self.value.split("_")[1][0]
        return numpy.dtype(f"{self.endian}{type}{self.size}")

# -------------------------------------------------------------------------------------------------|

class FFmpegModuleBase(BaseModel, ABC):

    @abstractmethod
    def command(self) -> Iterable[str]:
        ...

    def all(self, *args) -> List[Optional[str]]:
        if (None in args) or ('' in args):
            return []
        return args

# -------------------------------------------------------------------------------------------------|

class FFmpegInputPath(FFmpegModuleBase):
    # type: Literal["path"] = "path"
    path: Path

    def command(self) -> Iterable[str]:
        return ("-i", self.path)

class FFmpegInputPipe(FFmpegModuleBase):
    type: Literal["pipe"] = "pipe"

    format: Optional[Literal[
        "rawvideo",
        "image2pipe",
        "null",
    ]] = Field(default="rawvideo")

    pixel_format: Literal[
        "rgb24",
        "rgba"
    ] = Field(default="rgb24")


    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)

    framerate: float = Field(default=60.0, gt=-1.0)

    @field_validator("framerate", mode="plain")
    def validate_framerate(cls, value: Union[float, str]) -> float:
        return eval(str(value))

    def command(self) -> Iterable[str]:
        yield ("-f", self.format)
        yield ("-s", f"{self.width}x{self.height}")
        yield ("-pix_fmt", self.pixel_format)
        yield ("-r", self.framerate)
        yield ("-i", "-")

FFmpegInputType: TypeAlias = Union[
    FFmpegInputPipe,
    FFmpegInputPath
]

# -------------------------------------------------------------------------------------------------|

class FFmpegOutputPipe(FFmpegModuleBase):
    type: Literal["pipe"] = "pipe"
    format: Optional[Literal[
        "rawvideo",
        "image2pipe",
        "null",
    ]] = Field(default=None)

    pixel_format: Literal[
        "rgb24",
        "rgba"
    ] = Field(default=None)

    def command(self) -> Iterable[str]:
        yield self.all("-f", self.format)
        yield self.all("-pix_fmt", self.pixel_format)
        yield "-"

class FFmpegOutputPath(FFmpegModuleBase):
    type: Literal["path"] = "path"
    overwrite: bool = True
    path: Path

    def command(self) -> Iterable[str]:
        return (self.path, self.overwrite*"-y")

FFmpegOutputType = Union[
    FFmpegOutputPipe,
    FFmpegOutputPath,
]

# -------------------------------------------------------------------------------------------------|
# Todo: QSV, AMF, VVC ?

class FFmpegVideoCodecH264(FFmpegModuleBase):
    """https://trac.ffmpeg.org/wiki/Encode/H.264"""
    codec: Literal["h264"] = "h264"

    crf: int = Field(default=20, ge=0, le=51)
    """Constant Rate Factor. 0 is lossless, 51 is the worst quality
    • https://trac.ffmpeg.org/wiki/Encode/H.264#a1.ChooseaCRFvalue
    """

    bitrate: Optional[int] = Field(default=None, gt=-1)

    preset: Optional[Literal[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    ]] = Field(default="slow")
    """How much time to spend on encoding. Slower options gives better compression
    • https://trac.ffmpeg.org/wiki/Encode/H.264#Preset
    """

    tune: Optional[Literal[
        "film",
        "animation",
        "grain",
        "stillimage",
        "fastdecode",
        "zerolatency"
    ]] = Field(default=None)
    """Tune x264 to keep and optimize for certain aspects of the input media. See link for more:
    • https://trac.ffmpeg.org/wiki/Encode/H.264#Tune
    """

    profile: Optional[Literal[
        "baseline",
        "main",
        "high",
        "high10",
        "high422",
        "high444",
    ]] = Field(default=None)
    """What features the encoder can use. The playback device must support the same profile level
    • https://trac.ffmpeg.org/wiki/Encode/H.264#Profile
    """

    faststart: bool = Field(default=False)

    rgb: bool = Field(default=False)

    def command(self) -> Iterable[str]:
        yield self.all("-c:v", "libx264rgb" if self.rgb else "libx264")
        yield self.all("-profile", self.profile)
        yield self.all("-preset", self.preset)
        yield self.all("-tune", self.tune)
        yield self.all("-crf", str(self.crf))
        yield self.all("-movflags", "+faststart"*self.faststart)
        yield self.all("-b:v", self.bitrate)

class FFmpegVideoCodecH264_NVENC(FFmpegModuleBase):
    """`ffmpeg -h encoder=h264_nvenc`"""
    codec: Literal["h264_nvenc"] = "h264_nvenc"

    preset: Optional[Literal[
        "default", # Defaults to p4
        "slow", # High quality 2 passes
        "medium", # High quality 1 pass
        "fast", # High quality 1 pass
        "hp", # High performance
        "hq", # High quality
        "bd", # Balanced
        "ll", # Low latency
        "llhq", # Low latency high quality
        "llhp", # Low latency high performance
        "lossless", # Lossless
        "losslesshp", # Lossless high performance
        "p1", # fastest
        "p2", # faster
        "p3", # fast
        "p4", # medium
        "p5", # slow
        "p6", # slower
        "p7", # slowest
    ]] = Field(default="p5")

    tune: Optional[Literal[
        "hq", # High quality
        "ll", # Low latency
        "ull", # Ultra low latency
        "lossless" # Lossless
    ]] = Field(default="hq")

    profile: Optional[Literal[
        "baseline", # Very old devices
        "main", # Relatively modern devices
        "high", # Modern devices
        "high444p" # Modern devices
    ]] = Field(default="high")

    rc: Optional[Literal[
        "constqp", # Constant Quality 'Factor'
        "vbr", # Variable bitrate
        "cbr", # Constant bitrate
    ]] = Field(default="vbr")
    """'Rate Control' mode"""

    rc_lookahead: Optional[int] = Field(default=32, gt=-1)
    """Number of frames to look ahead for the rate control"""

    cbr: bool = Field(default=False)
    """Use Constant Bitrate mode"""

    gpu: int = Field(default=0, gt=-1)
    """Use the Nth NVENC capable GPU for encoding"""

    cq: int = Field(default=25, gt=-1)
    """Set the Constant Quality factor in a Variable Bitrate mode (similar to -crf)"""

    def command(self) -> Iterable[str]:
        yield self.all("-c:v", "h264_nvenc")
        yield self.all("-b:v", 0)
        yield self.all("-preset", self.preset)
        yield self.all("-tune", self.tune)
        yield self.all("-profile", self.profile)
        yield self.all("-rc", self.rc)
        yield self.all("-rc-lookahead", self.rc_lookahead)
        yield self.all("-cbr", int(self.cbr))
        yield self.all("-cq", self.cq)
        yield self.all("-gpu", self.gpu)


class FFmpegVideoCodecH265(FFmpegModuleBase):
    """https://trac.ffmpeg.org/wiki/Encode/H.265"""
    codec: Literal["h265"] = "h265"

    crf: int = Field(default=25, ge=0, le=51)
    """Constant Rate Factor. 0 is lossless, 51 is the worst quality"""

    bitrate: Optional[int] = Field(default=None, gt=-1)

    preset: Optional[Literal[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    ]] = Field(default="slow")

    def command(self) -> Iterable[str]:
        yield self.all("-c:v", "libx265")
        yield self.all("-preset", self.preset)
        yield self.all("-crf", str(self.crf))
        yield self.all("-b:v", self.bitrate)


class FFmpegVideoCodecH265_NVENC(FFmpegVideoCodecH265):
    """`ffmpeg -h encoder=hevc_nvenc`"""
    codec: Literal["hevc_nvenc"] = "hevc_nvenc"

    preset: Optional[Literal[
        "default", # Defaults to p4
        "slow", # High quality 2 passes
        "medium", # High quality 1 pass
        "fast", # High quality 1 pass
        "hp", # High performance
        "hq", # High quality
        "bd", # Balanced
        "ll", # Low latency
        "llhq", # Low latency high quality
        "llhp", # Low latency high performance
        "lossless", # Lossless
        "losslesshp", # Lossless high performance
        "p1", # fastest
        "p2", # faster
        "p3", # fast
        "p4", # medium
        "p5", # slow
        "p6", # slower
        "p7", # slowest
    ]] = Field(default="p5")

    tune: Optional[Literal[
        "hq", # High quality
        "ll", # Low latency
        "ull", # Ultra low latency
        "lossless" # Lossless
    ]] = Field(default="hq")

    profile: Optional[Literal[
        "main", # Modern devices
        "main10", # HDR 10 bits
        "rext"
    ]] = Field(default=None)

    tier: Optional[Literal[
        "main",
        "high",
    ]] = Field(default="high")

    rc: Optional[Literal[
        "constqp", # Constant Quality 'Factor'
        "vbr", # Variable bitrate
        "cbr", # Constant bitrate
    ]] = Field(default="vbr")
    """'Rate Control' mode"""

    rc_lookahead: Optional[int] = Field(default=10, gt=-1)
    """Number of frames to look ahead for the rate control"""

    cbr: bool = Field(default=False)
    """Use Constant Bitrate mode"""

    gpu: int = Field(default=0, gt=-1)
    """Use the Nth NVENC capable GPU for encoding"""

    cq: int = Field(default=25, gt=-1)
    """Set the Constant Quality factor in a Variable Bitrate mode (similar to -crf)"""

    def command(self) -> Iterable[str]:
        yield self.all("-c:v", "hevc_nvenc")
        yield self.all("-preset", self.preset)
        yield self.all("-tune", self.tune)
        yield self.all("-profile", self.profile)
        yield self.all("-tier", self.tier)
        yield self.all("-rc", self.rc)
        yield self.all("-rc-lookahead", self.rc_lookahead)
        yield self.all("-cbr", int(self.cbr))
        yield self.all("-cq", self.cq)
        yield self.all("-gpu", self.gpu)


class FFmpegVideoCodecVP9(FFmpegModuleBase):
    """https://trac.ffmpeg.org/wiki/Encode/VP9"""
    codec: Literal["libvpx-vp9"] = "libvpx-vp9"

    crf: int = Field(default=30, gt=-1, lt=64)
    """Constant Rate Factor (0-63). Lower values mean better quality, recommended (15-31)
    • https://trac.ffmpeg.org/wiki/Encode/VP9#constantq
    """

    speed: int = Field(default=4, gt=-1, lt=6)
    """Speed level (0-6). Higher values yields faster encoding but innacuracies in rate control
    • https://trac.ffmpeg.org/wiki/Encode/VP9#CPUUtilizationSpeed
    """

    deadline: Optional[Literal[
        "good", # General cases
        "best", # Offline renders
        "realtime",
    ]] = Field(default="good")
    """Tweak the encoding time philosophy. 'good' for general cases, 'best' for offline renders when
    there's plenty time available and best quality, 'realtime' for streams and low latency
    • https://trac.ffmpeg.org/wiki/Encode/VP9#DeadlineQuality
    """

    row_multithreading: bool = Field(default=True)
    """Faster encodes by splitting rows into multiple threads. Slight innacuracy on the rate control.
    Recommended for >= 1080p videos. Requires libvpx >= 1.7.0 (you should have it)
    • https://trac.ffmpeg.org/wiki/Encode/VP9#rowmt
    """

    def command(self) -> Iterable[str]:
        yield ("-c:v", "libvpx-vp9")
        yield ("-crf", self.crf)
        yield ("-b:v", 0)
        yield ("-deadline", self.deadline)
        yield ("-cpu-used", self.speed)
        yield ("-row-mt", "1") * self.row_multithreading


class FFmpegVideoCodecAV1_LIBAOM(FFmpegModuleBase):
    """The reference encoder for AV1. Similar to VP9, not the fastest current implementation
    • https://trac.ffmpeg.org/wiki/Encode/AV1#libaom
    """
    codec: Literal["libaom-av1"] = "libaom-av1"

    crf: int = Field(default=23, gt=-1, lt=64)
    """Constant Rate Factor (0-63). Lower values mean better quality, AV1 CRF 23 == x264 CRF 19
    • https://trac.ffmpeg.org/wiki/Encode/AV1#ConstantQuality
    """

    speed: int = Field(default=3, gt=-1, lt=7)
    """Speed level (0-6). Higher values yields faster encoding but innacuracies in rate control
    • https://trac.ffmpeg.org/wiki/Encode/AV1#ControllingSpeedQuality
    """

    def command(self) -> Iterable[str]:
        yield ("-c:v", "libaom-av1")
        yield ("-crf", self.crf)
        yield ("-cpu-used", self.speed)
        yield ("-row-mt", 1)
        yield ("-tiles", "2x2")


class FFmpegVideoCodecAV1_SVT(FFmpegModuleBase):
    """The official codec for future development of AV1. Faster than libaom reference
    • https://trac.ffmpeg.org/wiki/Encode/AV1#SVT-AV1
    """
    codec: Literal["libsvtav1"] = "libsvtav1"

    crf: int = Field(default=25, gt=-1, lt=64)
    """Constant Rate Factor (0-63). Lower values mean better quality,
    • https://trac.ffmpeg.org/wiki/Encode/AV1#CRF
    """

    preset: int = Field(default=3, gt=-1, lt=9)
    """The speed of the encoding, 0 is slowest, 8 is fastest. Decreases compression efficiency.
    • https://trac.ffmpeg.org/wiki/Encode/AV1#Presetsandtunes
    """

    def command(self) -> Iterable[str]:
        yield ("-c:v", "libsvtav1")
        yield ("-crf", self.crf)
        yield ("-preset", self.preset)
        yield ("-svtav1-params", "tune=0")


class FFmpegVideoCodecAV1_RAV1E(FFmpegModuleBase):
    """`ffmpeg -h encoder=librav1e`
    https://github.com/xiph/rav1e
    """
    codec: Literal["librav1e"] = "librav1e"

    qp: int = Field(default=80, gt=-2)
    """Constant quantizer mode (from -1 to 255). Smaller values are higher quality"""

    speed: int = Field(default=4, gt=-1, lt=11)
    """What speed preset to use (from -1 to 10) (default -1)"""

    tile_rows: int = Field(default=2, gt=-1)
    """Number of tile rows to encode with (from -1 to I64_MAX) (default 0)"""

    tile_columns: int = Field(default=2, gt=-1)
    """Number of tile columns to encode with (from -1 to I64_MAX) (default 0)"""

    def command(self) -> Iterable[str]:
        yield ("-c:v", "librav1e")
        yield ("-qp", self.qp)
        yield ("-speed", self.speed)
        yield ("-tile-rows", self.tile_rows)
        yield ("-tile-columns", self.tile_columns)


class FFmpegVideoCodecAV1_NVENC(FFmpegModuleBase):
    """`ffmpeg -h encoder=av1_nvenc`
    NVIDIA's NVENC encoder for AV1
    # Warning: REQUIRES A RTX 4000+ GPU (ADA Love Lace Architecture or newer
    """
    codec: Literal["av1_nvenc"] = "av1_nvenc"

    preset: Optional[Literal[
        "default", # Defaults to p4
        "slow", # High quality 2 passes
        "medium", # High quality 1 pass
        "fast", # High quality 1 pass
        "p1", # fastest
        "p2", # faster
        "p3", # fast
        "p4", # medium
        "p5", # slow
        "p6", # slower
        "p7", # slowest
    ]] = Field(default="p5")

    tune: Optional[Literal[
        "hq", # High quality
        "ll", # Low latency
        "ull", # Ultra low latency
        "lossless" # Lossless
    ]] = Field(default="hq")

    rc: Optional[Literal[
        "constqp", # Constant Quality 'Factor'
        "vbr", # Variable bitrate
        "cbr", # Constant bitrate
    ]] = Field(default="vbr")
    """'Rate Control' mode"""

    multipass: Optional[Literal[
        "disabled",
        "qres", # First pass is quarter resolution
        "fullres", # First pass is full resolution
    ]] = Field(default="fullres")

    tile_rows: Optional[int] = Field(default=2, gt=-1, lt=65)
    """Number of encoding tile rows, similar to -row-mt"""

    tile_columns: Optional[int] = Field(default=2, gt=-1, lt=65)
    """Number of encoding tile columns, similar to -col-mt"""

    rc_lookahead: Optional[int] = Field(default=10, gt=-1)
    """Number of frames to look ahead for the rate control"""

    gpu: int = Field(default=0, gt=-1)
    """Use the Nth NVENC capable GPU for encoding"""

    cq: int = Field(default=25, gt=-1)
    """Set the Constant Quality factor in a Variable Bitrate mode (similar to -crf)"""

    def command(self) -> Iterable[str]:
        yield self.all("-c:v", "av1_nvenc")
        yield self.all("-preset", self.preset)
        yield self.all("-tune", self.tune)
        yield self.all("-rc", self.rc)
        yield self.all("-rc-lookahead", self.rc_lookahead)
        yield self.all("-cq", self.cq)
        yield self.all("-gpu", self.gpu)


class FFmpegVideoCodecRawvideo(FFmpegModuleBase):
    codec: Literal["rawvideo"] = "rawvideo"

    def command(self) -> Iterable[str]:
        yield ("-c:v", "rawvideo")


class FFmpegVideoCodecCopy(FFmpegModuleBase):
    codec: Literal["copy"] = "copy"

    def command(self) -> Iterable[str]:
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
    FFmpegVideoCodecCopy,
]

# -------------------------------------------------------------------------------------------------|

class FFmpegAudioCodecAAC(FFmpegModuleBase):
    codec: Literal["aac"] = "aac"

    bitrate: int = Field(default=192, gt=-1)
    """Bitrate in kilobits per second. This value is shared between all audio channels"""

    def command(self) -> Iterable[str]:
        yield self.all("-c:a", "aac")
        yield self.all("-b:a", f"{self.bitrate}k")

class FFmpegAudioCodecMP3(FFmpegModuleBase):
    """https://trac.ffmpeg.org/wiki/Encode/MP3"""
    codec: Literal["mp3"] = "mp3"

    qscale: int = Field(default=2, gt=-1)
    """Quality scale, 0-9, Variable Bitrate"""

    def command(self) -> Iterable[str]:
        yield self.all("-c:a", "libmp3lame")
        yield self.all("-qscale:a", self.qscale)

class FFmpegAudioCodecOpus(FFmpegModuleBase):
    codec: Literal["libopus"] = "libopus"

    def command(self) -> Iterable[str]:
        yield self.all("-c:a", "libopus")

class FFmpegAudioCodecVorbis(FFmpegModuleBase):
    codec: Literal["libvorbis"] = "libvorbis"

    def command(self) -> Iterable[str]:
        yield self.all("-c:a", "libvorbis")

class FFmpegAudioCodecFLAC(FFmpegModuleBase):
    codec: Literal["flac"] = "flac"

    def command(self) -> Iterable[str]:
        yield self.all("-c:a", "flac")

class FFmpegAudioCodecCopy(FFmpegModuleBase):
    codec: Literal["copy"] = "copy"

    def command(self) -> Iterable[str]:
        yield ("-c:a", "copy")

class FFmpegAudioCodecNone(FFmpegModuleBase):
    codec: Literal["none"] = "none"

    def command(self) -> Iterable[str]:
        yield ("-an")

class FFmpegAudioCodecEmpty(FFmpegModuleBase):
    codec: Literal["anullsrc"] = "anullsrc"
    samplerate: float = 44100

    def command(self) -> Iterable[str]:
        yield ("-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={self.samplerate}")

FFmpegAudioCodecType: TypeAlias = Union[
    FFmpegAudioCodecAAC,
    FFmpegAudioCodecMP3,
    FFmpegAudioCodecOpus,
    FFmpegAudioCodecFLAC,
    FFmpegAudioCodecCopy,
    FFmpegAudioCodecNone,
    FFmpegAudioCodecEmpty,
]

# -------------------------------------------------------------------------------------------------|

class FFmpegFilterBase(BaseModel, ABC):

    @abstractmethod
    def string(self) -> Iterable[str]:
        ...

    def __str__(self) -> str:
        return self.string()

class FFmpegFilterScale(FFmpegFilterBase):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    resample: Literal[
        "lanczos",
        "bicubic",
        "fast_bilinear",
        "point",
        "spline",
    ] = Field(default="lanczos")

    def string(self) -> str:
        return f"scale={self.width}:{self.height}:flags={self.resample}"

class FFmpegFilterVerticalFlip(FFmpegFilterBase):
    def string(self) -> str:
        return "vflip"

class FFmpegFilterCustom(FFmpegFilterBase):
    content: str

    def string(self) -> str:
        return self.content

FFmpegFilterType: TypeAlias = Union[
    FFmpegFilterScale,
    FFmpegFilterVerticalFlip,
    FFmpegFilterCustom
]

# -------------------------------------------------------------------------------------------------|

class SerdeBaseModel(BaseModel):
    def serialize(self, json: bool=True) -> Union[dict, str]:
        if json: return self.model_dump_json()
        return self.model_dump()

    @classmethod
    def deserialize(cls, value: Union[dict, str]) -> Self:
        if isinstance(value, dict):
            return cls.model_validate(value)
        elif isinstance(value, str):
            return cls.model_validate_json(value)
        else:
            raise ValueError(f"Can't deserialize value of type {type(value)}")

# -------------------------------------------------------------------------------------------------|

class BrokenFFmpeg(SerdeBaseModel):
    hide_banner: bool = True
    shortest: bool = False

    loglevel: Literal[
        "error",
        "info",
        "verbose",
        "debug",
        "warning",
        "panic",
        "fatal",
    ] = Field(default="info")

    hwaccel: Optional[Literal[
        "auto",
        "cuda",
        "nvdec",
    ]] = Field(default=None)
    """https://trac.ffmpeg.org/wiki/HWAccelIntro"""

    threads: int = Field(default=0, gt=-1)
    """The number of threads FFmpeg should use. Generally speaking, more threads yields worse quality
    and compression ratios, but drastically improves performance. Behavior changes depending on codecs,
    some might not use more than a few depending on settings. '0' finds the optimal automatically"""

    vsync: Literal[
        "auto",
        "passthrough",
        "cfr",
        "vfr",
    ] = Field(default="cfr")

    inputs: List[FFmpegInputType] = Field(default_factory=list)

    filters: List[FFmpegFilterType] = Field(default_factory=list)

    outputs: List[FFmpegOutputType] = Field(default_factory=list)
    """A list of outputs. Yes, FFmpeg natively supports multi-encoding targets"""

    video_codec: Optional[FFmpegVideoCodecType] = Field(default=None)
    """The video codec to use and its configuration"""

    audio_codec: Optional[FFmpegAudioCodecType] = Field(default=None)
    """The audio codec to use and its configuration"""

    def quiet(self) -> Self:
        self.hide_banner = True
        self.loglevel = "error"
        return self

    # ---------------------------------------------------------------------------------------------|
    # Wrappers for all classes

    # Inputs and Outputs

    @functools.wraps(FFmpegInputPath)
    def input(self, **kwargs) -> Self:
        self.inputs.append(FFmpegInputPath(**kwargs))
        return self

    @functools.wraps(FFmpegInputPipe)
    def pipe(self, **kwargs) -> Self:
        self.inputs.append(FFmpegInputPipe(**kwargs))
        return self

    @functools.wraps(FFmpegOutputPath)
    def output(self, **kwargs) -> Self:
        self.outputs.append(FFmpegOutputPath(**kwargs))
        return self

    @functools.wraps(FFmpegOutputPipe)
    def pipe_output(self, **kwargs) -> Self:
        self.outputs.append(FFmpegOutputPipe(**kwargs))
        return self

    # Video codecs

    @functools.wraps(FFmpegVideoCodecH264)
    def h264(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecH264(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecH264_NVENC)
    def h264_nvenc(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecH264_NVENC(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecH265)
    def h265(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecH265(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecH265_NVENC)
    def h265_nvenc(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecH265_NVENC(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecVP9)
    def vp9(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecVP9(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecAV1_LIBAOM)
    def av1_aom(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecAV1_LIBAOM(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecAV1_SVT)
    def av1_svt(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecAV1_SVT(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecAV1_NVENC)
    def av1_nvenc(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecAV1_NVENC(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecAV1_RAV1E)
    def av1_rav1e(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecAV1_RAV1E(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecRawvideo)
    def rawvideo(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecRawvideo(**kwargs)
        return self

    @functools.wraps(FFmpegVideoCodecCopy)
    def copy_video(self, **kwargs) -> Self:
        self.video_codec = FFmpegVideoCodecCopy(**kwargs)
        return self

    def apply_vcodec_str(self, codec: str) -> Self:
        codec = codec.replace("_", "-").lower()
        if   (codec == "h264"      ): self.h264()
        elif (codec == "h264-nvenc"): self.h264_nvenc()
        elif (codec == "h265"      ): self.h265()
        elif (codec == "h265-nvenc"): self.h265_nvenc()
        elif (codec == "hevc-nvenc"): self.h265_nvenc()
        elif (codec == "vp9"       ): self.vp9()
        elif (codec == "av1-aom"   ): self.av1_aom()
        elif (codec == "av1-svt"   ): self.av1_svt()
        elif (codec == "av1-nvenc" ): self.av1_nvenc()
        elif (codec == "av1-rav1e" ): self.av1_rav1e()
        else: raise ValueError(f"Unknown Video Codec: {codec}")
        return self

    # Audio codecs

    @functools.wraps(FFmpegAudioCodecAAC)
    def aac(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecAAC(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecMP3)
    def mp3(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecMP3(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecOpus)
    def opus(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecOpus(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecFLAC)
    def flac(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecFLAC(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecCopy)
    def copy_audio(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecCopy(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecNone)
    def no_audio(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecNone(**kwargs)
        return self

    @functools.wraps(FFmpegAudioCodecEmpty)
    def empty_audio(self, **kwargs) -> Self:
        self.audio_codec = FFmpegAudioCodecEmpty(**kwargs)
        return self

    def apply_acodec_str(self, codec: str) -> Self:
        codec = codec.lower()
        if   (codec == "aac"   ): self.aac()
        elif (codec == "mp3"   ): self.mp3()
        elif (codec == "opus"  ): self.opus()
        elif (codec == "flac"  ): self.flac()
        elif (codec == "copy"  ): self.copy_audio()
        elif (codec == "none"  ): self.no_audio()
        elif (codec == "empty" ): self.empty_audio()
        else: raise ValueError(f"Unknown Audio Codec: {codec}")
        return self

    # Filters

    @functools.wraps(FFmpegFilterScale)
    def scale(self, **kwargs) -> Self:
        self.filters.append(FFmpegFilterScale(**kwargs))
        return self

    @functools.wraps(FFmpegFilterVerticalFlip)
    def vflip(self, **kwargs) -> Self:
        self.filters.append(FFmpegFilterVerticalFlip(**kwargs))
        return self

    @functools.wraps(FFmpegFilterCustom)
    def filter(self, **kwargs) -> Self:
        self.filters.append(FFmpegFilterCustom(**kwargs))
        return self

    # ---------------------------------------------------------------------------------------------|
    # Command building and running

    @property
    def command(self) -> List[str]:
        if (not self.inputs):
            raise ValueError("At least one input is required for FFmpeg")
        if (not self.outputs):
            raise ValueError("At least one output is required for FFmpeg")

        command = deque()

        def extend(*objects: Union[FFmpegModuleBase, Iterable[FFmpegModuleBase]]):
            for item in flatten(objects):
                if isinstance(item, FFmpegModuleBase):
                    command.extend(flatten(item.command()))
                else:
                    command.append(item)

        extend(shutil.which("ffmpeg"))
        extend("-threads", self.threads)
        extend("-hide_banner"*self.hide_banner)
        extend("-loglevel", self.loglevel)
        extend(("-hwaccel", self.hwaccel)*bool(self.hwaccel))
        extend(self.inputs)

        # Note: https://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
        for output in self.outputs:
            extend(self.video_codec)
            extend(("-vf", ",".join(map(str, self.filters)))*bool(self.filters))
            extend(self.audio_codec)
            extend(output)

        extend("-shortest"*self.shortest)
        return list(map(str, flatten(command)))

    def run(self, **kwargs) -> subprocess.CompletedProcess:
        return shell(self.command, **kwargs)

    def popen(self, **kwargs) -> subprocess.Popen:
        return shell(self.command, Popen=True, **kwargs)

    # ---------------------------------------------------------------------------------------------|
    # High level functions

    @staticmethod
    def install() -> None:
        if all(map(shutil.which, ("ffmpeg", "ffprobe"))):
            return

        if not BrokenPlatform.OnMacOS:
            log.info("FFmpeg wasn't found on System Path, will download a BtbN's Build")
            BrokenPath.get_external(''.join((
                "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/",
                "ffmpeg-master-latest-",
                BrokenPlatform.Name.replace("windows", "win"),
                BrokenPlatform.Architecture.replace("amd64", "64"),
                "-gpl.zip" if BrokenPlatform.OnWindows else "-gpl.tar.xz"
            )))
        else:
            log.info("FFmpeg wasn't found on System Path, will download a EverMeet's Build")
            for binary in ("ffmpeg", "ffprobe"):
                BrokenPath.get_external(f"https://evermeet.cx/ffmpeg/getrelease/{binary}/zip")

    @staticmethod
    @functools.lru_cache
    def get_resolution(path: Path, *, echo: bool=True) -> Optional[Tuple[int, int]]:
        """Get the resolution of a video in a smart way"""
        if not (path := Path(path).resolve()).exists():
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Video Resolution of ({path})", echo=echo)
        return PIL.Image.open(io.BytesIO(shell(
            shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error",
            "-i", path, "-vframes", "1", "-f", "image2pipe", "-",
            stdout=PIPE, echo=echo
        ).stdout), formats=["jpeg"]).size

    @staticmethod
    def get_frames(path: Path, *, skip: int=0, echo: bool=True) -> Optional[Iterable[numpy.ndarray]]:
        """Generator for every frame of the video as numpy arrays, FAST!"""
        if not (path := Path(path).resolve()).exists():
            return None
        BrokenFFmpeg.install()
        log.minor(f"Streaming Video Frames from file ({path})", echo=echo)
        (width, height) = BrokenFFmpeg.get_resolution(path)
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
    @functools.lru_cache
    def get_total_frames(path: Path, *, echo: bool=True) -> Optional[int]:
        """Count the total frames of a video by decode voiding and parsing stats output"""
        if not (path := Path(path).resolve()).exists():
            return None
        BrokenFFmpeg.install()
        with BrokenSpinner(log.minor(f"Getting total frames of video ({path}) by decoding every frame, might take a while..")):
            return int(re.compile(r"frame=\s*(\d+)").findall((
                BrokenFFmpeg(vsync="cfr")
                .input(path=path)
                .pipe_output(format="null")
            ).run(stderr=PIPE, echo=echo).stderr.decode())[-1])

    @staticmethod
    @functools.lru_cache
    def get_video_duration(path: Path, *, echo: bool=True) -> Optional[float]:
        if not (path := Path(path).resolve()).exists():
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
    def get_framerate(path: Path, *, precise: bool=False, echo: bool=True) -> Optional[float]:
        """Get the framerate of a video"""
        if not (path := Path(path).resolve()).exists():
            return None
        BrokenFFmpeg.install()
        log.minor(f"Getting Video Framerate of file ({path})", echo=echo)
        if precise:
            A = BrokenFFmpeg.get_total_frames(path, echo=False)
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

    @staticmethod
    @functools.lru_cache
    def get_audio_samplerate(path: Path, *, stream: int=0, echo: bool=True) -> Optional[float]:
        if not (path := Path(path).resolve()).exists():
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
        if not (path := Path(path).resolve()).exists():
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
        if not (path := Path(path).resolve()).exists():
            return
        try:
            generator = BrokenAudioReader(path=path, chunk=10).stream
            while next(generator) is not None: ...
        except StopIteration as result:
            return result.value

# -------------------------------------------------------------------------------------------------|
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
        self.path = BrokenPath(self.path)

        if (not self.path.exists()):
            return None

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
            .input(self.path)
            .audio_codec(self.format.value)
            .format(self.format.value.removeprefix("pcm_"))
            .no_video()
            .custom("-ar", self.samplerate)
            .custom("-ac", self.channels)
            .output("-")
        ).popen(stdout=PIPE, stderr=DEVNULL, echo=self.echo)

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
            length = nearest(length, self.bytes_per_sample, type=int)
            length = max(length, self.bytes_per_sample)
            data   = self._ffmpeg.stdout.read(length)
            if len(data) == 0: break

            # Increment precise time and read time
            yield numpy.frombuffer(data, dtype=self.dtype).reshape(-1, self.channels)
            self._read += len(data)

        return self.time
