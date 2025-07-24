from typing import Self, Union, TypeAlias


from visuscript.constants import PALETTE
from visuscript.primatives import Rgb
from visuscript.lazy_object import Lazible


    
class HasRgb:
    _RgbLike: TypeAlias = Union[Rgb, str, tuple[int,int,int]]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rgb: Rgb = PALETTE['off_white']

    def set_rgb(self, rgb: _RgbLike) -> Self:
        self.rgb = rgb
        return self

    @property
    def rgb(self) -> Rgb:
        return self._rgb

    @rgb.setter
    def rgb(self, value: _RgbLike):
        if isinstance(value, str):
            self._rgb = PALETTE[value]
        else:
            self._rgb = Rgb(*value)

class HasOpacity:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._opacity: float = 1

    @property
    def opacity(self) -> float:
        return self._opacity
    
    @opacity.setter
    def opacity(self, other: float):
        self._opacity = other

    def set_opacity(self, opacity: float) -> Self:
        self.opacity = opacity
        return self
    

class Color(HasRgb, HasOpacity, Lazible):
    def __init__(self, rgb: HasRgb._RgbLike | "Color", opacity: float | None = None, **kwargs):
        super().__init__(**kwargs)

        if isinstance(rgb, Color):
            self.rgb = rgb.rgb
            self.opacity = rgb.opacity

        if opacity is not None:
            self.opacity = opacity

    def __str__(self) -> str:
        return f"Color(color={tuple(self._rgb)}, opacity={self.opacity}"