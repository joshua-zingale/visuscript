from typing import Protocol
from .mixins import Shape
from visuscript.primatives import Transform


class Drawable(Protocol):
    def draw(self) -> str: ...

class HasShape(Protocol):
    @property
    def shape(self) -> Shape: ...

class HasTransform(Protocol):
    @property
    def transform(self) -> Transform: ...

