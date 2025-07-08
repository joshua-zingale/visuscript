from typing import TypeVar, Generic
from copy import deepcopy

from visuscript._internal._interpolable import InterpolableLike, interpolate
from visuscript._internal._constructors import construct_vec3

from .animation import AlphaAnimation
from visuscript.property_locker import PropertyLocker

from visuscript.primatives import Transform, Color, Rgb, Vec2, Vec3


from visuscript.drawable import Element

class NotInterpolableError(ValueError):
    def __init__(self, property_name: str):
        super().__init__(f"'{property_name}' is not Interpolable.")

T = TypeVar('T')
class PropertyAnimation(AlphaAnimation, Generic[T]):
    def __init__(self, *, obj: T, destinations: list[InterpolableLike], properties: list[str], initials: list[InterpolableLike | None], **kwargs):
        super().__init__(**kwargs)
        self._obj = obj
        self._destinations = deepcopy(destinations)
        self._attributes = deepcopy(properties)
        self._initials: list[InterpolableLike] = []
        for attribute, initial in zip(self._attributes, initials):
            if not isinstance(getattr(obj, attribute), InterpolableLike):
                raise NotInterpolableError(attribute)
            self._initials.append(deepcopy(getattr(obj, attribute)) if initial is None else deepcopy(initial))

    def __init_locker__(self, *, obj: T, destinations: list[InterpolableLike], properties: list[str], initials: list[InterpolableLike | None], **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({
            obj: properties
        })

    def update(self, alpha: float):
        for attribute, initial, destination in zip(self._attributes, self._initials, self._destinations):
            setattr(self._obj, attribute, interpolate(initial, destination, alpha))


class TranslationAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_translation: Vec2 | list, initial_translation: Vec2 | Vec3 | None = None,**kwargs):
        super().__init__(
            obj=transform,
            properties=['translation'],
            destinations=[construct_vec3(target_translation, transform.translation.z)],
            initials=[construct_vec3(initial_translation, transform.translation.z)],
            **kwargs)
    def __init_locker__(self, transform: Transform, target_translation: Vec2 | list, initial_translation: Vec2 | Vec3 | None = None,**kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({transform: ['translation']})

class ScaleAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_scale: float | Vec3 | list, initial_scale: int | float | Vec2 | Vec3 | None = None, **kwargs):
        super().__init__(
            obj=transform,
            properties=['scale'],
            destinations=[construct_vec3(target_scale, transform.scale.z)],
            initials=[construct_vec3(initial_scale, transform.scale.z)],
            **kwargs)
        
    def __init_locker__(self, transform: Transform, target_scale: float | Vec3 | list, initial_scale: int | float | Vec2 | Vec3 | None = None, **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({transform: ['scale']})

class RotationAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_rotation: float, initial_rotation: int | float | None = None, **kwargs):
        super().__init__(
            obj=transform,
            properties=['rotation'],
            destinations=[target_rotation],
            initials=[initial_rotation],
            **kwargs)
    def __init_locker__(self, transform: Transform, target_rotation: float, initial_rotation: int | float | None = None, **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({transform: ['rotation']})
        
class TransformAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_transform: Transform, initial_transform: Transform | None = None, **kwargs):
        if initial_transform:
            initials = [
                initial_transform.translation,
                initial_transform.scale,
                initial_transform.rotation,
            ]
        else:
            initials = [None]*3
        super().__init__(
            obj=transform,
            properties=['translation','scale','rotation'],
            destinations=[
                target_transform.translation,
                target_transform.scale,
                target_transform.rotation,
                ],
            initials=initials,
            **kwargs)
    def __init_locker__(self, transform: Transform, target_transform: Transform, initial_transform: Transform | None = None, **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({transform: ['translation','scale','rotation']})

class OpacityAnimation(PropertyAnimation[Color | Element]):
    def __init__(self, color: Color | Element, target_opacity: float, initial_opacity: float | None = None, **kwargs):
        super().__init__(
            obj=color,
            properties=['opacity'],
            destinations=[target_opacity],
            initials=[initial_opacity],
            **kwargs)
    def __init_locker__(self, color: Color | Element, target_opacity: float, initial_opacity: float | None = None, **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({color: ['opacity']})

class RgbAnimation(PropertyAnimation[Color]):
    def __init__(self, color: Color, target_rgb: Rgb, initial_rgb: Rgb | str | None = None, **kwargs):
        if isinstance(target_rgb, str):
            target_rgb = Color.PALETTE[target_rgb]
        if isinstance(initial_rgb, str):
            initial_rgb = Color.PALETTE[initial_rgb]
        super().__init__(
            obj=color,
            properties=['rgb'],
            destinations=[target_rgb],
            initials=[initial_rgb],
            **kwargs)
    def __init_locker__(self, color: Color, target_rgb: Rgb, initial_rgb: Rgb | str | None = None, **kwargs): # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({color: ['rgb']})