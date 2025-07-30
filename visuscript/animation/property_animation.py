from typing import TypeVar, Generic, Sequence
from copy import deepcopy

from visuscript._internal._interpolable import InterpolableLike, interpolate
from visuscript._internal._constructors import construct_vec3

from .animation import AlphaAnimation
from visuscript.property_locker import PropertyLocker

from visuscript.primatives import Transform, Rgb, Vec2, Vec3
from visuscript.drawable import Color
from visuscript.drawable.mixins import OpacityMixin, RgbMixin


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
        **kwargs,
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
        **kwargs,
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
        target_translation: Vec2 | Vec3 | Sequence[float],
        initial_translation: Vec2 | Vec3 | None = None,
        **kwargs,
    ):
        super().__init__(
            obj=transform,
            properties=["translation"],
            destinations=[construct_vec3(target_translation, transform.translation.z)],
            initials=[construct_vec3(initial_translation, transform.translation.z)],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_translation: Vec2 | Vec3 | Sequence[float],
        initial_translation: Vec2 | Vec3 | None = None,
        **kwargs,
    ):
        return PropertyLocker({transform: ["translation"]})


class ScaleAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_scale: float | Vec3 | list,
        initial_scale: int | float | Vec2 | Vec3 | None = None,
        **kwargs,
    ):
        super().__init__(
            obj=transform,
            properties=["scale"],
            destinations=[construct_vec3(target_scale, transform.scale.z)],
            initials=[construct_vec3(initial_scale, transform.scale.z)],
            **kwargs,
        )

    def __init_locker__(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        transform: Transform,
        target_scale: float | Vec3 | list,
        initial_scale: int | float | Vec2 | Vec3 | None = None,
        **kwargs,
    ):
        return PropertyLocker({transform: ["scale"]})


class RotationAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_rotation: float,
        initial_rotation: int | float | None = None,
        **kwargs,
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
        **kwargs,
    ):
        return PropertyLocker({transform: ["rotation"]})


class TransformAnimation(PropertyAnimation[Transform]):
    def __init__(
        self,
        transform: Transform,
        target_transform: Transform,
        initial_transform: Transform | None = None,
        **kwargs,
    ):
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
        target_transform: Transform,
        initial_transform: Transform | None = None,
        **kwargs,
    ):
        return PropertyLocker({transform: ["translation", "scale", "rotation"]})


class OpacityAnimation(PropertyAnimation[OpacityMixin]):
    def __init__(
        self,
        color: OpacityMixin,
        target_opacity: float,
        initial_opacity: float | None = None,
        **kwargs,
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
        color: OpacityMixin,
        target_opacity: float,
        initial_opacity: float | None = None,
        **kwargs,
    ):
        return PropertyLocker({color: ["opacity"]})


class RgbAnimation(PropertyAnimation[RgbMixin]):
    def __init__(
        self,
        color: RgbMixin,
        target_rgb: Rgb._RgbLike,
        initial_rgb: Rgb._RgbLike | None = None,
        **kwargs,
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
        color: RgbMixin,
        target_rgb: Rgb._RgbLike,
        initial_rgb: Rgb._RgbLike | None = None,
        **kwargs,
    ):
        return PropertyLocker({color: ["rgb"]})
