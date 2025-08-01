from typing import TypeVar, Generic, Unpack
from copy import deepcopy

from visuscript._internal._interpolable import InterpolableLike, interpolate

from .animation import AlphaAnimation, AlphaAnimationKwargs
from visuscript.property_locker import PropertyLocker

from visuscript.primatives import Transform, Rgb, Vec2, Color
from visuscript.primatives.protocols import HasRgb, HasOpacity


class NotInterpolableError(ValueError):
    def __init__(self, property_name: str):
        super().__init__(f"'{property_name}' is not Interpolable.")


T = TypeVar("T")


class PropertyAnimation(AlphaAnimation, Generic[T]):
    def __init__(
        self,
        *,
        obj: T,
        destinations: list[InterpolableLike],
        properties: list[str],
        initials: list[InterpolableLike | None],
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        super().__init__(**kwargs)
        self._obj = obj
        self._destinations = deepcopy(destinations)
        self._attributes = deepcopy(properties)
        self._initials: list[InterpolableLike] = []
        for attribute, initial in zip(self._attributes, initials):
            if not isinstance(getattr(obj, attribute), InterpolableLike):
                raise NotInterpolableError(attribute)
            self._initials.append(
                deepcopy(getattr(obj, attribute))
                if initial is None
                else deepcopy(initial)
            )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        obj: T,
        destinations: list[InterpolableLike],
        properties: list[str],
        initials: list[InterpolableLike | None],
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({obj: properties})

    def update(self, alpha: float):
        for attribute, initial, destination in zip(
            self._attributes, self._initials, self._destinations
        ):
            setattr(self._obj, attribute, interpolate(initial, destination, alpha))


class TranslationAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_translation: Vec2.Vec2Like,
        initial_translation: Vec2.Vec2Like | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        super().__init__(
            obj=transform,
            properties=["translation"],
            destinations=[Vec2.construct(target_translation)],
            initials=[
                Vec2.construct(initial_translation) if initial_translation else None
            ],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_translation: Vec2.Vec2Like,
        initial_translation: Vec2.Vec2Like | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({transform: ["translation"]})


class ScaleAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_scale: Vec2.Vec2Like | float,
        initial_scale: Vec2.Vec2Like | float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        super().__init__(
            obj=transform,
            properties=["scale"],
            destinations=[
                Vec2(target_scale, target_scale)
                if isinstance(target_scale, (int, float))
                else Vec2.construct(target_scale)
            ],
            initials=[
                (
                    Vec2(initial_scale, initial_scale)
                    if isinstance(initial_scale, (int, float))
                    else (Vec2.construct(initial_scale) if initial_scale else None)
                )
            ],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_scale: Vec2.Vec2Like | float,
        initial_scale: Vec2.Vec2Like | float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({transform: ["scale"]})


class RotationAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_rotation: float,
        initial_rotation: int | float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        super().__init__(
            obj=transform,
            properties=["rotation"],
            destinations=[target_rotation],
            initials=[initial_rotation],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_rotation: float,
        initial_rotation: int | float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({transform: ["rotation"]})


class TransformAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_transform: Transform.TransformLike,
        initial_transform: Transform.TransformLike | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        target_transform = Transform.construct(target_transform)

        if initial_transform is not None and not isinstance(
            initial_transform, Transform
        ):
            initial_transform = Transform.construct(initial_transform)

        initials: list[InterpolableLike | None]
        if initial_transform:
            initials = [
                initial_transform.translation,
                initial_transform.scale,
                initial_transform.rotation,
            ]
        else:
            initials = [None] * 3
        super().__init__(
            obj=transform,
            properties=["translation", "scale", "rotation"],
            destinations=[
                target_transform.translation,
                target_transform.scale,
                target_transform.rotation,
            ],
            initials=initials,
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_transform: Transform.TransformLike,
        initial_transform: Transform.TransformLike | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({transform: ["translation", "scale", "rotation"]})


class OpacityAnimation(PropertyAnimation[HasOpacity]):
    def __init__(
        self,
        color: HasOpacity,
        target_opacity: float,
        initial_opacity: float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        super().__init__(
            obj=color,
            properties=["opacity"],
            destinations=[target_opacity],
            initials=[initial_opacity],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        color: HasOpacity,
        target_opacity: float,
        initial_opacity: float | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({color: ["opacity"]})


class RgbAnimation(PropertyAnimation[HasRgb]):
    def __init__(
        self,
        color: HasRgb,
        target_rgb: Rgb.RgbLike,
        initial_rgb: Rgb.RgbLike | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        target_rgb = Color(target_rgb).rgb
        if initial_rgb is not None:
            initial_rgb = Color(initial_rgb).rgb

        super().__init__(
            obj=color,
            properties=["rgb"],
            destinations=[target_rgb],
            initials=[initial_rgb],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        color: HasRgb,
        target_rgb: Rgb.RgbLike,
        initial_rgb: Rgb.RgbLike | None = None,
        **kwargs: Unpack[AlphaAnimationKwargs],
    ):
        return PropertyLocker({color: ["rgb"]})
