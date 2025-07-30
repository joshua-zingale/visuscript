from typing import Protocol
from functools import cached_property
from .mixins import Shape
from visuscript.primatives import Transform


class CanBeDrawn(Protocol):
    def draw(self) -> str: ...


class HasShape(Protocol):
    @cached_property
    def shape(self) -> Shape: ...


class HasTransform(Protocol):
    @property
    def transform(self) -> Transform: ...
