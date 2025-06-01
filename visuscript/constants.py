from enum import IntEnum, auto
from visuscript.primatives import *

class Anchor(IntEnum):
    """
    Defines anchor points for Drawable objects.
    """
    DEFAULT = auto()
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    RIGHT = auto()
    BOTTOM_RIGHT = auto()
    BOTTOM = auto()
    BOTTOM_LEFT = auto()
    LEFT = auto()
    CENTER = auto()


class OutputFormat(IntEnum):
    """
    Defines the image output format for Canvas objects.
    """
    SVG = auto()

class LineTarget(IntEnum):
    """
    Defines the source or destination point method for a Line.
    """
    RADIAL = auto()
    """Indicates that the source/destination should rest on the radius of the a circumscribed circle around the object."""
    CENTER = auto()
    """Indicates that the source/destination should rest at the center the object."""

UP: Vec2 = Vec2(0,-1)
"""A two-dimensional unit vector pointing upward."""
RIGHT: Vec2 = Vec2(1,0)
"""A two-dimensional unit vector pointing rightward."""
DOWN: Vec2 = Vec2(0,1)
"""A two-dimensional unit vector pointing downward."""
LEFT: Vec2 = Vec2(-1,0)
"""A two-dimensional unit vector pointing leftward."""
BACKWARD: Vec3 = Vec3(0,0,-1)
"""A three-dimensional unit-vector pointing backward, i.e. away from the camera."""
FORWARD: Vec3 = Vec3(0,0,1)
"""A three-dimensional unit-vector pointing forward, i.e. toward from the camera."""
