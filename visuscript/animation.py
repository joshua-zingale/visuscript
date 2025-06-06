"""This module contains the abstract base class of all Animations alongside a bevy of basic animations and easing functions."""

from typing import Callable, Iterable, Generic, TypeVar
from abc import ABC, abstractmethod
from visuscript.config import *
from visuscript.element import Element
from visuscript.primatives import *
from visuscript.segment import Path
from visuscript._property_locker import PropertyLocker
from visuscript.updater import Updater
from visuscript._interpolable import InterpolableLike, interpolate
import numpy as np

from visuscript.config import config
def linear_easing(x: float) -> float:
    return x
def quintic_easing(x: float) -> float:
    return 6 * x**5 - 15 * x**4 + 10 * x**3
def sin_easing(a: float) -> float:
    return float(1 - np.cos(a*np.pi))/2
def sin_easing2(a: float) -> float:
    return sin_easing(sin_easing(a))

#TODO Remove FPS as a parameter for all Animations because set_speed on Updater assumes that the FPS will always match the config

class AnimationABC(ABC):
    def __init__(self):
        self._num_processed_frames = 0
        self._num_advances = 0
        self._animation_speed = 1
        self._keep_advancing = True

    def next_frame(self):
        """Makes the changes for one frame of the animation, accounting for the set animation speed.

        :return: True if this `Animation` had any frames left before it was called.
        :rtype: bool
        """
        self._num_advances += 1
        num_to_advance = round(self._animation_speed * self._num_advances - self._num_processed_frames)

        if self._keep_advancing:
            for _ in range(num_to_advance):
                if self._keep_advancing and not self.advance():
                    self._keep_advancing = False
                    break
            self._num_processed_frames += num_to_advance

        return self._keep_advancing

    @abstractmethod
    def advance(self) -> bool:
        """Makes the changes for one frame of the animation when at animation speed 1.

        :return: True if this `Animation` had any frames left before it was called.
        :rtype: bool
        """        
        ...

    @property
    @abstractmethod
    def locker(self) -> PropertyLocker:
        """
        The :class:`PropertyLocker` identifying all objects/properties updated by this Animation.
        """
        ...

    def finish(self) -> None:
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which it would have been had the animation completed naturally.
        """
        while self.next_frame():
            pass

    def set_speed(self, speed: float) -> Self:
        """Sets the playback speed for this Animation.

        :param speed: The new duration of the :class:`Animation` will be duration*speed.
        :type speed: float
        :return: self
        :rtype: Self
        """
        if not isinstance(speed, (int, float)) or speed <= 0:
            raise ValueError("Animation speed must be a positive number.")
        self._animation_speed = speed
        return self

class CompressedAnimation(AnimationABC):
    """:class:`CompressedAnimation` wraps around another :class:`Animation`, compressing it into an :class:`Animation` with a single advance that runs all of the advances in the original :class:`Animation`."""
    def __init__(self, animation: AnimationABC):
        super().__init__()
        self._animation = animation
        self._locker = animation.locker

    @property
    def locker(self):
        return self._locker
    
    def advance(self):
        advanced = False
        while self._animation.next_frame():
            advanced = True
        return advanced
    


class Animation(AnimationABC):
    """An Animation can be used to modify properties of objects in a programmatic manner."""
    def compress(self) -> CompressedAnimation:
        """Returns a compressed version of this Animation.
        
        The CompressedAnimation will have only a single advance (or frame), during which all of the advances (or frames) for this Animation will complete.
        """
        return CompressedAnimation(self)

class LazyAnimation(Animation):
    """A LazyAnimation allows the initialization of an Animation to be delayed until its first advance.

    The passed-in function must have no side effects because it could be called more than once.
    
    A LazyAnimation can be useful when chaining together multiple animations in an AnimationSequence,
    where the initial state of one object being animated should not be determined until the previous animation completes.
    """
    def __init__(self, animation_function: Callable[[], Animation]):
        super().__init__()
        self._animation_function = animation_function
        self._locker = animation_function().locker

    @property
    def locker(self):
        return self._locker
    
    def advance(self):
        if not hasattr(self, "_animation"):
            self._animation: Animation = self._animation_function()
        return self._animation.next_frame()
    


        
class NoAnimation(Animation):
    """A NoAnimation makes no changes to any object's state.
    
    A NoAnimation can be used to rest at the current state for a specified duration.
    """

    def __init__(self, *, fps: int | ConfigurationDeference = DEFER_TO_CONFIG, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        super().__init__()
        fps = config.fps if fps is DEFER_TO_CONFIG else fps
        duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration

        self._num_frames = round(fps*duration)

    @property
    def objects(self) -> set[int]:
        return set()
    

    @property
    def locker(self) -> PropertyLocker:
        return PropertyLocker()

    def advance(self) -> bool:
        if self._num_frames > 0:
            self._num_frames -= 1
            return True
        return False

# TODO Add an optional parameter to specify what properties are locked by RunFunction
class RunFunction(Animation):
    """A RunFunction Animation runs only a single advance, during which it calls a function."""

    def __init__(self, function: Callable[[], None], consume_frame=False):
        super().__init__()
        self._function = function
        self._has_been_run = False
        self._locker = PropertyLocker()
        self._consume_frame = consume_frame

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def advance(self) -> bool:
        if not self._has_been_run:
            self._function()
            self._has_been_run = True
            return self._consume_frame
        return False
    
class AnimationSequence(Animation):
    """An AnimationSequence runs through Animations in sequence.
    
    An AnimationSequence can be used to play multiple animation, one before another.
    """

    def __init__(self, *animations: Animation):
        super().__init__()
        self._animations: list[Animation] = []
        self._animation_index = 0
        self._locker = PropertyLocker()

        for animation in animations:
            self.push(animation)

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def advance(self) -> bool:
        while self._animation_index < len(self._animations) and self._animations[self._animation_index].next_frame() == False:
            self._animation_index += 1

        if self._animation_index == len(self._animations):
            return False
        return True
    

    def push(self, animation: Animation | Iterable[Animation], _call_method: str ="push"):
        if animation is None:
            pass
        elif isinstance(animation, Animation):
            self._locker.update(animation.locker, ignore_conflicts=True)
            self._animations.append(animation)
        elif isinstance(animation, Iterable):
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(f"'{_call_method}' is only implemented for types Animation and Iterable[Animation], not for '{type(animation)}'")
    
    def __lshift__(self, other: Animation | Iterable[Animation]):
        self.push(other, _call_method="<<")



class AnimationBundle(Animation):
    """An AnimationBundle combines multiple Animation instances into one concurrent Animation.

    An AnimationBundle can be used to play multiple Animation concurrently.
    """
    def __init__(self, *animations: Animation):
        super().__init__()
        self._animations: list[Animation] = []
        self._locker = PropertyLocker()

        for animation in animations:
            self.push(animation)
                
    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def advance(self) -> bool:
        advance_made = sum(map(lambda x: x.next_frame(), self._animations)) > 0
        return advance_made
    
    def push(self, animation: AnimationABC | Iterable[AnimationABC], _call_method: str ="push"):
        """Adds an animation to this AnimationBundle.

        :param animation: The animation to be added to this AnimationBundle
        :type animation: AnimationABC | Iterable[AnimationABC]
        :raises TypeError: The animation must inherit from AnimationABC or be an Iterable containing AnimationABC-inheriting instances.
        """
        if animation is None:
            pass
        elif isinstance(animation, AnimationABC):
            self._locker.update(animation.locker)
            self._animations.append(animation)
        elif isinstance(animation, Iterable):
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(f"'{_call_method}' is only implemented for types AnimationABC, Iterable[AnimationABC], and None, not for '{type(animation)}'")

    
    def __lshift__(self, other: Animation | Iterable[Animation]):
        """See :func:AnimationBundle.push"""
        self.push(other, _call_method="<<")

class UpdaterAnimation(Animation):
    """An UpdaterAnimation wraps around an Updater to make an Animation.
    
    This Animation runs the Updater's update once every advance (frame) for a specified duration.
    The first advance is counted as t=0 for the Updater.
    """
    def __init__(self, updater: Updater, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        super().__init__()
        self._duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration
        self._updater = updater
        self._locker = deepcopy(updater.locker)

        self._t = 0
        self._dt = 1/config.fps

    @property
    def locker(self):
        return self._locker

    def advance(self) -> bool:
        if self._t >= self._duration:
            return False

        self._updater.update(self._t, self._dt)
        self._t += self._dt
        return True

class AlphaAnimation(Animation):
    def __init__(self, *, fps: int | ConfigurationDeference = DEFER_TO_CONFIG, duration: float | ConfigurationDeference = DEFER_TO_CONFIG, easing_function: Callable[[float], float] = sin_easing2):
        super().__init__()
        fps = config.fps if fps is DEFER_TO_CONFIG else fps
        duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration

        self._frame_number: int = 1
        self._num_frames: int = round(fps * duration)
        self._easing_function = easing_function

    def advance(self) -> bool:
        if self._frame_number > self._num_frames:
            return False

        self.update(self._easing_function(self._frame_number/self._num_frames))

        self._frame_number += 1
        
        return True
            

    @abstractmethod
    def update(self, alpha: float):
        """
        Updates the object to be percentage alpha through the animation.
        """
        ...

class PathAnimation(AlphaAnimation):
    def __init__(self, transform: Transform, path: Path, **kwargs):
        super().__init__(**kwargs)
        self._transform = transform
        self._source_translation = self._transform.translation
        self._path = path

        self._locker = PropertyLocker()
        self._locker.add(self._transform, "translation")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._transform.translation = self._path.end

        self._transform.translation = self._path.point_percentage(alpha)


T = TypeVar('T')
_InterpolableLike = TypeVar('_InterpolableLike', bound=InterpolableLike)
class NotInterpolableError(ValueError):
    def __init__(self, property_name: str):
        super().__init__(f"'{property_name}' is not Interpolable.")
class PropertyAnimation(AlphaAnimation, Generic[T, _InterpolableLike]):
    def __init__(self, *, obj: T, destinations: list[_InterpolableLike], properties: list[str], initials: list[_InterpolableLike | None], **kwargs):
        super().__init__(**kwargs)
        self._obj = obj
        self._destinations = deepcopy(destinations)
        self._attributes = deepcopy(properties)
        self._initials: list[_InterpolableLike] = []
        self._locker = PropertyLocker()
        for attribute, initial in zip(self._attributes, initials):
            if not isinstance(getattr(obj, attribute), InterpolableLike):
                raise NotInterpolableError(attribute)
            self._initials.append(getattr(obj, attribute) if initial is None else initial)
            self._locker.add(obj, attribute)

    @property
    def locker(self):
        return self._locker

    def update(self, alpha: float):
        for attribute, initial, destination in zip(self._attributes, self._initials, self._destinations):
            setattr(self._obj, attribute, interpolate(initial, destination, alpha))


class TranslationAnimation(PropertyAnimation[Transform, Vec2 | Vec3]):
    def __init__(self, transform: Transform, target_translation: Vec2 | list, initial_translation: Vec2 | Vec3 | None = None,**kwargs):
        if isinstance(target_translation, Vec2):
            target_translation = target_translation.extend(transform.translation.z)
        super().__init__(
            obj=transform,
            properties=['translation'],
            destinations=[target_translation],
            initials=[initial_translation],
            **kwargs)

class ScaleAnimation(AlphaAnimation):
    def __init__(self, transform: Transform, target_scale: float | Vec3 | list, **kwargs):
        super().__init__(**kwargs)

        self._transform = transform
        self._source_scale = self._transform.scale

        
        self._target_scale = target_scale

        self._locker = PropertyLocker()
        self._locker.add(self._transform, "scale")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker

    def update(self, alpha: float):
        self._transform.scale = self._source_scale * (1 - alpha) + self._target_scale * alpha

class RotationAnimation(AlphaAnimation):
    def __init__(self, transform: Transform, target_rotation: float, **kwargs):
        super().__init__(**kwargs)
        self._transform = transform
        self._target_rotation = target_rotation
        self._source_rotation = self._transform.rotation

        self._locker = PropertyLocker()
        self._locker.add(self._transform, "rotation")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def update(self, alpha: float):
        self._transform.rotation = self._source_rotation * (1 - alpha) + self._target_rotation * alpha

class TransformAnimation(AlphaAnimation):
    """Animates a Transform linearly toward a target."""
    def __init__(self, transform: Transform, target: Transform, **kwargs):
        super().__init__(**kwargs)

        self._transform = transform
        self._target = Transform(target)
        self._source_transform = deepcopy(self._transform)


        self._locker = PropertyLocker()
        self._locker.add(self._transform, PropertyLocker.ALL_PROPERTIES)

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def update(self, alpha: float):
        self._transform.update(self._source_transform.interpolate(self._target, alpha))

class OpacityAnimation(AlphaAnimation):
    def __init__(self, color: Color | Element, target_opacity: float, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._target_opacity = target_opacity
        self._source_opacity = self._color.opacity


        self._locker = PropertyLocker()
        self._locker.add(self._color, "opacity")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def update(self, alpha: float):
        self._color.opacity = self._source_opacity * (1 - alpha) + self._target_opacity * alpha

class RgbAnimation(AlphaAnimation):
    def __init__(self, color: Color, target_rgb: Rgb, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._source_rgb = self._color.rgb
        
        if isinstance(target_rgb, str):
            target_rgb = Color.PALETTE[target_rgb]
        self._target_rgb = target_rgb

        self._locker = PropertyLocker()
        self._locker.add(self._color, "rgb")

    @property
    def locker(self) -> PropertyLocker:
        return self._locker
    
    def update(self, alpha: float):
        self._color.rgb = self._source_rgb.interpolate(self._target_rgb, alpha)


def fade_in(element: Element, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element in."""
    return OpacityAnimation(element, 1.0, **kwargs)

def fade_out(element: Element, **kwargs) -> Animation:
    """Returns an Animation to fade an Element out."""
    return OpacityAnimation(element, 0.0, **kwargs)

def flash(color: Color, rgb: str | Tuple[int, int, int], duration: float | ConfigurationDeference = DEFER_TO_CONFIG, **kwargs):
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration
    original_rgb = color.rgb
    return AnimationSequence(
        RgbAnimation(color, rgb, duration=duration/2, **kwargs),
        RgbAnimation(color, original_rgb, duration=duration/2, **kwargs)
    )

