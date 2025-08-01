from visuscript.primatives import Vec2
from visuscript.primatives.mixins import (
    HierarchicalDrawable,
    GlobalShapeMixin,
    AnchorMixin,
    FillMixin,
    StrokeMixin,
    OpacityMixin,
)

from visuscript.segment import Path
from visuscript.constants import Anchor
from .drawing import Drawing


class Rect(Drawing):
    """A Rectangle."""

    def __init__(self, width: float, height: float | None = None):
        height = height if height is not None else width
        super().__init__(Path().l(width, 0).l(0, height).l(-width, 0).Z())
        self.set_anchor(Anchor.CENTER)


class Circle(
    GlobalShapeMixin,
    HierarchicalDrawable,
    FillMixin,
    StrokeMixin,
    AnchorMixin,
    OpacityMixin,
):
    """A Circle."""

    def __init__(self, radius: float):
        super().__init__()
        self.radius = radius

    def calculate_top_left(self):
        return Vec2(-self.radius, -self.radius)

    def calculate_width(self):
        return self.radius * 2

    def calculate_height(self):
        return self.radius * 2

    def calculate_circumscribed_radius(self):
        return self.radius

    def draw_self(self):
        x, y = self.anchor_offset
        return f"""<circle \
cx="{x}" \
cy="{y}" \
r="{self.radius}" \
transform="{self.global_transform.svg_transform}" \
stroke="{self.stroke.rgb}" \
stroke-opacity="{self.stroke.opacity}" \
stroke-width="{self.stroke_width}" \
fill="{self.fill.rgb}" \
fill-opacity="{self.fill.opacity}" \
opacity="{self.global_opacity}"\
/>"""
