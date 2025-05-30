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
    PNG = auto()

class LineTarget(IntEnum):
    """
    Defines the source or destination point method for a Line.
    """
    RADIAL = auto()
    CENTER = auto()

UP: Vec2 = Vec2(0,-1)
RIGHT: Vec2 = Vec2(1,0)
DOWN: Vec2 = Vec2(0,1)
LEFT: Vec2 = Vec2(-1,0)
BACKWARD: Vec3 = Vec3(0,0,-1)
FORWARD: Vec3 = Vec3(0,0,1)
