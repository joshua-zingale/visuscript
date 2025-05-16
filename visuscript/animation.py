from typing import Callable, Tuple
from abc import ABC, abstractmethod
from visuscript.config import *
from visuscript.drawable import Drawable
from visuscript.element import Drawing
from visuscript.primatives import *
from visuscript.segment import Path
import numpy as np

from visuscript.config import config

def quintic_easing(x: float) -> float:
    return 6 * x**5 - 15 * x**4 + 10 * x**3

def sin_easing(a: float) -> float:
    return float(1 - np.cos(a*np.pi))/2

class Animation(ABC):

    @abstractmethod
    def advance(self) -> bool:
        """
        Makes the changes for one frame of the animation.

        Returns True if there is a next frame for the animation or if the current advance was the last frame; else returns False.
        """
        ...

    @property
    def properties(self) -> dict[object, list[str]]:
        """
        Returns a dictionary maping objects that are animated by this Animation to the properties on those objects being animated.

        If no properties are listed for an object, it is assumed that all properties are being used by this Animation.
        """
        return dict()
    

    def contradicts(self, other: "Animation") -> bool:
        """
        Returns True if this Animation and `other` animate same property on the same object.
        """
        for obj in self.properties:
            if obj in other:
                if len(self.properties[obj]) * len(other.properties[obj]) == 0:
                    return True
                for property in self.properties[obj]:
                    if property in other.properties[obj]:
                        return True
        return False
                

    def finish(self):
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which they would have been had the animation completed naturally.
        """
        while self.advance():
            pass
        
class NoAnimation(Animation):

    def __init__(self, *, fps: int = config.fps, duration: float = config.animation_duration):
        self._num_frames = round(fps*duration)

    def advance(self) -> bool:
        if self._num_frames > 0:
            self._num_frames -= 1
            return True
        return False
    
class RF(Animation):

    def __init__(self, function: Callable[[], None]):
        self._function = function

    def advance(self) -> bool:
        self._function()
        return False
    
class AnimationSequence(Animation):

    def __init__(self, *animations: Tuple[Animation, ...]):
        self._animations = animations
        self._animation_index = 0

    def advance(self) -> bool:
        while self._animation_index < len(self._animations) and self._animations[self._animation_index].advance() == False:
            self._animation_index += 1

        if self._animation_index == len(self._animations):
            return False
        return True



class TimeDeltaAnimation(Animation):
    def __init__(self, *, fps: int = config.fps, duration: float = config.animation_duration, updates_per_frame: int = 1):
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
    def __init__(self, *, fps: int = config.fps, duration: float = config.animation_duration, easing_function: Callable[[float], float] = sin_easing):
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


class PathAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, path: Path, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        self._path = path

    def first_advance_initializer(self):
        self._source_translation = self._drawable.transform.translation


    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._drawable.transform.translation = self._path.end

        self._drawable.transform.translation = self._path.point_percentage(alpha)

class TranslationAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, target_translation: np.ndarray | list, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable


        self._target_translation = Transform(target_translation).translation

    def first_advance_initializer(self):
        self._source_translation = self._drawable.transform.translation


    def update(self, alpha: float):
        assert 0 <= alpha <= 1

        self._drawable.transform.translation = self._source_translation * (1 - alpha) + self._target_translation * alpha

class ScaleAnimation(AlphaAnimation):
    def __init__(self, drawable: Drawable, target_scale: float | np.ndarray | list, **kwargs):
        super().__init__(**kwargs)
        self._drawable = drawable
        
        self._target_scale = target_scale

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

    def first_advance_initializer(self):
        self._source_rotation = self._drawable.transform.rotation

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._drawable.transform.rotation = self._source_rotation * (1 - alpha) + self._target_rotation * alpha


class AnimationBundle(Animation):
    def __init__(self, *animations: Tuple[Animation, ...]):
        self._animations: list[Animation] = []

        for animation in animations:
            self.push(animation)
    
    def advance(self) -> bool:
        return sum(map(lambda x: x.advance(), self._animations)) > 0
    
    def push(self, animation: Animation | list[Animation]):
        if isinstance(animation, Animation):
            self._animations.append(animation)
        elif isinstance(animation, list):
            self._animations.extend(animation)
        else:
            raise TypeError(f"'<<' is only implemented for types Animation and list[Animation], not for '{type(animation)}'")


    def clear(self):
        self._animations = []
    
    def __lshift__(self, other: Animation | list[Animation]):
        self.push(other)


class TransformInterpolation(Animation):
    def __init__(self, drawable: Drawable, target: Transform, fps: int = config.fps, duration: float = config.animation_duration, easing_function: Callable[[float], float] = sin_easing):

        super().__init__()

        animations = [
            TranslationAnimation(drawable=drawable, target_translation=target.translation, fps=fps, duration=duration, easing_function=easing_function),
            ScaleAnimation(drawable=drawable, target_scale=target.scale, fps = fps, duration = duration, easing_function = easing_function),
            RotationAnimation(drawable=drawable, target_rotation=target.rotation, fps = fps, duration = duration, easing_function = easing_function)
        ]

        self._animation_bundle = AnimationBundle(animations)
    
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