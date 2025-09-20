from .animation import Animation, AnimationABC
from visuscript.property_locker import PropertyLocker

from typing import Iterable, Self


class AnimationSequence(Animation):
    """An AnimationSequence runs through Animations in sequence.

    An AnimationSequence can be used to play multiple animation, one after another.
    """

    def __init__(self, *animations: AnimationABC | None):
        super().__init__()
        self._animations: list[AnimationABC] = []
        self._animation_index = 0
        self._locker = PropertyLocker()

        for animation in animations:
            self.push(animation)

    def __init_locker__(self, *animations: AnimationABC | None):
        locker = PropertyLocker()
        for animation in filter(None, animations):
            locker.update(animation.locker, ignore_conflicts=True)
        return locker

    def advance(self) -> bool:
        while (
            self._animation_index < len(self._animations)
            and self._animations[self._animation_index].next_frame() == False
        ):
            self._animation_index += 1

        if self._animation_index == len(self._animations):
            return False
        return True

    def push(
        self,
        animation: AnimationABC | Iterable[AnimationABC | None] | None,
        _call_method: str = "push",
    ) -> Self:
        """Adds an Animation to the end sequence."""
        if animation is None:
            pass
        elif isinstance(animation, AnimationABC):
            self._locker.update(animation.locker, ignore_conflicts=True)
            self._animations.append(animation)
        elif isinstance(animation, Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Animation and Iterable[Animation], not for '{type(animation)}'"
            )
        return self

    def __lshift__(self, other: AnimationABC | Iterable[AnimationABC | None] | None):
        """See :meth:AnimationSequence.push"""
        self.push(other, _call_method="<<")


class AnimationBundle(Animation):
    """An AnimationBundle combines multiple Animation instances into one concurrent Animation.

    An AnimationBundle can be used to play multiple Animation concurrently.
    """

    def __init__(self, *animations: AnimationABC | None):
        super().__init__()
        self._animations: list[AnimationABC] = []

        for animation in animations:
            self.push(animation, _update_locker=False)

    def __init_locker__(self, *animations: AnimationABC | None):
        locker = PropertyLocker()
        for animation in filter(None, animations):
            locker.update(animation.locker)
        return locker

    def advance(self) -> bool:
        advance_made = sum(map(lambda x: x.next_frame(), self._animations)) > 0
        return advance_made

    def push(
        self,
        animation: AnimationABC | Iterable[AnimationABC | None] | None,
        _call_method: str = "push",
        _update_locker: bool = True,
    ) -> Self:
        """Adds an animation to this bundle."""
        if animation is None:
            pass
        elif isinstance(animation, AnimationABC):
            if _update_locker:
                self._locker.update(animation.locker)
            self._animations.append(animation)
        elif isinstance(animation, Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types AnimationABC, Iterable[AnimationABC], and None, not for '{type(animation)}'"
            )
        return self

    def __lshift__(self, other: AnimationABC | Iterable[AnimationABC] | None):
        """See :meth:AnimationBundle.push"""
        self.push(other, _call_method="<<")
