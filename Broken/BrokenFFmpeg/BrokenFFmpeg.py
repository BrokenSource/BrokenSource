from __future__ import annotations


@define
class FFmpegResolution:
    width:  int = field(converter=int)
    height: int = field(converter=int)

    @width.validator
    @height.validator
    def check(self, attribute: str, value: int) -> None:
        if value <= 0:
            raise ValueError(f"{attribute} must be a natural number")

    def __mul__(self, other: float) -> FFmpegResolution:
        self.width  *= other
        self.height *= other
        return self

    def __truediv__(self, other: float) -> FFmpegResolution:
        self.width  /= other
        self.height /= other
        return self

    def aspect_ratio(self) -> float:
        return self.width / self.height



@define
class BrokenFFmpeg:
    ...