from visuscript.primatives import Vec2
from visuscript.primatives.mixins import (
    HierarchicalDrawable,
    GlobalShapeMixin,
)


class Pivot(GlobalShapeMixin, HierarchicalDrawable):
    """A Pivot is :class:`~visuscript.primatives.mixins.HierarchicalDrawable` with no display for itself.

    A Pivot can be used to construct more complex visual object by adding children."""

    def calculate_top_left(self):
        return Vec2(0, 0)

    def calculate_width(self) -> float:
        return 0.0

    def calculate_height(self) -> float:
        return 0.0

    def draw_self(self):
        return ""
