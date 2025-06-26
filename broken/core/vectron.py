from typing import Optional, Union

import numpy as np
import xxhash
from PIL.Image import Image as ImageType


class Vectron:

    def image_hash(image: Union[ImageType, np.ndarray]) -> int:
        return xxhash.xxh3_64_intdigest(image.tobytes())

    def normalize(
        array: np.ndarray,
        dtype: np.dtype=np.float32,
        min: Optional[float]=None,
        max: Optional[float]=None,
    ) -> np.ndarray:

        # Get the dtype information
        info = (np.iinfo(dtype) if np.issubdtype(dtype, np.integer) else np.finfo(dtype))

        # Optionally override target dtype min and max
        min = (info.min if (min is None) else min)
        max = (info.max if (max is None) else max)

        # Work with float64 as array might be low precision
        return np.interp(
            x=array.astype(np.float64),
            xp=(np.min(array), np.max(array)),
            fp=(min, max),
        ).astype(dtype)

    def lstq_masked(
        base: np.ndarray,
        fill: np.ndarray,
        mask: np.ndarray=None,
    ) -> tuple[float, float]:
        """
        Find the linear system coefficients (A, B) that minimizes MSE(base, A*(fill + B)) for the
        masked pixels, returns
        """

        # Use whole image by default
        if mask is None:
            mask = np.ones_like(base, dtype=bool)

        # Make linear, apply mask
        mask = mask.ravel()
        x = base.ravel()[mask]
        y = fill.ravel()[mask]

        # Fit least squares linear regression
        A = np.column_stack((x, np.ones_like(x)))
        (a, b), *_ = np.linalg.lstsq(A, y)

        # Return opposite effects
        return (1/a), (-b)

    def limited_ratio(
        number: Optional[float], *,
        upper: float=None
    ) -> Optional[tuple[int, int]]:
        """Same as Number.as_integer_ratio but with an optional upper limit and optional return"""
        if (number is None):
            return None

        num, den = number.as_integer_ratio()

        if upper and ((den > upper) or (num > upper)):
            normalize = upper/min(num, den)
            num *= normalize
            den *= normalize

        return (int(num), int(den))

