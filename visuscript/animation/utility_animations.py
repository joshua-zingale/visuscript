from visuscript.drawable.element import Element
from . import (
    AnimationSequence,
    OpacityAnimation,
    RgbAnimation,
    LazyAnimation
    )

from visuscript.primatives import Color

from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG, config

from typing import Tuple


def fade_in(element: Element, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element in."""
    return OpacityAnimation.lazy(element, 1.0, **kwargs)

def fade_out(element: Element, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element out."""
    return OpacityAnimation.lazy(element, 0.0, **kwargs)

def flash(color: Color, rgb: str | Tuple[int, int, int], duration: float | ConfigurationDeference = DEFER_TO_CONFIG, **kwargs):
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration
    return LazyAnimation(lambda:AnimationSequence(
        RgbAnimation(color, rgb, duration=duration/2, **kwargs),
        RgbAnimation.lazy(color, color.rgb, duration=duration/2, **kwargs)
    ))

