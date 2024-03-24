import sys
import time
import warnings
from math import pi as PI
from typing import TypeAlias
from typing import TypeVar
from typing import Union

import numpy
import PIL.Image

# Fix: typing.Self was implemented in Python 3.11
if sys.version_info < (3, 11):
    Self = TypeVar("Self")

# Ignore mostly NumPy warnings
warnings.filterwarnings('ignore')

# # Custom types and utilities
Image:     TypeAlias = PIL.Image.Image
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

# # Y'know what, I'm tired of numpy.* stuff. Let's fix that.

# Good to have
ndarray:    TypeAlias = numpy.ndarray

# Types
complex128: TypeAlias = numpy.complex128
c128:       TypeAlias = numpy.complex128
complex64:  TypeAlias = numpy.complex64
c64:        TypeAlias = numpy.complex64
float64:    TypeAlias = numpy.float64
f64:        TypeAlias = numpy.float64
float32:    TypeAlias = numpy.float32
f32:        TypeAlias = numpy.float32
int64:      TypeAlias = numpy.int64
i64:        TypeAlias = numpy.int64
int32:      TypeAlias = numpy.int32
i32:        TypeAlias = numpy.int32
int16:      TypeAlias = numpy.int16
i16:        TypeAlias = numpy.int16
int8:       TypeAlias = numpy.int8
i8:         TypeAlias = numpy.int8
uint64:     TypeAlias = numpy.uint64
u64:        TypeAlias = numpy.uint64
uint32:     TypeAlias = numpy.uint32
u32:        TypeAlias = numpy.uint32
uint16:     TypeAlias = numpy.uint16
u16:        TypeAlias = numpy.uint16
uint8:      TypeAlias = numpy.uint8
u8:         TypeAlias = numpy.uint8

# Recurring math constants
TAU     = (2 * PI)
SQRT2   = numpy.sqrt(2)
SQRT3   = numpy.sqrt(3)
SQRT_PI = numpy.sqrt(PI)

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
