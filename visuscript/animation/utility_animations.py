from visuscript.primatives import Rgb
from visuscript.primatives.protocols import HasOpacity, HasRgb
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG, config
from . import AnimationSequence, OpacityAnimation, RgbAnimation, LazyAnimation


def fade_in(
    obj: HasOpacity, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
) -> OpacityAnimation:
    """Returns an Animation to fade an object in."""
    return OpacityAnimation(obj, 1.0, duration=duration)


def fade_out(
    obj: HasOpacity, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
) -> OpacityAnimation:
    """Returns an Animation to fade an object out."""
    return OpacityAnimation(obj, 0.0, duration=duration)


def flash(
    color: HasRgb,
    rgb: Rgb.RgbLike,
    duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
):
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    if isinstance(duration, ConfigurationDeference):
        duration = config.animation_duration
    return LazyAnimation(
        lambda: AnimationSequence(
            RgbAnimation(color, rgb, duration=duration / 2),
            RgbAnimation(color, color.rgb, duration=duration / 2),
        )
    )
