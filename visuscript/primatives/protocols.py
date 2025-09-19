from typing import Protocol, runtime_checkable
from .mixins import Shape
from visuscript.primatives import Transform, Rgb
from visuscript.primatives import Color
from typing import Self


@runtime_checkable
class CanBeDrawn(Protocol):
    @property
    def extrusion(self) -> float: ...

    @extrusion.setter
    def extrusion(self, other: float): ...

    def draw(self) -> str: ...


class CanBeLazed(Protocol):
    @property
    def lazy(self) -> Self: ...

    """This should actually return a Lazy version of the class.
    
    The "Self" type hint is to make the type checker happy."""


class HasShape(Protocol):
    @property
    def shape(self) -> Shape: ...


class HasTransform(Protocol):
    @property
    def transform(self) -> Transform: ...

    @transform.setter
    def transform(self, other: Transform) -> None: ...


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
