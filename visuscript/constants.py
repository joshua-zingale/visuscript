from enum import IntEnum, auto

class Anchor(IntEnum):
    """
    Defines anchor points for Drawables.
    """
    DEFAULT = auto()
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    LEFT = auto()
    CENTER = auto()