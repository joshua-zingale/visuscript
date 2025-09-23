import typing as t
from dataclasses import dataclass

from visuscript.primatives import Transform, Vec2, InterpolableFloat, Rgb
from visuscript.primatives.protocols import HasRgb, HasOpacity
from visuscript.lazy_object import make_lazy
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.property_locker import PropertyLocker


from .protocols import Setter, InterpolationFunction, Keyframe, Interpolable
from .primatives import Animation
from .constructors import laze, keyframe_construct, duration_to_frame_count
from .easing import sin_easing2
from .interpolation import interpolate



_T = t.TypeVar("_T")
_U = t.TypeVar("_U")

class _InterpolationKwargs(t.TypedDict, t.Generic[_T], total=False):
    """Common keyword arguments for interpolation-like animations."""

    duration: float | ConfigurationDeference
    easing_function: t.Callable[[float], float]
    interpolation_function: InterpolationFunction[_T]

@dataclass
class _InterpolationCompleteKwargs(t.Generic[_T]):
    duration: float
    easing_function: t.Callable[[float], float]    
    interpolation_function: InterpolationFunction[_T]

def _parse_interpolation_kwargs(kwargs: _InterpolationKwargs[_T], default_easing: t.Callable[[float], float], default_interpolation: InterpolationFunction[_T]) -> _InterpolationCompleteKwargs[_T]:
    duration = kwargs.get("duration") or DEFER_TO_CONFIG

    
    return _InterpolationCompleteKwargs(
        duration=config.animation_duration if isinstance(duration, ConfigurationDeference) else duration,
        easing_function=kwargs.get("easing_function") or default_easing,
        interpolation_function=kwargs.get("interpolation_function") or default_interpolation
    )


def _get_evenly_space_keyframes(first_state: Interpolable[_T], states: t.Sequence[Interpolable[_T]]) -> tuple[Keyframe[_T], tuple[Keyframe[_T], ...]]:
    num_states = len(states)
    return (
        (first_state, 0),
        tuple(map(lambda s: (s[1], s[0] / num_states), enumerate(states, 1)))
    )




# @t.overload
# def construct_property_animation(setter: Setter[_T], interpolation_function: InterpolationFunction[_T], first_keyframe: Keyframe[_T], keyframes: t.Sequence[Keyframe[_T]], locker: t.Optional[PropertyLocker] = None, **kwargs: t.Unpack[_InterpolationKwargs]) -> Animation: ...
# @t.overload
# def construct_property_animation(setter: Setter[_T], interpolation_function: InterpolationFunction[_T], first_keyframe: Interpolable[_T], keyframes: t.Sequence[Interpolable[_T]], locker: t.Optional[PropertyLocker] = None, **kwargs: t.Unpack[_InterpolationKwargs]) -> Animation: ...
def construct_property_animation(setter: Setter[_T], first_keyframe: Keyframe[_T] | Interpolable[_T], keyframes: t.Sequence[Keyframe[_T] | Interpolable[_T]], locker: t.Optional[PropertyLocker] = None, **kwargs: t.Unpack[_InterpolationKwargs[_T]]) -> Animation:
    complete_kwargs = _parse_interpolation_kwargs(
        kwargs,
        default_easing=sin_easing2,
        default_interpolation=interpolate
        )

    if not isinstance(first_keyframe, tuple):
        no_alpha_keyframes: list[Interpolable[_T]] = []
        full_keyframes: list[Keyframe[_T]] = []

        found_keyframe = False
        found_non_keyframe = False
        for keyframe in keyframes:
            if isinstance(keyframe, tuple):
                if found_non_keyframe:
                    raise ValueError("Found keyframe with specified progression when there was a keyframe without a progression before it.")
                found_keyframe = True
                full_keyframes.append(keyframe)
            else:
                if found_keyframe:
                    ValueError("Found a keyframe without a specified progression when there was a keyframe with progression before it.")
                found_non_keyframe = True
                no_alpha_keyframes.append(keyframe)

        assert not (found_keyframe and found_non_keyframe)
        if found_keyframe:
            initial, latter = (first_keyframe, 0.0), tuple(full_keyframes)
        else:
            initial, latter = _get_evenly_space_keyframes(first_keyframe, no_alpha_keyframes)

    else:
        with_alpha_keyframes: list[Keyframe[_T]] = []
        for keyframe in keyframes:
            if not isinstance(keyframe, tuple):
                raise ValueError("Found a keyframe without a specified progression when there was a keyframe with progression before it.")
            with_alpha_keyframes.append(keyframe)
        initial, latter = first_keyframe, with_alpha_keyframes


    return keyframe_construct(
        setter,
        duration_to_frame_count(complete_kwargs.duration),
        complete_kwargs.interpolation_function,
        initial,
        latter,
        easing_function=complete_kwargs.easing_function,
        locker=locker)


def _get_convert_object_maybe_in_tuple(converter: t.Callable[[_T], _U]) -> t.Callable[[_T | tuple[_T, float]], _U | tuple[_U, float]]:
    def wrapped(obj: _T | tuple[_T, float]) -> _U | tuple[_U, float]:
        if isinstance(obj, tuple):
            return (converter(obj[0]), obj[1]) # type: ignore
        else:
            return converter(obj)
    return wrapped
    
def _eager_animate_translation(obj: Transform, first_target: Vec2.Vec2Like | tuple[Vec2.Vec2Like, float], *targets: Vec2.Vec2Like | tuple[Vec2.Vec2Like, float], initial: t.Optional[Vec2.Vec2Like | tuple[Vec2.Vec2Like, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Vec2]]):
    convert = _get_convert_object_maybe_in_tuple(Vec2.construct)
    first = convert(initial) if initial else obj.scale
    rest = tuple(map(convert, (first_target,) + targets))
    return construct_property_animation(
        obj.set_translation,
        first,
        rest,
        **kwargs,
        )
def animate_translation(obj: Transform, first_target: Vec2.Vec2Like | tuple[Vec2.Vec2Like, float], *targets: Vec2.Vec2Like | tuple[Vec2.Vec2Like, float], initial: t.Optional[Vec2.Vec2Like | tuple[Vec2.Vec2Like, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Vec2]]):
    return laze(PropertyLocker({obj: ["translation"]}), _eager_animate_translation, obj, first_target, *targets, initial=initial or make_lazy(obj).translation, **kwargs)

def _eager_animate_scale(obj: Transform, first_target: Vec2.Vec2Like | float | tuple[Vec2.Vec2Like | float, float], *targets: Vec2.Vec2Like | float | tuple[Vec2.Vec2Like | float, float], initial: t.Optional[Vec2.Vec2Like | float | tuple[Vec2.Vec2Like, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Vec2]]):
    def converter(scale: Vec2.Vec2Like | float):
        return Vec2(scale, scale) if isinstance(scale, (float, int)) else Vec2.construct(scale)
    convert = _get_convert_object_maybe_in_tuple(converter)
    first = convert(initial) if initial else obj.scale
    rest = tuple(map(convert, (first_target,) + targets))
    return construct_property_animation(
        obj.set_scale,
        first,
        rest,
        **kwargs,
        )
def animate_scale(obj: Transform, first_target: Vec2.Vec2Like | float | tuple[Vec2.Vec2Like | float, float], *targets: Vec2.Vec2Like | float | tuple[Vec2.Vec2Like | float, float], initial: t.Optional[Vec2.Vec2Like | float | tuple[Vec2.Vec2Like, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Vec2]]):
    return laze(PropertyLocker({obj: ["scale"]}), _eager_animate_scale, obj, first_target, *targets, initial=initial or make_lazy(obj).scale, **kwargs)

def _eager_animate_rotation(obj: Transform, first_target: float | tuple[float, float], *targets: float | tuple[float, float], initial: t.Optional[float | tuple[float, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[float]]):
    convert = _get_convert_object_maybe_in_tuple(InterpolableFloat)
    first = convert(initial) if initial else obj.rotation
    rest = tuple(map(convert, (first_target,) + targets))
    return construct_property_animation(
        obj.set_rotation,
        first,
        rest,
        **kwargs,
        )
def animate_rotation(obj: Transform, first_target: float | tuple[float, float], *targets: float | tuple[float, float], initial: t.Optional[float | tuple[float, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[float]]):
    return laze(PropertyLocker({obj: ["rotation"]}), _eager_animate_rotation, obj, first_target, *targets, initial=initial or make_lazy(obj).rotation, **kwargs)


def _eager_animate_rgb(obj: HasRgb, first_target: Rgb.RgbLike | tuple[Rgb.RgbLike, float], *targets: Rgb.RgbLike | tuple[Rgb.RgbLike, float], initial: t.Optional[Rgb.RgbLike | tuple[Rgb.RgbLike, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Rgb]]):
    def get_interpolator(rgb: Rgb.RgbLike):
        return Rgb.construct(rgb).get_interpolator()
    convert = _get_convert_object_maybe_in_tuple(get_interpolator)
    first = convert(initial) if initial else obj.rgb.get_interpolator()
    rest = tuple(map(convert, (first_target,) + targets))

    def set_rgb(rgb: Rgb):
        obj.rgb = rgb

    return construct_property_animation(
        set_rgb,
        first,
        rest,
        **kwargs
        )

def animate_rgb(obj: HasRgb, first_target: Rgb.RgbLike | tuple[Rgb.RgbLike, float], *targets: Rgb.RgbLike | tuple[Rgb.RgbLike, float], initial: t.Optional[Rgb.RgbLike | tuple[Rgb.RgbLike, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[Rgb]]):
    return laze(PropertyLocker({obj: ["rgb"]}), _eager_animate_rgb, obj, first_target, *targets, initial=initial or make_lazy(obj).rgb, **kwargs)

def _eager_animate_opacity(obj: HasOpacity, first_target: float | tuple[float, float], *targets: float | tuple[float, float], initial: t.Optional[float | tuple[float, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[float]]):
    convert = _get_convert_object_maybe_in_tuple(InterpolableFloat)
    initial = convert(initial) if initial else obj.opacity
    rest = tuple(map(convert, (first_target,) + targets))
    def set_opacity(opacity: float):
        obj.opacity = opacity
    return construct_property_animation(
        set_opacity,
        initial,
        rest,
        **kwargs,
        )

def animate_opacity(obj: HasOpacity, first_target: float | tuple[float, float], *targets: float | tuple[float, float], initial: t.Optional[float | tuple[float, float]] = None, **kwargs: t.Unpack[_InterpolationKwargs[float]]):
    return laze(PropertyLocker({obj: ["opacity"]}), _eager_animate_opacity, obj, first_target, *targets, initial=initial or make_lazy(obj).opacity, **kwargs)
    
