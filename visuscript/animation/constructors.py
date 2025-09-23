import typing as t
from dataclasses import dataclass

from visuscript.property_locker import PropertyLocker
from visuscript.lazy_object import evaluate_lazy
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG

from .easing import linear_easing
from .primatives import Animation
from .animation_store import AnimationSequence, AnimationBundle
from .protocols import InterpolationFunction, Keyframe, Setter




_P = t.ParamSpec("_P")
_T = t.TypeVar("_T")
def construct(advancer: t.Callable[[_T], _T | None], initial_state: _T, locker: t.Optional[PropertyLocker] = None) -> Animation:
    """Builds a new :class:`~visuscript.Animation`.

    :param advancer: A function that processes one frame of the animation.
        This function should mutate any objects that are to be animated.
        The function has one parameter, which should store the state of the :class:`~visuscript.Animation`;
        then the function must then return a modified state object,
        which will be the input to the `advancer` for the next frame.
    :param initial_state: The argument passed into the `advancer` before the first frame of
        the :class:`~visuscript.Animation` is generated.
    :param locker: The property locker that indicates all objects (and the properties thereof)
        that are animated by the constructed :class:`~visuscript.Animation`.
    :return: The constructed :class:`~visuscript.Animation`. 
    """
    return _ConstructedAnimation(advancer, locker, initial_state)


def sequence(*animations: Animation | None) -> AnimationSequence:
    return AnimationSequence(*animations)
def bundle(*animations: Animation | None) -> AnimationBundle:
    return AnimationBundle(*animations)


@t.overload
def laze(animation_factory: t.Callable[_P, Animation], /, *args: _P.args, **kwargs: _P.kwargs) -> Animation:
    """Turns an animation factory into one that accepts lazy arguments that are not evaluated
    until the first advance."""
@t.overload
def laze(locker: PropertyLocker, animation_factory: t.Callable[_P, Animation], /, *args: _P.args,**kwargs: _P.kwargs) -> Animation:
    """Turns an animation factory into one that accepts lazy arguments that are not evaluated
    until the first advance."""
def laze(*args: t.Any, **kwargs: t.Any) -> Animation:
    if isinstance(args[0], PropertyLocker):
        return _LazyAnimation(args[1], args[0], *args[2:], **kwargs)
    return _LazyAnimation(args[0], None, *args[1:], **kwargs)


class HasFrameState(t.Protocol):
    @property
    def num_total_frames(self) -> int: ...
    @property
    def num_processed_frames(self) -> int: ...



@dataclass
class FrameState:
    num_total_frames: int
    num_processed_frames: int

def keyframe_construct(setter: Setter[_T], num_frames: int, interpolation_function: InterpolationFunction[_T], first_keyframe: Keyframe[_T], keyframes: t.Sequence[Keyframe[_T]], easing_function: t.Callable[[float], float] = linear_easing, locker: t.Optional[PropertyLocker] = None) -> Animation:

    def alpha_animation(state: FrameState) -> FrameState | None:
        if state.num_processed_frames == state.num_total_frames:
            return None
        state.num_processed_frames += 1
        alpha =  easing_function(state.num_processed_frames / state.num_total_frames)
        setter(interpolation_function(alpha, first_keyframe, *keyframes).get_interpolated_object())
        return state

    return construct(alpha_animation, FrameState(num_total_frames=num_frames, num_processed_frames=0), locker=locker)



class _ConstructedAnimation(Animation, t.Generic[_T]):
    def __init__(self, advancer: t.Callable[[_T], _T | None], locker: t.Optional[PropertyLocker], initial_state: _T):
        super().__init__()
        self._state = initial_state
        if locker:
            self.locker.update(locker)
        self._advancer = advancer

    def advance(self) -> bool:
        maybe_next_state = self._advancer(self._state)
        if maybe_next_state:
            self._state = maybe_next_state
            return True
        return False
    
class _LazyAnimation(Animation, t.Generic[_P]):
    def __init__(self, animation_factory: t.Callable[_P, Animation], locker: t.Optional[PropertyLocker],  *args: _P.args, **kwargs: _P.kwargs):
        super().__init__()
        self._animation_factory = animation_factory
        if locker:
            self.locker.update(locker)
        self._init_args = args
        self._init_kwargs = kwargs
        self._animation: Animation | None = None

    @t.no_type_check
    def advance(self):
        self._init_args, self._init_kwargs = evaluate_lazy(self._init_args, self._init_kwargs)
        self._animation = self._animation_factory(*self._init_args, **self._init_kwargs)
        del self._init_args, self._init_kwargs

        val = self._advance()
        self.advance = self._advance
        return val
    
    def _advance(self) -> bool:
        assert self._animation is not None
        return self._animation.next_frame()
    

def duration_to_frame_count(seconds: float | ConfigurationDeference = DEFER_TO_CONFIG) -> int:
    seconds = config.animation_duration if isinstance(seconds, ConfigurationDeference) else seconds
    return round(seconds * config.fps)