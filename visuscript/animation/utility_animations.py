from typing import Tuple

from visuscript.primatives import Rgb
from visuscript.drawable.mixins import OpacityMixin, RgbMixin
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG, config
from . import AnimationSequence, OpacityAnimation, RgbAnimation, LazyAnimation

def fade_in(element: OpacityMixin, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element in."""
    return OpacityAnimation.lazy(element, 1.0, **kwargs)


def fade_out(element: OpacityMixin, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element out."""
    return OpacityAnimation.lazy(element, 0.0, **kwargs)


def flash(
    color: RgbMixin,
    rgb: Rgb._RgbLike,
    duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    **kwargs,
):
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    if isinstance(duration, ConfigurationDeference):
        duration = config.animation_duration
    return LazyAnimation(
        lambda: AnimationSequence(
            RgbAnimation(color, rgb, duration=duration / 2, **kwargs),
            RgbAnimation.lazy(color, color.rgb, duration=duration / 2, **kwargs),
        )
    )
