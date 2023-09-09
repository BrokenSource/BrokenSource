from . import *


@attrs.define
class BrokenNote:
    note:     int   = 60
    start:    float = 0
    end:      float = 0
    velocity: float = 100

    _PIANO_NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

    # Initialization functions

    def from_index(note: int, *args, **kwargs) -> Self:
        """Build a BrokenNote from a MIDI note index (eg 60, 69)"""
        return BrokenNote(note=note, *args, **kwargs)

    def from_name(name: str, *args, **kwargs) -> Self:
        """Build a BrokenNote from a key name (eg C4, A4)"""
        return BrokenNote.from_index(BrokenNote.name_to_index(name), *args, **kwargs)

    def from_frequency(frequency: float, *args, **kwargs) -> Self:
        """Build a BrokenNote from a frequency in Hz (eg 261.63, 440)"""
        return BrokenNote.from_index(BrokenNote.frequency_to_index(frequency), *args, **kwargs)

    # # Conversions

    # We map (index) -> {name, frequency} and the opposite first (they are own implemntation)

    def index_to_name(note: int) -> str:
        """Convert a MIDI note index to a key name, eg (60 -> C4) (69 -> A4)"""
        return BrokenNote._PIANO_NOTES[note % 12] + str(note // 12 - 1)

    def name_to_index(key: str) -> int:
        """Convert a key name to a MIDI note index, eg (C4 -> 60) (A4 -> 69) (A10)"""
        return BrokenNote._PIANO_NOTES.index(key[:-1]) + (int(key[-1]) + 1) * 12

    def index_to_frequency(note: int) -> float:
        """Convert a MIDI note index to a frequency, eg (60 -> 261.63) (69 -> 440)"""
        return 440 * 2**((note - 69)/12)

    def frequency_to_index(frequency: float) -> int:
        """Convert a frequency to a MIDI note index, eg (261.63 -> 60) (440 -> 69)"""
        return round(12 * math.log2(frequency / 440) + 69)

    # Then build other conversions that are "high level"

    def name_to_frequency(key: str) -> float:
        """Convert a key name to a frequency, eg (C4 -> 261.63) (A4 -> 440)"""
        return BrokenNote.index_to_frequency(BrokenNote.key_to_index(key))

    def frequency_to_name(frequency: float) -> str:
        """Convert a frequency to a key name, eg (261.63 -> C4) (440 -> A4)"""
        return BrokenNote.index_to_name(BrokenNote.frequency_to_index(frequency))

    # # Properties

    def is_white(note: int) -> bool:
        """Is this note a white key on the piano?"""
        return "#" in BrokenNote.index_to_name(note)

    def is_black(note: int) -> bool:
        """Is this note a black key on the piano?"""
        return not BrokenNote.is_white(note)

    # # Self functions

    @property
    def black(self) -> bool:
        """Is this note a black key on the piano?"""
        return BrokenNote.is_black(self.note)

    @property
    def white(self) -> bool:
        """Is this note a white key on the piano?"""
        return BrokenNote.is_white(self.note)

    @property
    def name(self) -> str:
        """Get the name of this note, eg C4"""
        return BrokenNote.index_to_name(self.note)

    @property
    def frequency(self) -> float:
        """Get the frequency of this note, eg 261.63"""
        return BrokenNote.index_to_frequency(self.note)


@attrs.define
class BrokenPianoRoll:
    notes: intervaltree.IntervalTree = attrs.Factory(intervaltree.IntervalTree)

    def add_notes(self, *notes: Union[BrokenNote, list[BrokenNote]]):
        """Add notes to the piano roll"""
        notes = BrokenUtils.flatten(notes)
        for note in notes:
            self.notes.addi(note.start, note.end, note)

    def get_notes_between(self, start: float, end: float) -> list[BrokenNote]:
        """Get all notes playing between two times"""
        return list(self.notes[start:end])

    def get_notes_at(self, time: float) -> list[BrokenNote]:
        """Get all notes playing at a givenl time"""
        return self.get_notes_between(time, time)
