from enum import IntEnum, auto

class Anchor(IntEnum):
    """
    Defines anchor points for Drawable objects.
    """
    DEFAULT = auto()
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    LEFT = auto()
    CENTER = auto()


class OutputFormat(IntEnum):
    """
    Defines the image output format for Canvas objects.
    """
    SVG = auto()
    PNG = auto()