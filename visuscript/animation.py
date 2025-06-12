"""This module contains the abstract base class of all Animations alongside a bevy of basic animations and easing functions."""

from visuscript.config import *
from visuscript.element import Element
from visuscript.primatives import *
from visuscript.segment import Path
from visuscript._property_locker import PropertyLocker
from visuscript.updater import Updater
from visuscript._interpolable import InterpolableLike, interpolate
from visuscript._constructors import construct_vec3
from visuscript.lazy_object import evaluate_lazy, LazyObject
import numpy as np

from typing import Callable, Iterable, Generic, TypeVar
from abc import ABC, abstractmethod, ABCMeta
import inspect

from visuscript.config import config
def linear_easing(x: float) -> float:
    return x
def quintic_easing(x: float) -> float:
    return 6 * x**5 - 15 * x**4 + 10 * x**3
def sin_easing(a: float) -> float:
    return float(1 - np.cos(a*np.pi))/2
def sin_easing2(a: float) -> float:
    return sin_easing(sin_easing(a))


class AnimationMetaClass(ABCMeta):
    def __new__(meta, name, bases, attrs):

        # Set all parent classes' initializers to their default.
        for base in bases:
            if hasattr(base, "_original_init"):
                base.__init__ = base._original_init

        cls = super().__new__(meta, name, bases, attrs)
        # TODO see if there is any way to loosen requirement on signature
        if inspect.signature(cls.__init__) != inspect.signature(cls.init_locker):
            print(inspect.signature(cls.__init__), inspect.signature(cls.init_locker))
            raise TypeError(f"The '__init__' method and the 'init_locker' method must have the exact same signature for class '{cls.__name__}', including type hints, parameter names, parameter order, and keyword argument default values. This error could result from overloading one but not the other.")

        # TODO find a way around using "_is_lazy" because this hack is not good style
        # "_is_lazy" tracks what kind of initializer should be called
        cls._is_lazy = False
        # Set initializer to call init_locker unless the animation is lazy
        cls._original_init = cls.__init__
        def combined_init(self, *args, **kwargs):
            if self._is_lazy:
                self._init_args = args
                self._init_kwargs = kwargs
                self._locker = self.init_locker(*args, **kwargs)
                self._original_advance = self.advance
                def initializing_advance(*args, **kwargs):
                    init_args, init_kwargs = evaluate_lazy(self._init_args, self._init_kwargs)
                    self._original_init(*init_args, **init_kwargs)
                    self.advance = self._original_advance
                    return self.advance(*args, **kwargs)
                self.advance = initializing_advance
                cls._is_lazy = False
            else:
                for arg in [*args] + [*kwargs.values()]:
                    if isinstance(arg, LazyObject):
                        raise TypeError("Cannot pass a LazyObject as an argument to an Animation's initializer that is not being lazily constructed. Use Animation.lazy(...) to pass in LazyObject arguments.")
                self._locker = self.init_locker(*args, **kwargs)
                cls._original_init(self, *args, **kwargs)
        cls.__init__ = combined_init

        return cls


#TODO Remove FPS as a parameter for all Animations because set_speed on Updater assumes that the FPS will always match the config

class AnimationABC(ABC, metaclass=AnimationMetaClass):
    _num_processed_frames = 0
    _num_advances = 0
    _animation_speed = 1
    _keep_advancing = True
    _locker: PropertyLocker

    def __init__(self):
        ...
        

    @abstractmethod
    def init_locker(self):
        """initializes and returns a property locker for self."""
        ...

    def next_frame(self):
        """Makes the changes for one frame of the animation, accounting for the set animation speed.

        :return: True if this `Animation` had any frames left before it was called.
        :rtype: bool
        """
        self._num_advances += 1
        num_to_advance = int(self._animation_speed * self._num_advances - self._num_processed_frames)

        if self._keep_advancing:
            for _ in range(num_to_advance):
                if self._keep_advancing and not self.advance():
                    self._keep_advancing = False
                    break
            self._num_processed_frames += num_to_advance

        return self._keep_advancing

    # TODO consider changing interface to return True if there is a next frame.
    # This would allow fractional speed controls
    @abstractmethod
    def advance(self) -> bool:
        """Makes the changes for one frame of the animation when at animation speed 1.

        :return: True if this `Animation` had any frames left before it was called.
        :rtype: bool
        """        
        ...

    @property
    def locker(self) -> PropertyLocker:
        """
        The :class:`PropertyLocker` identifying all objects/properties updated by this Animation.
        """
        return self._locker

    def finish(self) -> None:
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which it would have been had the animation completed naturally.
        """
        while self.next_frame():
            pass

    def set_speed(self, speed: int) -> Self:
        """Sets the playback speed for this Animation.

        :param speed: The new duration of this :class:`Animation` will be duration*speed.
        :type speed: int
        :return: self
        :rtype: Self
        """
        if not isinstance(speed, int) or speed <= 0:
            raise ValueError("Animation speed must be a positive integer.")
        self._animation_speed = speed
        return self
    
    @classmethod
    def lazy(cls, *args, **kwargs) -> Self:
        """A constructor for a lazy version of this :class:`Animation`,
        in which the constructor is not called until the first advance.
        
        This differs from :class:`LazyAnimation` in that the arguments are evaluated when
        passed hereinto, whereas :class:`LazyAnimation` allows even the arguments to be
        evaluated lazily.

        :param *args: Positional arguments to be passed into this :class:`Animation`'s constructor.
        :param **kwargs: Keyword arguments to be passed into this :class:`Animation`'s constructor.
        :return: A lazy version of this :class:`Animation`
        :rtype: LazyAnimation
        """
        cls._is_lazy = True
        return cls(*args, **kwargs)

class CompressedAnimation(AnimationABC):
    """:class:`CompressedAnimation` wraps around another :class:`Animation`, compressing it into an :class:`Animation` with a single advance that runs all of the advances in the original :class:`Animation`."""
    def __init__(self, animation: AnimationABC):
        super().__init__()
        self._animation = animation

    def init_locker(self, animation: AnimationABC):
        return animation.locker
    
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
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    def __repr__(self) -> str:
        return str(self)
    

class LazyAnimation(Animation):
    """A LazyAnimation allows the initialization of an Animation to be delayed until its first advance.

    The passed-in callable must have no side effects because it is called twice: once to initialize the
    PropertyLocker and once to initialize the the Animation.
    
    A LazyAnimation can be useful when chaining together multiple animations in an AnimationSequence,
    where the initial state of one object being animated should not be determined until the previous animation completes.
    Often, Animation.lazy in conjuction with lazy arguments could and propably should be used instead of
    :class:`LazyAnimation`: it is in cases where the argumets cannot reasonably be made lazy that :class:`LazyAnimation`
    shines.
    """
    def __init__(self, animation_function: Callable[[], Animation]):
        super().__init__()
        self._animation_function = animation_function

    def init_locker(self, animation_function: Callable[[], Animation]):
        return deepcopy(animation_function().locker)
    
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

    def init_locker(self, *, fps: int | ConfigurationDeference = DEFER_TO_CONFIG, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
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

    def init_locker(self, function: Callable[[], None], consume_frame=False):
        return PropertyLocker()

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

    def init_locker(self, *animations: Animation):
        locker = PropertyLocker()
        for animation in filter(None, animations):
            locker.update(animation.locker, ignore_conflicts=True)
        return locker

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

        for animation in animations:
            self.push(animation, _update_locker=False)
                
    def init_locker(self, *animations: Animation):
        locker = PropertyLocker()
        for animation in filter(None, animations):
            locker.update(animation.locker)
        return locker
    
    def advance(self) -> bool:
        advance_made = sum(map(lambda x: x.next_frame(), self._animations)) > 0
        return advance_made
    
    def push(self, animation: AnimationABC | Iterable[AnimationABC], _call_method: str ="push", _update_locker: bool = True):
        """Adds an animation to this AnimationBundle.

        :param animation: The animation to be added to this AnimationBundle
        :type animation: AnimationABC | Iterable[AnimationABC]
        :raises TypeError: The animation must inherit from AnimationABC or be an Iterable containing AnimationABC-inheriting instances.
        """
        if animation is None:
            pass
        elif isinstance(animation, AnimationABC):
            if _update_locker:
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

        self._t = 0
        self._dt = 1/config.fps

    def init_locker(self, updater: Updater, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        return deepcopy(updater.locker)

    def advance(self) -> bool:
        if self._t >= self._duration:
            return False
        self._updater.update_for_frame()
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

    @abstractmethod
    def init_locker(self, *, fps: int | ConfigurationDeference = DEFER_TO_CONFIG, duration: float | ConfigurationDeference = DEFER_TO_CONFIG, easing_function: Callable[[float], float] = sin_easing2):
        ...

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

    def init_locker(self, transform: Transform, path: Path, **kwargs):
        return PropertyLocker({
            transform: ['translation']
            })
    
    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._transform.translation = self._path.end

        self._transform.translation = self._path.point_percentage(alpha)


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

    def init_locker(self, *, obj: T, destinations: list[InterpolableLike], properties: list[str], initials: list[InterpolableLike | None], **kwargs):
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
    def init_locker(self, transform: Transform, target_translation: Vec2 | list, initial_translation: Vec2 | Vec3 | None = None,**kwargs):
        return PropertyLocker({transform: ['translation']})

class ScaleAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_scale: float | Vec3 | list, initial_scale: int | float | Vec2 | Vec3 | None = None, **kwargs):
        super().__init__(
            obj=transform,
            properties=['scale'],
            destinations=[construct_vec3(target_scale, transform.translation.z)],
            initials=[construct_vec3(initial_scale, transform.translation.z)],
            **kwargs)
        
    def init_locker(self, transform: Transform, target_scale: float | Vec3 | list, initial_scale: int | float | Vec2 | Vec3 | None = None, **kwargs):
        return PropertyLocker({transform: ['scale']})

class RotationAnimation(PropertyAnimation[Transform]):
    def __init__(self, transform: Transform, target_rotation: float, initial_rotation: int | float | None = None, **kwargs):
        super().__init__(
            obj=transform,
            properties=['rotation'],
            destinations=[target_rotation, transform.translation.z],
            initials=[initial_rotation, transform.translation.z],
            **kwargs)
    def init_locker(self, transform: Transform, target_rotation: float, initial_rotation: int | float | None = None, **kwargs):
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
    def init_locker(self, transform: Transform, target_transform: Transform, initial_transform: Transform | None = None, **kwargs):
        return PropertyLocker({transform: ['translation','scale','rotation']})

class OpacityAnimation(PropertyAnimation[Color]):
    def __init__(self, color: Color | Element, target_opacity: float, initial_opacity: float | None = None, **kwargs):
        super().__init__(
            obj=color,
            properties=['opacity'],
            destinations=[target_opacity],
            initials=[initial_opacity],
            **kwargs)
    def init_locker(self, color: Color | Element, target_opacity: float, initial_opacity: float | None = None, **kwargs):
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
    def init_locker(self, color: Color, target_rgb: Rgb, initial_rgb: Rgb | str | None = None, **kwargs):
        return PropertyLocker({color: ['rgb']})


def fade_in(element: Element, **kwargs) -> OpacityAnimation:
    """Returns an Animation to fade an Element in."""
    return OpacityAnimation.lazy(element, 1.0, **kwargs)

def fade_out(element: Element, **kwargs) -> Animation:
    """Returns an Animation to fade an Element out."""
    return OpacityAnimation.lazy(element, 0.0, **kwargs)

def flash(color: Color, rgb: str | Tuple[int, int, int], duration: float | ConfigurationDeference = DEFER_TO_CONFIG, **kwargs):
    """Returns an Animation to flash a Color's rgb to another and then back to its original rgb.."""
    duration = config.animation_duration if duration is DEFER_TO_CONFIG else duration
    return AnimationSequence(
        RgbAnimation.lazy(color, rgb, duration=duration/2, **kwargs),
        RgbAnimation.lazy(color, color.rgb, duration=duration/2, **kwargs)
    )

