"""This module contains the abstract base class of all Animations alongside a bevy of basic animations and easing functions."""

from visuscript.config import *
from visuscript.primatives import *
from visuscript.segment import Path
from visuscript.property_locker import PropertyLocker
from visuscript.updater import Updater
from visuscript.lazy_object import evaluate_lazy, LazyObject


from typing import Callable, no_type_check
from abc import ABC, abstractmethod, ABCMeta
import inspect

from .easing import sin_easing2

from visuscript.config import config


class AnimationMetaClass(ABCMeta):
    @no_type_check
    def __new__(meta, name, bases, attrs):
        # Set all parent classes' initializers to their default.
        for base in bases:
            if hasattr(base, "_original_init"):
                base.__init__ = base._original_init

        cls = super().__new__(meta, name, bases, attrs)
        # TODO see if there is any way to loosen requirement on signature
        if (
            inspect.signature(cls.__init__).parameters
            != inspect.signature(cls.__init_locker__).parameters
        ):
            print(
                inspect.signature(cls.__init__), inspect.signature(cls.__init_locker__)
            )
            raise TypeError(
                f"The '__init__' method and the '__init_locker__' method must have the exact same signature for class '{cls.__name__}', including type hints, parameter names, parameter order, and keyword argument default values. This error could result from overloading one but not the other."
            )

        # TODO find a way around using "_is_lazy" because this hack is not good style
        # "_is_lazy" tracks what kind of initializer should be called
        cls._is_lazy = False
        # Set initializer to call __init_locker__ unless the animation is lazy
        cls._original_init = cls.__init__

        @no_type_check
        def combined_init(self, *args, **kwargs):
            if self._is_lazy:
                self._init_args = args
                self._init_kwargs = kwargs
                self._locker = self.__init_locker__(*args, **kwargs)
                self._original_advance = self.advance

                def initializing_advance(*args, **kwargs):
                    init_args, init_kwargs = evaluate_lazy(
                        self._init_args, self._init_kwargs
                    )
                    self._original_init(*init_args, **init_kwargs)
                    self.advance = self._original_advance
                    return self.advance(*args, **kwargs)

                self.advance = initializing_advance
                cls._is_lazy = False
            else:
                for arg in [*args] + [*kwargs.values()]:
                    if isinstance(arg, LazyObject):
                        raise TypeError(
                            "Cannot pass a LazyObject as an argument to an Animation's initializer that is not being lazily constructed. Use Animation.lazy(...) to pass in LazyObject arguments."
                        )
                self._locker = self.__init_locker__(*args, **kwargs)
                cls._original_init(self, *args, **kwargs)

        cls.__init__ = combined_init

        return cls


# TODO Remove FPS as a parameter for all Animations because set_speed on Updater assumes that the FPS will always match the config


class AnimationABC(ABC, metaclass=AnimationMetaClass):
    _num_processed_frames = 0
    _num_advances = 0
    _animation_speed = 1
    _keep_advancing = True
    _locker: PropertyLocker

    def __init__(self): ...

    @abstractmethod
    def __init_locker__(self) -> PropertyLocker:
        """initializes and returns a property locker for self."""
        ...

    def next_frame(self):
        """Makes the changes for one frame of the animation, accounting for the set animation speed.

        :return: True if this `Animation` had any frames left before it was called.
        :rtype: bool
        """
        self._num_advances += 1
        num_to_advance = int(
            self._animation_speed * self._num_advances - self._num_processed_frames
        )

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

    def __init_locker__(self, animation: AnimationABC):  # type: ignore[reportIncompatibleMethodOverride]
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

    def __init__(self, animation_function: Callable[[], Animation]):  # type: ignore[reportIncompatibleMethodOverride]
        super().__init__()
        self._animation_function = animation_function

    def __init_locker__(self, animation_function: Callable[[], Animation]):  # type: ignore[reportIncompatibleMethodOverride]
        return deepcopy(animation_function().locker)

    def advance(self):
        if not hasattr(self, "_animation"):
            self._animation: Animation = self._animation_function()
        return self._animation.next_frame()


class NoAnimation(Animation):
    """A NoAnimation makes no changes to any object's state.

    A NoAnimation can be used to rest at the current state for a specified duration.
    """

    def __init__(
        self,
        *,
        fps: int | ConfigurationDeference = DEFER_TO_CONFIG,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        super().__init__()
        fps = config.fps if fps is DEFER_TO_CONFIG else fps
        duration = (
            config.animation_duration if duration is DEFER_TO_CONFIG else duration
        )

        self._num_frames = round(fps * duration)

    def __init_locker__(
        self,
        *,
        fps: int | ConfigurationDeference = DEFER_TO_CONFIG,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
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

    def __init_locker__(self, function: Callable[[], None], consume_frame=False):  # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker()

    def advance(self) -> bool:
        if not self._has_been_run:
            self._function()
            self._has_been_run = True
            return self._consume_frame
        return False


class UpdaterAnimation(Animation):
    """An UpdaterAnimation wraps around an Updater to make an Animation.

    This Animation runs the Updater's update once every advance (frame) for a specified duration.
    The first advance is counted as t=0 for the Updater.
    """

    def __init__(
        self,
        updater: Updater,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        super().__init__()
        self._duration = (
            config.animation_duration if duration is DEFER_TO_CONFIG else duration
        )
        self._updater = updater

        self._t = 0
        self._dt = 1 / config.fps

    def __init_locker__(
        self,
        updater: Updater,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):  # type: ignore[reportIncompatibleMethodOverride]
        return deepcopy(updater.locker)

    def advance(self) -> bool:
        if self._t >= self._duration:
            return False
        self._updater.update_for_frame()
        self._t += self._dt
        return True


class AlphaAnimation(Animation):
    def __init__(
        self,
        *,
        fps: int | ConfigurationDeference = DEFER_TO_CONFIG,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
        easing_function: Callable[[float], float] = sin_easing2,
    ):
        super().__init__()
        fps = config.fps if fps is DEFER_TO_CONFIG else fps
        duration = (
            config.animation_duration if duration is DEFER_TO_CONFIG else duration
        )

        self._frame_number: int = 1
        self._num_frames: int = round(fps * duration)
        self._easing_function = easing_function

    @abstractmethod
    def __init_locker__(
        self,
        *,
        fps: int | ConfigurationDeference = DEFER_TO_CONFIG,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
        easing_function: Callable[[float], float] = sin_easing2,
    ):  # type: ignore[reportIncompatibleMethodOverride]
        ...

    def advance(self) -> bool:
        if self._frame_number > self._num_frames:
            return False

        self.update(self._easing_function(self._frame_number / self._num_frames))

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

    def __init_locker__(self, transform: Transform, path: Path, **kwargs):  # type: ignore[reportIncompatibleMethodOverride]
        return PropertyLocker({transform: ["translation"]})

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._transform.translation = self._path.end

        self._transform.translation = self._path.point_percentage(alpha)
