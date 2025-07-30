from typing import Protocol, runtime_checkable
from functools import cached_property
from .mixins import Shape
from visuscript.primatives import Transform


@runtime_checkable
class CanBeDrawn(Protocol):
    extrusion: float

    def draw(self) -> str: ...


class HasShape(Protocol):
    @cached_property
    def shape(self) -> Shape: ...


class HasTransform(Protocol):
    @property
    def transform(self) -> Transform: ...
