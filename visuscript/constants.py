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


UP: Vec2 = Vec2(0, -1)
"""A two-dimensional unit vector pointing upward."""
RIGHT: Vec2 = Vec2(1, 0)
"""A two-dimensional unit vector pointing rightward."""
DOWN: Vec2 = Vec2(0, 1)
"""A two-dimensional unit vector pointing downward."""
LEFT: Vec2 = Vec2(-1, 0)
"""A two-dimensional unit vector pointing leftward."""
BACKWARD: Vec3 = Vec3(0, 0, -1)
"""A three-dimensional unit-vector pointing backward, i.e. away from the camera."""
FORWARD: Vec3 = Vec3(0, 0, 1)
"""A three-dimensional unit-vector pointing forward, i.e. toward from the camera."""


PALETTE: dict[str, Rgb] = {
        "dark_slate": Rgb(*[28, 28, 28]),
        "soft_blue": Rgb(*[173, 216, 230]),
        "vibrant_orange": Rgb(*[255, 165, 0]),
        "pale_green": Rgb(*[144, 238, 144]),
        "bright_yellow": Rgb(*[255, 255, 0]),
        "steel_blue": Rgb(*[70, 130, 180]),
        "forest_green": Rgb(*[34, 139, 34]),
        "burnt_orange": Rgb(*[205, 127, 50]),
        "light_gray": Rgb(*[220, 220, 220]),
        "off_white": Rgb(*[245, 245, 220]),
        "medium_gray": Rgb(*[150, 150, 150]),
        "slate_gray": Rgb(*[112, 128, 144]),
        "crimson": Rgb(*[220, 20, 60]),
        "gold": Rgb(*[255, 215, 0]),
        "sky_blue": Rgb(*[135, 206, 235]),
        "light_coral": Rgb(*[240, 128, 128]),
        "red": Rgb(*[255, 99, 71]),
        "orange": Rgb(*[255, 165, 0]),
        "yellow": Rgb(*[255, 215, 0]),
        "green": Rgb(*[124, 252, 0]),
        "blue": Rgb(*[65, 105, 225]),
        "purple": Rgb(*[138, 43, 226]),
        "white": Rgb(*[255, 255, 255]),
    }