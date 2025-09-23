"""Contains easing functions for interpolation."""
from math import cos, pi as PI

__all__ = [
    "linear_easing",
    "quintic_easing",
    "sin_easing",
    "sin_easing2",
]

def linear_easing(x: float) -> float:
    return x


def quintic_easing(x: float) -> float:
    return 6 * x**5 - 15 * x**4 + 10 * x**3


def sin_easing(a: float) -> float:
    return float(1 - cos(a * PI)) / 2


def sin_easing2(a: float) -> float:
    return sin_easing(sin_easing(a))
