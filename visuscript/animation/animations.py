import typing as t

from visuscript.primatives import Rgb, Vec2, Transform
from visuscript.segment import Path
from visuscript.primatives.protocols import HasOpacity, HasRgb, HasTransform, HasShape
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG, config
from visuscript.math_utility import magnitude
from visuscript.lazy_object import make_lazy
from visuscript.property_locker import PropertyLocker
from visuscript.updater import Updater

from .constructors import sequence, bundle, laze, construct, duration_to_frame_count
from .primatives import Animation
from .property_animations import (
    animate_opacity,
    animate_rgb,
    animate_translation,
    animate_scale,
    animate_rotation,
    _InterpolationKwargs, # type: ignore[reportPrivateUsage]
    )
from .easing import sin_easing2

def fade_in(
    obj: HasOpacity, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
) -> Animation:
    """Returns an Animation to fade an object in."""
    return animate_opacity(obj, 1.0, duration=duration)


def fade_out(
    obj: HasOpacity, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
) -> Animation:
    """Returns an Animation to fade an object out."""
    return animate_opacity(obj, 0.0, duration=duration)


def flash(
    color: HasRgb,
    rgb: Rgb.RgbLike,
    duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
) -> Animation:
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    if isinstance(duration, ConfigurationDeference):
        duration = config.animation_duration
    return sequence(
        animate_rgb(color, rgb, duration=duration/3),
        animate_rgb(color, color.rgb, initial=make_lazy(color).rgb, duration=duration/3)
        )


def wait(duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> Animation:
    total_frames = duration_to_frame_count(duration)
    def advancer(frame: int):
        if frame == total_frames:
            return None    
        return frame + 1
    return construct(advancer, 0)

_P = t.ParamSpec("_P")

def run(function: t.Callable[_P, t.Any], *args: _P.args, **kwargs: _P.kwargs) -> Animation:
    def wrapper(been_run: bool):
        if not been_run:
            function(*args, **kwargs)
        return None
    return construct(wrapper, False)

def animate_path(obj: Transform, path: Path, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG, easing_function: t.Callable[[float], float] = sin_easing2) -> Animation:
    total_frames = duration_to_frame_count(duration)
    def advancer(frame: int):
        if frame == total_frames:
            return None    
        frame_ord = frame + 1
        obj.translation = path.point_percentage(easing_function(frame_ord/total_frames))
        return frame_ord
    return construct(advancer, 0, locker=PropertyLocker({obj: ["translation"]}))


def animate_updater(updater: Updater, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG, locker: t.Optional[PropertyLocker] = None) -> Animation:
    total_frames = duration_to_frame_count(duration)
    def advancer(frame: int):
        if frame == total_frames:
            return None
        t = frame / config.fps
        dt = 1 / config.fps
        updater.update(t, dt)
        return frame + 1
    return construct(advancer, 0, updater.locker)


class Swapable(HasTransform, HasShape, t.Protocol):
    pass


def quadratic_swap(
    a: Swapable,
    b: Swapable,
    *,
    height_multiplier: float = 1,
    duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
) -> Animation:
    """Returns an :class:`Animation` to swap two objects along a quadratic bezier curve."""

    def _eager_quadratic_swap(
            a: Swapable,
            b: Swapable,
            *,
            height_multiplier: float,
            duration: float | ConfigurationDeference):
        
        diff = b.transform.translation - a.transform.translation
        distance = magnitude(diff)
        direction = diff / distance
        ortho = Vec2(-direction.y, direction.x)

        mid = a.transform.translation + direction * distance / 2
        lift = ortho * a.shape.circumscribed_radius * 2 * height_multiplier

        return bundle(
            animate_translation(a.transform, mid - lift, b.transform.translation, duration=duration),
            animate_translation(b.transform, mid + lift, a.transform.translation, duration=duration)
        )
    
    return laze(_eager_quadratic_swap, a, b, height_multiplier=height_multiplier, duration=duration)

def animate_transform(obj: Transform, first_target: Transform, *targets: Transform, initial: t.Optional[Transform] = None, **kwargs: t.Unpack[_InterpolationKwargs[t.Any]]):
    translations = map(lambda t: t.translation, targets)
    scales = map(lambda t: t.scale, targets)
    rotations = map(lambda t: t.rotation, targets)
    initial_translation = initial.translation if initial else None
    initial_scale = initial.scale if initial else None
    initial_rotation = initial.rotation if initial else None
    return bundle(
        animate_translation(obj, first_target.translation, *translations, initial=initial_translation, **kwargs),
        animate_scale(obj, first_target.scale, *scales, initial=initial_scale, **kwargs),
        animate_rotation(obj, first_target.rotation, *rotations, initial=initial_rotation, **kwargs)
    )