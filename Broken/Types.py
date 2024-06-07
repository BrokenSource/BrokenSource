import warnings
from math import pi as PI
from typing import TypeAlias, Union

# Ignore mostly NumPy warnings
warnings.filterwarnings("ignore")

# # Custom types and utilities
Unchanged: TypeAlias = None
URL:       TypeAlias = str
Option               = Union
Range:     TypeAlias = range
Channels:  TypeAlias = int

# Units
Seconds:   TypeAlias = float
Minutes:   TypeAlias = float
Hours:     TypeAlias = float
Hertz:     TypeAlias = float
Samples:   TypeAlias = int
Bytes:     TypeAlias = int
Degrees:   TypeAlias = float
Radians:   TypeAlias = float
BPM:       TypeAlias = float
Pixel:     TypeAlias = int

# Recurring math constants
TAU     = (2*PI)
SQRT2   = (2**0.5)
SQRT3   = (3**0.5)
SQRT_PI = (PI**0.5)

# File extensions. {} are sets !
class FileExtensions:
    Audio = {".wav", ".ogg", ".flac", ".mp3"}
    Image = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
    Video = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".wmv", ".flv"}
    Font  = {".ttf", ".otf", ".woff", ".woff2"}
    Midi  = {".mid", ".midi"}
    Soundfont = {".sf2", ".sf3"}
