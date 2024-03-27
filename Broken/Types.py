import sys
import time
import warnings
from math import pi as PI
from typing import TypeAlias, TypeVar, Union

# Fix: typing.Self was implemented in Python 3.11
if sys.version_info < (3, 11):
    Self = TypeVar("Self")

# Ignore mostly NumPy warnings
warnings.filterwarnings('ignore')

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
Degrees:   TypeAlias = float
Radians:   TypeAlias = float
BPM:       TypeAlias = float
Pixel:     TypeAlias = int

# Recurring math constants
TAU     = (2 * PI)
SQRT2   = (2**0.5)
SQRT3   = (3**0.5)
SQRT_PI = (PI**0.5)

# File extensions. {} are sets !
AUDIO_EXTENSIONS = {".wav", ".ogg", ".flac", ".mp3"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
FONTS_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".wmv", ".flv"}
FONTS_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
MIDI_EXTENSIONS  = {".mid", ".midi"}
SOUNDFONTS_EXTENSIONS = {".sf2", ".sf3"}

# Count time since.. the big bang with the bang counter. Shebang #!
# Serious note, a Decoupled client starts at the Python's time origin, others on OS perf counter
BIG_BANG: Seconds = time.perf_counter()
time.bang_counter = (lambda: time.perf_counter() - BIG_BANG)
