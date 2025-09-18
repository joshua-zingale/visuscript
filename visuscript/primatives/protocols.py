from typing import Protocol, runtime_checkable
from functools import cached_property
from .mixins import Shape
from visuscript.primatives import Transform, Rgb
from visuscript.primatives import Color


@runtime_checkable
class CanBeDrawn(Protocol):
    @property
    def extrusion(self) -> float: ...

    @extrusion.setter
    def extrusion(self, other: float): ...

    def draw(self) -> str: ...


class HasShape(Protocol):
    @cached_property
    def shape(self) -> Shape: ...


class HasTransform(Protocol):
    @property
    def transform(self) -> Transform: ...


class HasOpacity(Protocol):
    @property
    def opacity(self) -> float: ...

    @opacity.setter
    def opacity(self, other: float): ...


class HasRgb(Protocol):
    @property
    def rgb(self) -> Rgb: ...

    @rgb.setter
    def rgb(self, other: Rgb): ...

class HasFill(Protocol):
    @property
    def fill(self) -> Color: ...

    @fill.setter
    def fill(self, other: Color): ...

