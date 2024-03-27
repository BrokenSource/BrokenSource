"""
Absolutely clutch information for parsing MIDI files:
• https://web.archive.org/web/20141227205754/http://www.sonicspot.com:80/guide/midifiles.html
"""

from __future__ import annotations

import functools
import io
import math
from collections import deque
from pathlib import Path
from typing import Any, Deque, Iterable, Self, Tuple, TypeAlias, Union

from attr import Factory, define

from Broken.Types import Seconds

__all__ = ["Midi", "Events", "Note"]

# -------------------------------------------------------------------------------------------------|

PIANO_NOTES = "C C# D D# E F F# G G# A A# B".split()
MICROSECONDS_PER_MINUTE: int = 60_000_000
BIT_SHIFT_4: int = int(2**4)
BIT_SHIFT_7: int = int(2**7)
BIT_SHIFT_8: int = int(2**8)

Hertz: TypeAlias = float

# -------------------------------------------------------------------------------------------------|

@define
class Note:
    note:     int   = 60
    velocity: int   = 100
    channel:  int   = 0
    start:    float = 0
    end:      float = 0

    def __hash__(self):
        return hash((self.note, self.start, self.end, self.channel, self.velocity))

    def __eq__(self, other):
        return hash(self) == hash(other)

    # # Initialization

    @classmethod
    @functools.lru_cache
    def from_index(cls, note: int, **kwargs) -> Self:
        return cls(note=note, **kwargs)

    @classmethod
    @functools.lru_cache
    def from_name(cls, name: str, **kwargs) -> Self:
        return cls(note=Note.name_to_index(name), **kwargs)

    @classmethod
    @functools.lru_cache
    def from_frequency(cls, frequency: Hertz, **kwargs) -> Self:
        return cls(note=Note.frequency_to_index(frequency), **kwargs)

    @classmethod
    @functools.lru_cache
    def get(cls, object: Any, **kwargs) -> Self:
        if isinstance(object, Note):
            return object(**kwargs)
        elif isinstance(object, int):
            return cls.from_index(object, **kwargs)
        elif isinstance(object, str):
            return cls.from_name(object, **kwargs)
        elif isinstance(object, Hertz):
            return cls.from_frequency(object, **kwargs)
        return cls(**kwargs)

    # # Conversion

    @staticmethod
    @functools.lru_cache
    def index_to_name(index: int) -> str:
        return f"{PIANO_NOTES[index % 12]}{index//12 - 1}"

    @staticmethod
    @functools.lru_cache
    def index_to_frequency(index: int) -> Hertz:
        return 440 * 2**((index - 69)/12)

    @staticmethod
    @functools.lru_cache
    def name_to_index(name: str) -> int:
        note, octave = name[:-1].upper(), int(name[-1])
        return PIANO_NOTES.index(note) + 12*(octave + 1)

    @staticmethod
    @functools.lru_cache
    def name_to_frequency(name: str) -> Hertz:
        return Note.index_to_frequency(Note.name_to_index(name))

    @staticmethod
    @functools.lru_cache
    def frequency_to_index(frequency: Hertz) -> int:
        return round(12*math.log2(frequency/440) + 69)

    @staticmethod
    @functools.lru_cache
    def frequency_to_name(frequency: Hertz) -> str:
        return Note.index_to_name(Note.frequency_to_index(frequency))

    # # Utilities

    @property
    def frequency(self) -> Hertz:
        return Note.index_to_frequency(self.note)

    @frequency.setter
    def frequency(self, value: Hertz):
        self.note = Note.frequency_to_index(value)

    @property
    def name(self) -> str:
        return Note.index_to_name(self.note)

    @name.setter
    def name(self, value: str):
        self.note = Note.name_to_index(value)

    # Black and White

    def is_white(note: int) -> bool:
        return (note % 12) in {0, 2, 4, 5, 7, 9, 11}

    def is_black(note: int) -> bool:
        return (note % 12) in {1, 3, 6, 8, 10}

    @property
    def white(self) -> bool:
        return Note.is_white(self.note)

    @property
    def black(self) -> bool:
        return Note.is_black(self.note)

    # Temporal

    @property
    def duration(self):
        return self.end - self.start

    @duration.setter
    def duration(self, value: Seconds):
        self.end = self.start + value

# -------------------------------------------------------------------------------------------------|

@define
class BaseEvent:
    time: float

class Events:

    # # Meta events

    @define
    class SequenceNumber(BaseEvent):
        value: int

    @define
    class Text(BaseEvent):
        text: str

    @define
    class Copyright(BaseEvent):
        text: str

    @define
    class TrackName(BaseEvent):
        text: str

    @define
    class InstrumentName(BaseEvent):
        text: str

    @define
    class Lyrics(BaseEvent):
        text: str

    @define
    class Marker(BaseEvent):
        text: str

    @define
    class CuePoint(BaseEvent):
        text: str

    @define
    class MidiChannelPrefix(BaseEvent):
        channel: int

    @define
    class EndTrack:
        ...

    @define
    class SetTempo(BaseEvent):
        mpqn: int
        """Microseconds per Quarter Note"""

        @property
        def bpm(self) -> float:
            return MICROSECONDS_PER_MINUTE / self.mpqn

    @define
    class SMTPEOffset(BaseEvent):
        hours: int
        minutes: int
        seconds: int
        frames: int
        subframes: int

    @define
    class TimeSignature(BaseEvent):
        numerator: int
        denominator: int
        metronome: int
        thirty_seconds: int

    @define
    class KeySignature(BaseEvent):
        key: int
        scale: int

        @property
        def major(self) -> bool:
            return (self.scale == 0)

        @property
        def minor(self) -> bool:
            return (self.scale == 1)

    @define
    class SequencerSpecific(BaseEvent):
        text: str

    # # Midi events

    Note = Note

    @define
    class Pressure(BaseEvent):
        note: int
        pressure: int

    @define
    class Controller(BaseEvent):
        controller: int
        value: int

        @property
        def bank_select(self) -> int:
            return (self.value == 0x00)

        @property
        def modulation(self) -> int:
            return (self.value == 0x01)

        ... # Todo

    @define
    class Program(BaseEvent):
        program: int

    @define
    class ChannelPressure(BaseEvent):
        pressure: int

    @define
    class PitchBend(BaseEvent):
        value: int

# -------------------------------------------------------------------------------------------------|

Tempo: TypeAlias = float

@define
class Midi:
    format: int = 0
    tracks: int = 0
    _tempos: Deque[Tuple[Seconds, Tempo]] = Factory(deque)

    @property
    def tempos(self) -> Deque[Tuple[Seconds, Tempo]]:
        if len(self._tempos) == 0:
            return deque(((0, 120),))
        return self._tempos

    def _tempo(self, time: Seconds) -> Tuple[Seconds, Tempo]:
        """Returns the last tempo change not greater than this time and the next tempo change"""

        for i, (when, _) in enumerate(self._tempos):

            # Reached end of list, yield last tempo and only change at "infinity"
            # ie. listen for new tempos but do nothing
            if (i == len(self.tempos) - 1):
                return (math.inf, self._tempos[-1][1])

            # Found a tempo change that's one index greater than the current one
            if (time <= when):
                return (when, self._tempos[i-1][1])

        # On an empty tempos list, keep listening and default to 120 BPM
        return (math.inf, 120)

    def load(self, file: Path) -> Iterable[Events]:
        """
        Warn: Only files with all Tempo changes on the first track will be precisely parsed
        """

        # Reading to a bytearray, memoryview is slower than buffered io
        stream = io.BytesIO(Path(file).read_bytes())
        _end = len(stream.getbuffer())
        position = 0

        # --------------------------------------|

        # Note: We REALLY want to avoid self or lambdas, as these methods
        # Note: are called SO MANY TIMES that it's not even funny

        # Fixme: Slowest bottleneck, I tried
        def read_variable_length() -> int:
            nonlocal position
            value = 0
            while True:
                position += 1
                byte = int.from_bytes(stream.read(1))
                value = (value * BIT_SHIFT_7) | (byte & 0x7F)
                if (byte & 0x80) == 0:
                    return value

        def read_string() -> Union[str, bytes]:
            nonlocal position
            length = int.from_bytes(stream.read(1))
            position += 1 + length
            return stream.read(length).decode(encoding="utf-8", errors="replace")

        # --------------------------------------|

        # The chunk id start must be MThd (0x4D546864)
        if (stream.read(4) != b"MThd"):
            raise Exception("Invalid MIDI file")
        position += 4

        # Skip chunk size as it's always 6
        stream.read(4)
        position += 4

        # Read basic metadata
        self.format = int.from_bytes(stream.read(2))
        self.tracks = int.from_bytes(stream.read(2))
        self.tempos.clear()
        position += 4

        if (self.format == 0) and (self.tracks > 1):
            raise Exception("Midi format 0 with more than one track")

        # Read the time division
        time_division = int.from_bytes(stream.read(2))
        position += 2

        # Top bit is zero, then it's ticks per beat
        if (time_division & 0x8000) == 0:
            ticks_per_beat = (time_division & 0x7FFF)

        # Top bit is one, then it's frames per second
        else:
            raise NotImplementedError("Frames per Second (SMPTE) Midi time division isn't implemented")
            _frames_per_second = (time_division & 0x7F00) >> 8
            _ticks_per_frame = (time_division & 0x00FF)

        # --------------------------------------|

        # Read the tracks
        for track in range(self.tracks):
            chunk_id = stream.read(4)
            position += 4

            # Premature end of file or invalid start of track
            if (chunk_id != b"MTrk"):
                raise Exception(f"Invalid MIDI file, expected ('MTrk'=0x4D546864) but got (0x{chunk_id.hex()})")
            elif (chunk_id == b""):
                break

            # Trackers
            pressing = dict()
            time: float = 0

            # Assume 120 BPM if no tempo is set
            changes, tempo = self._tempo(time)
            print("• New: Changed to", tempo, "at", time, "next on", changes)

            # Multiply by delta time to get seconds
            seconds_per_tick = ((60/tempo)/ticks_per_beat)

            # Read the chunk size of this track
            chunk_size = int.from_bytes(stream.read(4))
            position += 4
            chunk_end = position + chunk_size

            # Control events: Constant size two bytes as arguments
            while (position < chunk_end):
                delta = read_variable_length()
                byte  = int.from_bytes(stream.read(1))
                position += 1

                # Maybe reached EOF
                if byte == b"":
                    break

                # Control events
                elif (0x80 <= byte <= 0xEF):
                    type    = (byte & 0xF0)
                    channel = (byte & 0x0F)
                    word    = int.from_bytes(stream.read(2))
                    options = ((word & 0xFF00)//BIT_SHIFT_8, (word & 0x00FF))
                    position += 2

                    # Note ON and OFF events - Yield full duration notes
                    if (off := (type == 0x80)) or (type == 0x90):
                        time += (delta * seconds_per_tick)

                        # Change tempo if needed
                        if (changes < time):
                            changes, tempo = self._tempo(time)
                            print("• Inner: Changed to", tempo, "at", time, "next on", changes)

                        note, velocity = options

                        # If there was a note playing or same-note on, yield it
                        if (other := pressing.get(channel, {}).pop(note, None)):
                            other.end = time
                            yield other

                        # Insert a partial note on note_on
                        if not (off or (velocity==0)):
                            # print("Note", note)
                            pressing.setdefault(channel, {})[note] = Events.Note(
                                note=note,
                                velocity=velocity,
                                channel=channel,
                                start=time,
                            )

                    elif (type == 0xA0):
                        pressure, note = options
                        yield Events.Pressure(
                            note=note,
                            pressure=pressure,
                            time=time,
                        )

                    elif (type == 0xB0):
                        yield Events.Controller(
                            controller=options[0],
                            value=options[1],
                            time=time,
                        )

                    elif (type == 0xC0):
                        yield Events.Program(
                            program=options[0],
                            time=time,
                        )

                    elif (type == 0xD0):
                        yield Events.ChannelPressure(
                            pressure=options[0],
                            time=time,
                        )

                    elif (type == 0xE0):
                        yield Events.PitchBend(
                            value=options[0] + (options[1] * BIT_SHIFT_7),
                            time=time,
                        )

                # Meta events: Variable content length based on type
                elif (byte == 0xFF):
                    type = int.from_bytes(stream.read(1))
                    position += 1

                    if (type == 0x00):
                        yield Events.SequenceNumber(
                            value=int.from_bytes(stream.read(2)),
                            time=time,
                        )
                        position += 2

                    elif (type == 0x01):
                        yield Events.Text(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x02):
                        yield Events.Copyright(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x03):
                        yield Events.TrackName(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x04):
                        yield Events.InstrumentName(
                            text=read_string(),
                            time=time,
                        )

                        yield Events.Lyrics(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x06):
                        yield Events.Marker(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x07):
                        yield Events.CuePoint(
                            text=read_string(),
                            time=time,
                        )

                    elif (type == 0x20):
                        yield Events.MidiChannelPrefix(
                            channel=int.from_bytes(stream.read(1)),
                            time=time,
                        )
                        position += 1

                    elif (type == 0x2F):
                        yield Events.EndTrack()
                        stream.read(1)
                        position += 1
                        break

                    elif (type == 0x51):
                        mpqn  = int.from_bytes(stream.read(3))
                        tempo = (MICROSECONDS_PER_MINUTE/mpqn)
                        seconds_per_tick = ((60/tempo)/ticks_per_beat)
                        self.tempos.append((time, tempo))
                        yield Events.SetTempo(mpqn=mpqn, time=time)
                        position += 3
                        # print(f"Tempo: {tempo:.2f} ({time=})")

                    elif (type == 0x54):
                        yield Events.SMTPEOffset(
                            hours=    int.from_bytes(stream.read(1)),
                            minutes=  int.from_bytes(stream.read(1)),
                            seconds=  int.from_bytes(stream.read(1)),
                            frames=   int.from_bytes(stream.read(1)),
                            subframes=int.from_bytes(stream.read(1)),
                            time=time,
                        )
                        position += 5

                    elif (type == 0x58):
                        yield (_signature := Events.TimeSignature(
                            numerator=     int.from_bytes(stream.read(1)),
                            denominator=   int.from_bytes(stream.read(1)),
                            metronome=     int.from_bytes(stream.read(1)),
                            thirty_seconds=int.from_bytes(stream.read(1)),
                            time=time,
                        ))
                        # tempo = (_signature.thirty_seconds)*(_signature.numerator)
                        position += 4

                    elif (type == 0x59):
                        yield Events.KeySignature(
                            key=  int.from_bytes(stream.read(1)),
                            scale=int.from_bytes(stream.read(1)),
                            time= time,
                        )
                        position += 2

                    elif (type == 0x7F):
                        yield Events.SequencerSpecific(
                            text=read_variable_length(),
                            time=time,
                        )
