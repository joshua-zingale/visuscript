"""Contains mixins usable for creating displayable objects that are
compatible with the Visuscript ecosystem.

To create a new displayable object, inherit from :class:`Drawable`.
Then, add appropriate mixins according to what features your new
object should have, e.g. a :class:`Shape` or an opacity.

Also contains :class:`Color`.
"""

from .color import RgbMixin, OpacityMixin, Color
from .mixins import (
    Drawable,
    TransformMixin,
    FillMixin,
    StrokeMixin,
    ShapeMixin,
    TransformableShapeMixin,
    AnchorMixin,
    HierarchicalDrawable,
    GlobalShapeMixin,
    Element,
    Shape,
)

__all__ = [
    "RgbMixin",
    "OpacityMixin",
    "Color",
    "Drawable",
    "TransformMixin",
    "FillMixin",
    "StrokeMixin",
    "ShapeMixin",
    "TransformableShapeMixin",
    "AnchorMixin",
    "HierarchicalDrawable",
    "GlobalShapeMixin",
    "Element",
    "Shape",
]
