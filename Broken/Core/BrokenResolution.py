from numbers import Number
from typing import Tuple

from Broken import nearest


class BrokenResolution:

    @staticmethod
    def round_resolution(width: Number, height: Number) -> Tuple[int, int]:
        """FFmpeg likes multiples of 2, so let it be"""
        return (
            nearest(width,  multiple=2, type=int),
            nearest(height, multiple=2, type=int)
        )

    @staticmethod
    def fitscar(
        x: int,
        y: int,
        w: int=None,
        h: int=None,
        s: float=1
    ) -> Tuple[int, int]:
        """
        "(Fit), (Sc)ale, (A)spect (R)atio"

        Given a base resolution (x, y), calculates the final resolution (w, h) such that:
        - When both (w, h) are given, the resolution is forced to it
        - When either (w,) or (h,) are given, calculates the other value respecting the aspect ratio
        - When none (w, h) are given, returns the base resolution itself (x, y)
        - Post-multiplies the final resolution by a scale factor (s,)

        This is useful when calculating an upscaled or target resolution knowing only one component
        or applying an upscaling factor (s,) to the resolution.
        """
        ar = (x/y)

        # Both are forced
        if (bool(w) == bool(h)):
            return (
                int(s*(w or x)),
                int(s*(h or y))
            )
        else:
            return (
                int(s*((h or 0)*ar or w)),
                int(s*((w or 0)/ar or h))
            )
