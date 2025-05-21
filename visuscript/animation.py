from typing import Callable, Iterable
from abc import ABC, abstractmethod
from visuscript.config import *
from visuscript.drawable import Drawable
from visuscript.element import Drawing
from visuscript.primatives import *
from visuscript.segment import Path
import ctypes
import numpy as np

from visuscript.config import config

def quintic_easing(x: float) -> float:
    return 6 * x**5 - 15 * x**4 + 10 * x**3
def sin_easing(a: float) -> float:
    return float(1 - np.cos(a*np.pi))/2

class LockedPropertyError(ValueError):
    def __init__(self, obj: object, property: str):
        message = f"'{property}' on object of type {type(obj)} is already locked."
        super().__init__(message)

class PropertyLocker:
    ALL_PROPERTIES = "*"
    """Signifies that all properties are locked for this object."""

    def __init__(self):
        self._map: dict[object, set[str]] = dict()

    def add(self, obj: object, property: str = ALL_PROPERTIES):
        """Raises LockedPropertyError if the property is already locked by this PropertyLocker."""

        self._map[obj] = self._map.get(obj, set())

        if PropertyLocker.ALL_PROPERTIES in self._map[obj]:
            raise LockedPropertyError(obj, property)
        if property == PropertyLocker.ALL_PROPERTIES and len(self._map[obj]) > 0:
            raise LockedPropertyError(obj, property)
        if property in self._map[obj]:
            raise LockedPropertyError(obj, property)
    
        self._map[obj] = self._map[obj].union(set([property]))

    def update(self, other: "PropertyLocker"):
        """Merges this PropertyLocker with another in place. Raises LockedPropertyError if the two PropertyLockers lock one or more of the same properties on the same object."""

        for obj in other._map:
            for property in other._map[obj]:
                self.add(obj, property)

class Animation(ABC):

    @abstractmethod
    def advance(self) -> bool:
        """
        Makes the changes for one frame of the animation.

        Returns True if there is a next frame for the animation or if the current advance was the last frame; else returns False.
        """
        ...

    @property
    @abstractmethod
    def locker(self) -> PropertyLocker:
        """
        Returns a PropertyLocker identifying all objects/properties updated by this Animation.
        """
        ...

    def finish(self):
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which it would have been had the animation completed naturally.
        """
        while self.advance():
            pass
        
class NoAnimation(Animation):

    def __init__(self, *, fps: int | Configuration = DEFAULT_CONFIG, duration: float | Configuration = DEFAULT_CONFIG):

        fps = config.fps if fps is DEFAULT_CONFIG else fps
        duration = config.animation_duration if duration is DEFAULT_CONFIG else duration

        self._num_frames = round(fps*duration)

    @property
    def objects(self) -> set[int]:
        return set()

    def advance(self) -> bool:
        if self._num_frames > 0:
            self._num_frames -= 1
            return True
        return False
    
class RF(Animation):

    def __init__(self, function: Callable[[], None]):
        self._function = function

    @property
    def locker(self) -> PropertyLocker:
        return PropertyLocker()

    def advance(self) -> bool:
        self._function()
        return False
    
class AnimationSequence(Animation):

    def __init__(self, *animations: Animation):
        self._animations = animations
        self._animation_index = 0

        self._locker = PropertyLocker()
        for animation in self._animations:
            self._locker.update(animation)

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def advance(self) -> bool:
        while self._animation_index < len(self._animations) and self._animations[self._animation_index].advance() == False:
            self._animation_index += 1

        if self._animation_index == len(self._animations):
            return False
        return True



class TimeDeltaAnimation(Animation):
    def __init__(self, *, fps: int | Configuration = DEFAULT_CONFIG, duration: float | Configuration = DEFAULT_CONFIG, updates_per_frame: int = 1):

        fps = config.fps if fps is DEFAULT_CONFIG else fps
        duration = config.animation_duration if duration is DEFAULT_CONFIG else duration

        assert updates_per_frame >= 0

        self._frame_number: int = 1
        self._num_frames: int = round(fps * duration)

        self._dt: float = 1/(fps * updates_per_frame)

        self._updates_per_frame: int = updates_per_frame


    def advance(self) -> bool:
        # TODO handle edge case of the final advance, where less time may need to be taken

        if self._frame_number > self._num_frames:
            return False

        for _ in range(self._updates_per_frame):
            self.update(self._dt)

        self._frame_number += 1

        
        return True
            

    @abstractmethod
    def update(self, dt: float):
        """
        Makes the change for the time `dt` in seconds of this animation.
        """
        ...


class AlphaAnimation(Animation):
    def __init__(self, *, fps: int | Configuration = DEFAULT_CONFIG, duration: float | Configuration = DEFAULT_CONFIG, easing_function: Callable[[float], float] = sin_easing):

        fps = config.fps if fps is DEFAULT_CONFIG else fps
        duration = config.animation_duration if duration is DEFAULT_CONFIG else duration

        self._frame_number: int = 1
        self._num_frames: int = round(fps * duration)
        self._easing_function = easing_function


    def first_advance_initializer(self):
        """
        This function is run the first time advance is called. This can be useful for setting the source value of interpolation.
        """
        pass


    def advance(self) -> bool:

        if self._frame_number == 1:
            self.first_advance_initializer()

        if self._frame_number > self._num_frames:
            return False

        self.update(self._easing_function(self._frame_number/self._num_frames))

        self._frame_number += 1
        
        return True
            

    @abstractmethod
    def update(self, alpha: float):
        """
        Updates the object to be percentage `alpha` through the animation.
        """
        ...

class AnimationBundle(Animation):
    def __init__(self, *animations: Animation):
        self._animations: list[Animation] = []

        self._locker = PropertyLocker()

        for animation in animations:
            self.push(animation)
                
    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def advance(self) -> bool:
        return sum(map(lambda x: x.advance(), self._animations)) > 0
    
    def push(self, animation: Animation | list[Animation], _call_method: str ="push"):
        if isinstance(animation, Animation):
            self._locker.update(animation.locker)
            self._animations.append(animation)
        elif isinstance(animation, list):
            for animation_ in animation:
                self.push(animation)
        else:
            raise TypeError(f"'{_call_method}' is only implemented for types Animation and list[Animation], not for '{type(animation)}'")


    def clear(self):
        self._animations = []
        self._locker = PropertyLocker()
    
    def __lshift__(self, other: Animation | list[Animation]):
        self.push(other, _call_method="<<")


class PathAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, path: Path, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        self._path = path

        self._locker = PropertyLocker()
        self._locker.add(self._drawable, "transform.translation")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    

    def first_advance_initializer(self):
        self._source_translation = self._drawable.transform.translation


    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._drawable.transform.translation = self._path.end

        self._drawable.transform.translation = self._path.point_percentage(alpha)

class TranslationAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, target_translation: Vec2 | list, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        self._target_translation = Transform(target_translation).translation

        self._locker = PropertyLocker()
        self._locker.add(self._drawable, "transform.translation")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def first_advance_initializer(self):
        self._source_translation = self._drawable.transform.translation

    def update(self, alpha: float):
        assert 0 <= alpha <= 1

        self._drawable.transform.translation = self._source_translation * (1 - alpha) + self._target_translation * alpha

class ScaleAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, target_scale: float | Vec3 | list, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        
        self._target_scale = target_scale

        self._locker = PropertyLocker()
        self._locker.add(self._drawable, "transform.scale")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker


    def first_advance_initializer(self):
        self._source_scale = self._drawable.transform.scale

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._drawable.transform.scale = self._source_scale * (1 - alpha) + self._target_scale * alpha

class RotationAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, target_rotation: float, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        self._target_rotation = target_rotation

        self._locker = PropertyLocker()
        self._locker.add(self._drawable, "transform.rotation")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def first_advance_initializer(self):
        self._source_rotation = self._drawable.transform.rotation

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._drawable.transform.rotation = self._source_rotation * (1 - alpha) + self._target_rotation * alpha



class TransformInterpolation(Animation):
    def __init__(self, drawable: Drawable, target: Transform, fps: int | Configuration = DEFAULT_CONFIG, duration: float | Configuration = DEFAULT_CONFIG, easing_function: Callable[[float], float] = sin_easing):

        fps = config.fps if fps is DEFAULT_CONFIG else fps
        duration = config.animation_duration if duration is DEFAULT_CONFIG else duration

        super().__init__()

        animations = [
            TranslationAnimation(drawable=drawable, target_translation=target.translation, fps=fps, duration=duration, easing_function=easing_function),
            ScaleAnimation(drawable=drawable, target_scale=target.scale, fps = fps, duration = duration, easing_function = easing_function),
            RotationAnimation(drawable=drawable, target_rotation=target.rotation, fps = fps, duration = duration, easing_function = easing_function)
        ]

        self._animation_bundle = AnimationBundle(*animations)

    @property
    def locker(self) -> PropertyLocker:
        return self._animation_bundle.locker
    
    def advance(self) -> bool:
        return self._animation_bundle.advance()
        

class FillAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawing, target_fill: Color, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        self._source_color = Color(drawable.fill)
        self._target_color = Color(target_fill)

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._drawable.fill = self._source_color * (1 - alpha) + self._target_color * alpha