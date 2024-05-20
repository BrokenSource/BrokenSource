import sys
import time
from threading import Thread
from typing import List, Self, Union

from attr import define


class Spinners:
    Simple: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

@define
class BrokenSpinner:

    text: str = ""
    """The text to display next to the spinner. Also defines if the spinner is active"""

    spinner: Union[str, List[str]] = Spinners.Simple
    """A Sequence or list of printable objects to use as the spinner"""

    framerate: float = 10
    """Update rate of the spinner"""

    _index: int = 0
    """Current index of the spinner"""

    @property
    def frametime(self) -> float:
        return 1/self.framerate

    # Singleton to save spawning multiple threads
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __attrs_post_init__(self):
        Thread(target=self._worker, daemon=True).start()

    def start(self, text: str) -> Self:
        self.text = text
        return self

    def stop(self) -> Self:
        self.text = ""
        while self._spinning:
            time.sleep(0.01)
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, a, b, c) -> None:
        self.stop()

    def _write(self, text: str="") -> None:
        """Clean current stdout line and flush write new text"""
        sys.stdout.write(f"\r\033[K{text}")
        sys.stdout.flush()

    _spinning: bool = False

    def _worker(self):
        while True:

            # Get and write next character
            while bool(self.text):
                self._spinning = True
                self._index += 1
                char = self.spinner[self._index % len(self.spinner)]
                self._write(f"{char} {self.text}")

                # Sleep for a frametime, but break if there's no text
                start = time.perf_counter()

                while bool(self.text) and (time.perf_counter() - start < self.frametime):
                    time.sleep(0.01/self.framerate)

            # Cleanup
            if self._spinning:
                self._write()

            self._spinning = False
            time.sleep(0.01)
