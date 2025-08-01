from typing import Self, Union, TypeAlias, cast


from visuscript.constants import PALETTE
from visuscript.primatives.primatives import Rgb
from visuscript.lazy_object import Lazible


class RgbMixin:
    def __init__(self):
        super().__init__()
        self._rgb: Rgb = PALETTE["off_white"]

    def set_rgb(self, rgb: Rgb._RgbLike) -> Self:
        self.rgb = rgb
        return self

    @property
    def rgb(self) -> Rgb:
        return self._rgb

    @rgb.setter
    def rgb(self, value: Rgb._RgbLike):
        if isinstance(value, str):
            self._rgb = PALETTE[value]
        else:
            self._rgb = Rgb(*value)


class OpacityMixin:
    def __init__(self):
        super().__init__()
        self.opacity: float = 1

    def set_opacity(self, opacity: float) -> Self:
        self.opacity = opacity
        return self


class Color(RgbMixin, OpacityMixin, Lazible):
    _ColorLike: TypeAlias = Union[Rgb._RgbLike, "Color"]

    def __init__(self, rgb: Rgb._RgbLike, opacity: float | None = None):
        super().__init__()

        self.rgb = cast(Rgb, rgb)  # The setter in RgbMixin ensures this property is Rgb

        if opacity is not None:
            self.opacity = opacity

    @staticmethod
    def construct(other: _ColorLike) -> "Color":
        if isinstance(other, Color):
            return Color(other.rgb, other.opacity)
        else:
            return Color(other, 1)

    def __str__(self) -> str:
        return f"Color(color={tuple(self.rgb)}, opacity={self.opacity}"
