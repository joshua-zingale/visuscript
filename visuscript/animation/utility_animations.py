from typing import Protocol

from visuscript.primatives import Rgb, Vec2
from visuscript.primatives.protocols import HasOpacity, HasRgb, HasTransform, HasShape
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG, config
from visuscript.segment import Path
from visuscript.math_utility import magnitude
from . import (
    AnimationSequence,
    OpacityAnimation,
    RgbAnimation,
    LazyAnimation,
    PathAnimation,
    AnimationBundle,
    Animation,
)


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


class Swapable(HasTransform, HasShape, Protocol):
    pass


def quadratic_swap(
    a: Swapable,
    b: Swapable,
    *,
    height_multiplier: float = 1,
    duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
) -> Animation:
    """Returns an AnimationBundle to swap two objects along a quadratic bezier curve."""
    diff = b.transform.translation - a.transform.translation
    distance = magnitude(diff)
    direction = diff / distance
    ortho = Vec2(-direction.y, direction.x)

    mid = a.transform.translation + direction * distance / 2
    lift = ortho * a.shape.circumscribed_radius * 2 * height_multiplier

    return AnimationBundle(
        PathAnimation(
            a.transform,
            Path()
            .M(*a.transform.translation)
            .Q(*(mid - lift), *b.transform.translation),
            duration=duration,
        ),
        PathAnimation(
            b.transform,
            Path()
            .M(*b.transform.translation)
            .Q(*(mid + lift), *a.transform.translation),
            duration=duration,
        ),
    )
