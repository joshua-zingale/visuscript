from visuscript.segment import Path
from visuscript.mixins import (
    HierarchicalDrawable,
    GlobalShapeMixin,
    AnchorMixin,
    FillMixin,
    StrokeMixin,
    OpacityMixin,
)
from visuscript.constants import Anchor


class Drawing(
    GlobalShapeMixin,
    HierarchicalDrawable,
    FillMixin,
    StrokeMixin,
    AnchorMixin,
    OpacityMixin,
):
    """A :class:`~visuscript.mixins.HierarchicalDrawable` for which the self-display is defined by a :class:`~visuscript.Path`."""

    def __init__(self, path: Path):
        self._path: Path = path
        super().__init__()
        self.set_anchor(Anchor.DEFAULT)

    def calculate_top_left(self):
        return self._path.top_left

    def calculate_width(self):
        return self._path.width

    def calculate_height(self):
        return self._path.height

    def draw_self(self):
        self._path.set_offset(*self.anchor_offset)
        return f"""<path \
d="{self._path.path_str}" \
transform="{self.global_transform.svg_transform}" \
stroke="{self.stroke.rgb}" \
stroke-opacity="{self.stroke.opacity}" \
stroke-width="{self.stroke_width}" \
fill="{self.fill.rgb}" \
fill-opacity="{self.fill.opacity}" \
opacity="{self.global_opacity}"\
/>"""
