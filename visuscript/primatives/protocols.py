"""Contains Protocols used throughout Visuscript's interfaces."""


import typing as t

from .primatives import Transform, Rgb, InterpolableFloat
from .shape import Shape


@t.runtime_checkable
class CanBeDrawn(t.Protocol):
    @property
    def extrusion(self) -> float: ...

    @extrusion.setter
    def extrusion(self, other: float): ...

    def draw(self) -> str: ...


class CanBeLazed(t.Protocol):
    @property
    def lazy(self) -> t.Self:
        """This should actually return a Lazy version of the class.
        The "Self" type hint is to make the type checker happy."""
        ...


class HasShape(t.Protocol):
    @property
    def shape(self) -> Shape: ...


class HasTransform(t.Protocol):
    @property
    def transform(self) -> Transform: ...

    @transform.setter
    def transform(self, other: Transform) -> None: ...


class HasOpacity(t.Protocol):
    @property
    def opacity(self) -> InterpolableFloat: ...

    @opacity.setter
    def opacity(self, other: float): ...


class HasRgb(t.Protocol):
    @property
    def rgb(self) -> Rgb: ...

    @rgb.setter
    def rgb(self, other: Rgb): ...