from visuscript.primatives import Rgb
def rgb_diff(rgb1: Rgb, rgb2: Rgb) -> int:
    """Returns the difference between two rgb values."""
    return sum(abs(a-b) for a, b in zip(rgb1, rgb2))