from typing import Callable
from abc import ABC, abstractmethod
from visuscript.drawable import *
from visuscript.primatives import *
from visuscript.segments import Path
import numpy as np

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

    def finish(self):
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which they would have been had the animation completed naturally.
        """
        while self.advance():
            pass
        
class NoAnimation(Animation):

    def __init__(self, *, fps: int, duration: float):
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

    def __init__(self, animations: list[Animation]):
        self._animations = animations
        self._animation_index = 0

    def advance(self) -> bool:
        while self._animation_index < len(self._animations) and self._animations[self._animation_index].advance() == False:
            self._animation_index += 1

        if self._animation_index == len(self._animations):
            return False
        return True



class TimeDeltaAnimation(Animation):
    def __init__(self, *, fps: int, duration: float, updates_per_frame: int = 1):
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
    def __init__(self, *, fps: int, duration: float, easing_function: Callable[[float], float] = sin_easing):
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
        Updates the object to be percentage `alpha` through the animation.
        """
        ...


class PathAnimation(AlphaAnimation):
    def __init__(self, object: Drawable, path: Path, **kwargs):
        super().__init__(**kwargs)
        self._object = object
        self._source_translation = object.transform.translation
        self._path = path

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        if alpha == 1:
            self._object.transform.translation = self._path.end

        self._object.transform.translation = self._path.point_percentage(alpha)

class ScaleAnimation(AlphaAnimation):
    def __init__(self, object: Drawable, target_scale: float | np.ndarray | list, **kwargs):
        super().__init__(**kwargs)
        self._object = object
        self._source_scale = object.transform.scale
        self._target_scale = target_scale

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._object.transform.scale = self._source_scale * (1 - alpha) + self._target_scale * alpha

class RotationAnimation(AlphaAnimation):
    def __init__(self, object: Drawable, target_rotation: float, **kwargs):
        super().__init__(**kwargs)
        self._object = object
        self._source_rotation = object.transform.rotation
        self._target_rotation = target_rotation

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._object.transform.rotation = self._source_rotation * (1 - alpha) + self._target_rotation * alpha


class AnimationBundle(Animation):
    def __init__(self, animations: list[Animation] = []):
        self._animations: list[Animation] = animations
    
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
    def __init__(self, object: Drawable, target: Transform, fps: int, duration: float, easing_function: Callable[[float], float] = sin_easing):

        super().__init__()

        animations = [
            PathAnimation(object=object, path=Path().M(*object.transform.xy).L(*target.xy), fps = fps, duration = duration, easing_function = easing_function),
            ScaleAnimation(object=object, target_scale=target.scale, fps = fps, duration = duration, easing_function = easing_function),
            RotationAnimation(object=object, target_rotation=target.rotation, fps = fps, duration = duration, easing_function = easing_function)
        ]

        self._animation_bundle = AnimationBundle(animations)
    
    def advance(self) -> bool:
        return self._animation_bundle.advance()
        

class FillAnimation(AlphaAnimation):
    def __init__(self, object: Drawing, target_fill: Color, **kwargs):
        super().__init__(**kwargs)
        self._object = object
        self._source_color = Color(object.fill)
        self._target_color = Color(target_fill)

    def update(self, alpha: float):
        assert 0 <= alpha <= 1
        self._object.fill = self._source_color * (1 - alpha) + self._target_color * alpha