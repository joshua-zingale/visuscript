import typing as t

from .primatives import Animation

class AnimationSequence(Animation):
    """An AnimationSequence runs through Animations in sequence.

    An AnimationSequence can be used to play multiple animation, one after another.
    """

    def __init__(self, *animations: Animation | None):
        super().__init__()
        self._animations: list[Animation] = []
        self._animation_index = 0

        for animation in animations:
            self.push(animation)

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
        animation: Animation | t.Iterable[Animation | None] | None,
        _call_method: str = "push",
    ) -> t.Self:
        """Adds an Animation to the end sequence."""
        if animation is None:
            pass
        elif isinstance(animation, Animation):
            self.locker.update(animation.locker, ignore_conflicts=True)
            self._animations.append(animation)
        elif isinstance(animation, t.Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Animation and Iterable[Animation], not for '{type(animation)}'"
            )
        return self

    def __lshift__(self, other: Animation | t.Iterable[Animation | None] | None):
        """See :meth:AnimationSequence.push"""
        self.push(other, _call_method="<<")


class AnimationBundle(Animation):
    """An AnimationBundle combines multiple Animation instances into one concurrent Animation.

    An AnimationBundle can be used to play multiple Animation concurrently.
    """

    def __init__(self, *animations: Animation | None):
        super().__init__()
        self._animations: list[Animation] = []

        for animation in animations:
            self.push(animation)

    def advance(self) -> bool:
        advance_made = sum(map(lambda x: x.next_frame(), self._animations)) > 0
        return advance_made

    def push(
        self,
        animation: Animation | t.Iterable[Animation | None] | None,
        _call_method: str = "push",
    ) -> t.Self:
        """Adds an animation to this bundle."""
        if animation is None:
            pass
        elif isinstance(animation, Animation):
            self.locker.update(animation.locker)
            self._animations.append(animation)
        elif isinstance(animation, t.Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for animation_ in animation:
                self.push(animation_)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Animation, Iterable[Animation], and None, not for '{type(animation)}'"
            )
        return self

    def __lshift__(self, other: Animation | t.Iterable[Animation] | None):
        """See :meth:AnimationBundle.push"""
        self.push(other, _call_method="<<")
