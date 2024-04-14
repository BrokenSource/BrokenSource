from numbers import Number
from typing import Tuple

from Broken import nearest


class BrokenResolution:

    @staticmethod
    def round(width: Number, height: Number) -> Tuple[int, int]:
        """FFmpeg likes multiples of 2, so let it be"""
        return (
            max(1, nearest(width,  multiple=2, type=int)),
            max(1, nearest(height, multiple=2, type=int))
        )

    @staticmethod
    def fitscar(
        w: int=None,
        h: int=None,
        s: float=1,
        ar: float=None
    ) -> Tuple[int, int]:
        """
        "(Fit), (Sc)ale, (A)spect (R)atio a (w)idth and (h)eight to a base resolution (x, y)"
        """
        if ar is None:
            return BrokenResolution.round(w, h)

        if (w is h is None):
            raise ValueError("Both w and h cannot be None")

        # Build from height or from width
        A = (w, w/ar)
        B = (h*ar, h)
        R = A if (A>B) else B
        R = map(int, (c*s for c in R))
        return BrokenResolution.round(*R)

    @staticmethod
    def fitscar_pro(
        x: int,
        y: int,
        w: int=None,
        h: int=None,
        s: float=1,
        ar: float=None
    ) -> Tuple[int, int]:
        """
        "(Fit), (Sc)ale, (A)spect (R)atio a (w)idth and (h)eight to a base resolution (x, y)"

        Given a base resolution (x, y), calculates the final resolution (w, h) such that:
        - When both (w, h) are given, forces the resolution to (w, h)
        - When either (w,) or (h,) are given, calculates the other value respecting the aspect ratio
        - When none (w, h) are given, returns the base resolution itself (x, y)
        - Post-multiplies the final resolution by a scale factor (s,)

        This is useful when calculating an upscaled or target resolution knowing only one component
        or applying an upscaling factor (s,) to the resolution.
        """
        ar = ar or (x/y)

        # Both are forced
        if (bool(w) == bool(h)):
            resolution = (
                int(s*(w or x)),
                int(s*(h or y))
            )
        else:
            resolution = (
                int(s*((h or 0)*ar or w)),
                int(s*((w or 0)/ar or h))
            )

        return BrokenResolution.round(*resolution)
