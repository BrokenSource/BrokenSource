import math
from numbers import Number
from typing import Tuple

from loguru import logger as log

from Broken import nearest


class BrokenResolution:

    @staticmethod
    def round_component(component: Number, *, scale: Number=1) -> int:
        return max(1, nearest(scale*component, multiple=2, type=int, operator=round))

    @staticmethod
    def round_resolution(width: Number, height: Number, *, scale: Number=1) -> Tuple[int, int]:
        """FFmpeg likes multiples of 2, so let's make it happy"""
        return tuple(map(BrokenResolution.round_component, (scale*width, scale*height)))

    @staticmethod
    def fit(
        old: Tuple[int, int]=None,
        new: Tuple[int, int]=None,
        max: Tuple[int, int]=None,
        aspect_ratio: float=None,
    ) -> Tuple[int, int]:
        """Fit, Scale and optionally force Aspect Ratio on a base to a (un)limited target resolution

        This method solves the following problem:
            "A window is at some initial size (ow, oh) and a resize was asked to (nw, nh); what
            final resolution the window should be, optionally enforcing an aspect ratio (ar),
            and limited by the monitor resolution (mw, mh)?"

        To which, the behavior is as follows in the two branches:
            No aspect ratio (ar=None) is send:
                - Returns the original resolution overrided by any new (nw, nh)

            Aspect ratio (ar!=None) is send:
                - If any of the new (nw, nh) is missing, find the other based on the aspect ratio
                - Else, prioritize width changes, and downscale/upscale accordingly;
                - Post-limits resolution to (mw, mh) by multiplying both components to max fit it

        Notes
        -----
            - The resolution is rounded to the nearest multiple of 2, so FFmpeg is happy

        Parameters
        ----------
        old
            Old resolution
        new
            New resolution
        max
            Maximum resolution
        ar
            Force aspect ratio, if any

        Returns
        -------
        (int, int)
            The new best-fit width and height
        """

        # Unpack
        old_width, old_height = (old or (None, None))
        new_width, new_height = (new or (None, None))
        max_width, max_height = (max or (None, None))

        log.debug(f"Fit resolution: ({old_width}, {old_height}) -> ({new_width}, {new_height})^({max_width}, {max_height}), AR {aspect_ratio}")

        # Force or keep either component
        (width, height) = ((new_width or old_width), (new_height or old_height))

        if (aspect_ratio is None):
            pass

        else:
            # Build from width (W) or from height (H)
            from_width  = (width, width/aspect_ratio)
            from_height = (height*aspect_ratio, height)

            # Pick the non missing component's
            if (new_height is None):
                (width, height) = from_width
            elif (new_width is None):
                (width, height) = from_height

            # Based on upscale or downscale
            elif (new_width != old_width):
                (width, height) = from_width
            elif (new_height != old_height):
                (width, height) = from_height

        # Limit the resolution to (mw, mh) bounding box and keep aspect ratio
        # - The idea is to find the maximum reduce factor for either component so it normalizes
        #   to the respective (mw, mh), and apply it to both components to scale down
        reduce = __builtins__["max"](
            width/(min(width, max_width or math.inf) or 1),
            height/(min(height, max_height or math.inf) or 1)
        ) or 1

        return BrokenResolution.round_resolution(width/reduce, height/reduce)
