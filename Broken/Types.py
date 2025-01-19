import warnings
from math import pi as PI
from pathlib import Path
from typing import TypeAlias, Union

from pydantic import HttpUrl

PydanticImage = Union[str, Path, HttpUrl]

# Ignore mostly NumPy warnings
warnings.filterwarnings("ignore")

# Custom types and utilities
Unchanged: TypeAlias = None
Channels:  TypeAlias = int

# Units
Seconds: TypeAlias = float
Minutes: TypeAlias = float
Hours:   TypeAlias = float
Hertz:   TypeAlias = float
Samples: TypeAlias = int
Bytes:   TypeAlias = int
Degrees: TypeAlias = float
Radians: TypeAlias = float
BPM:     TypeAlias = float
Pixel:   TypeAlias = int

# Recurring math constants
TAU:     float = (2*PI)
SQRT2:   float = (2**0.5)
SQRT3:   float = (3**0.5)
SQRT5:   float = (5**0.5)
SQRT_PI: float = (PI**0.5)

# Recurring computing constants
KB:  int = (1000)
MB:  int = (KB*1000)
GB:  int = (MB*1000)
TB:  int = (GB*1000)
KiB: int = (1024)
MiB: int = (KiB*1024)
GiB: int = (MiB*1024)
TiB: int = (GiB*1024)

class FileExtensions:
    Audio:     set[str] = {".wav", ".ogg", ".flac", ".mp3"}
    Image:     set[str] = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
    Video:     set[str] = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".wmv", ".flv"}
    Font:      set[str] = {".ttf", ".otf", ".woff", ".woff2"}
    Midi:      set[str] = {".mid", ".midi"}
    Soundfont: set[str] = {".sf2", ".sf3"}
