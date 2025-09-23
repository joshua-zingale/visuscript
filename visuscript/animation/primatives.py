from abc import ABC, abstractmethod
import typing as t

from visuscript.property_locker import PropertyLocker




class Animation(ABC):
    """Modifies one or more objects over time when added to a :class:`~visuscript.Scene`."""

    _num_processed_frames = 0
    _num_advances = 0
    _animation_speed = 1
    _keep_advancing = True


    def __init__(self):
        self.__locker__ = PropertyLocker()


    # TODO consider changing interface to return True if there is a next frame.
    # This would allow fractional speed controls
    @abstractmethod
    def advance(self) -> bool:
        """Makes the changes for one frame of the animation when at animation speed 1.

        :return: True if this Animation had any frames left before it was called.
        """
        ...

    def next_frame(self) -> bool:
        """Makes the changes for one frame of the animation, accounting for the set animation speed.

        :return: True if this Animation had any frames left before it was called.
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

    @property
    def locker(self) -> PropertyLocker:
        """
        The :class:`~visuscript.property_locker.PropertyLocker` identifying all objects/properties updated by this Animation.
        """
        return self.__locker__

    def finish(self) -> None:
        """
        Brings the animation to a finish instantly, leaving everything controlled by the animation in the state in which it would have been had the animation completed naturally.
        """
        while self.next_frame():
            pass

    def set_speed(self, speed: int) -> t.Self:
        """Sets the playback speed for this Animation.

        :param speed: The new duration of this :class:`Animation` will be duration/speed.
        :return: self
        """
        if not isinstance(speed, int) or speed <= 0:  # type: ignore
            raise ValueError("Animation speed must be a positive integer.")
        self._animation_speed = speed
        return self

    def compress(self) -> "_CompressedAnimation":
        """Returns a compressed version of this Animation.

        The _CompressedAnimation will have only a single advance (or frame), during which all of the advances (or frames) for this Animation will complete.
        """
        return _CompressedAnimation(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        return str(self)


class _CompressedAnimation(Animation):
    """:class:`_CompressedAnimation` wraps around another :class:`Animation`, compressing it into an :class:`Animation` with a single advance that runs all of the advances in the original :class:`Animation`."""

    def __init__(self, animation: Animation):
        super().__init__()
        self._animation = animation
        self.locker.update(animation.locker)

    def advance(self):
        advanced = False
        while self._animation.next_frame():
            advanced = True
        return advanced