import typing as t

from visuscript.primatives.primatives import PALETTE
from visuscript.primatives import Rgb, InterpolableFloat
from visuscript.lazy_object import Lazible


class RgbMixin:
    """Adds an :class:`~visuscript.Rgb` to this object."""

    def __init__(self):
        super().__init__()
        self._rgb: Rgb = PALETTE["off_white"]

    def set_rgb(self, rgb: Rgb.RgbLike) -> t.Self:
        """Sets this object's :class:`~visuscript.Rgb`"""
        self.rgb = rgb
        return self

    @property
    def rgb(self) -> Rgb:
        """This object's :class:`~visuscript.Rgb`"""
        return self._rgb

    @rgb.setter
    def rgb(self, value: Rgb.RgbLike):
            self._rgb = Rgb.construct(value)


class OpacityMixin:
    """Adds an opacity to this object"""

    def __init__(self):
        super().__init__()
        self._opacity: InterpolableFloat = InterpolableFloat(1)
        """This object's opacity."""

    def set_opacity(self, opacity: float) -> t.Self:
        """Sets this object's opacity."""
        self._opacity = InterpolableFloat(opacity)
        return self
    
    @property
    def opacity(self) -> InterpolableFloat:
        return self._opacity
    
    @opacity.setter
    def opacity(self, other: float):
        self._opacity = InterpolableFloat(other)


class Color(RgbMixin, OpacityMixin, Lazible):
    """Represents color-properties, including :class:`~visuscript.Rgb` and opacity,
    of another object."""

    ColorLike: t.TypeAlias = t.Union[Rgb.RgbLike, "Color"]

    def __init__(self, rgb: Rgb.RgbLike, opacity: float | None = None):
        super().__init__()

        self.rgb = t.cast(Rgb, rgb)

        if opacity is not None:
            self.opacity = t.cast(InterpolableFloat, opacity)

    @staticmethod
    def construct(other: ColorLike) -> "Color":
        if isinstance(other, Color):
            return Color(other.rgb, other.opacity)
        else:
            return Color(other, 1)

    def __str__(self) -> str:
        return f"Color(color={tuple(self.rgb)}, opacity={self.opacity}"
