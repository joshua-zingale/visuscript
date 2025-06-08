"""This module contains the abstract base class of all updaters alongside a bevy of basic updaters"""

from abc import ABC, abstractmethod, ABCMeta
from visuscript.primatives import Transform
from visuscript._property_locker import PropertyLocker
from visuscript.math_utility import magnitude
from visuscript.config import config
from typing import Iterable, Self, Callable
import numpy as np

class UpdaterActivityError(ValueError):
    pass
class UpdaterAlreadyActiveError(UpdaterActivityError):
    pass
class UpdaterAlreadyDeactiveError(UpdaterActivityError):
    pass

class Updater(ABC):
    _num_frames = 0
    _updates_per_second = config.fps
    _updates_per_frame = 1
    _num_updates_processed = 0
    _active = True

    @property
    def active(self) -> bool:
        """Whether this Updater is active or not."""
        return self._active
    
    def activate(self):
        """Activate this Updater."""
        if self._active:
            raise UpdaterAlreadyActiveError()
        self._active = False

    def deactivate(self):
        """Deactivate this Updater."""
        if not self._active:
            raise UpdaterAlreadyDeactiveError()
        self._active = True

    def update_for_frame(self) -> Self:
        self._num_frames += 1
        num_updates_to_make = int(self._num_frames * self._updates_per_frame - self._num_updates_processed)
        sub_dt = 1 / self._updates_per_second
        for i in range(num_updates_to_make):
            self.update(self._num_updates_processed/self._updates_per_second, sub_dt)

        self._num_updates_processed += num_updates_to_make

        return self

    @property
    @abstractmethod
    def locker(self) -> PropertyLocker:
        """
        Returns a PropertyLocker identifying all objects/properties updated by this Updater.
        """
        ...
    
    @abstractmethod
    def update(self, t: float, dt: float) -> Self:
        """Makes this Updater's update."""
        ...

    def set_update_rate(self, updates_per_second: float) -> Self:
        """Sets the rate that updates occur for this Updater.
        
        By default, an Updater will execute once for each frame inside of a Scene.
        If this is set, then the updater can run more
        or less often than once per frame.
        """
        if not isinstance(updates_per_second, (int, float)) or updates_per_second <= 0:
            raise ValueError("Update rate must be a positive number.")
        self._updates_per_second = updates_per_second
        self._updates_per_frame = updates_per_second/config.fps
        return self


class UpdaterBundle(Updater):
    def __init__(self, *updaters: Updater):
        self._updaters: list[Updater] = []
        self._locker: PropertyLocker = PropertyLocker()

        for updater in updaters:
            self.push(updater)

    def update(self, t: float, dt: float) -> Self:
        for updater in filter(lambda u: u.active, self._updaters):
            updater.set_update_rate(config.fps).update(t, dt)
        return self

    @property
    def locker(self):
        return self._locker

    def push(self, updater: Updater | Iterable[Updater], _call_method="push"):
        if isinstance(updater, Updater):
            self._locker.update(updater.locker)
            self._updaters.append(updater)
        elif isinstance(updater, Iterable):
            for updater_ in updater:
                self.push(updater_)
        else:
            raise TypeError(f"Cannot push type '{updater.__class__.__name__}' to '{self.__class__.__name__}': must push types 'Updater' or 'Iterable[Updater]' ")


    def __lshift__(self, other: Updater | Iterable[Updater]):
        self.push(other, _call_method="<<")


    def clear(self):
        self._updaters = []
        self._locker = PropertyLocker()


class FunctionUpdater(Updater):
    def __init__(self, function: Callable[[float, float], None]):
        self._function = function
        self._locker = PropertyLocker()
    
    @property
    def locker(self):
        return self._locker
    
    def update(self, t, dt) -> Self:
        self._function(t, dt)
        return self



class TranslationUpdater(Updater):

    def __init__(self, transform: Transform, target: Transform, *, max_speed: float | None = None, acceleration: float | None = None):
        self._transform = transform
        self._target = target
        self._max_speed = max_speed
        self._acceleration = acceleration

        self._locker = PropertyLocker()
        self._locker.add(transform, "translation")

        self._last_speed = 0.0

    @property
    def locker(self):
        return self._locker

    def update(self, t: float, dt: float) -> Self:

        if self._max_speed is None and self._acceleration is None:
            self._transform.translation = self._target.translation
            return

        diff = self._target.translation - self._transform.translation
        dist = magnitude(diff)
        unit = diff/max(dist, 1e-16)
        

        if self._acceleration is None:
            max_speed = self._max_speed
            if max_speed*dt < dist:
                self._transform.translation += unit*max_speed*dt
            else:
                self._transform.translation = self._target.translation
        else:
            # Determine whether to increase or decrease velocity
            min_time_to_stop = self._last_speed/self._acceleration
            slowdown_distance = self._last_speed * min_time_to_stop - self._acceleration * min_time_to_stop**2 / 2
            acceleration = self._acceleration if dist > slowdown_distance else -self._acceleration


            max_speed = min(self._last_speed + acceleration * dt, self._max_speed or np.inf)
            self._last_speed = max_speed

            desired_speed = dist/dt
            if desired_speed > max_speed:
                self._transform.translation += unit*max_speed*dt
            else:
                self._transform.translation = self._target.translation

        return self



def run_updater(updater: Updater, duration: float):
    t = 0
    dt = 1/config.fps

    for _ in range(duration*config.fps):
        updater.update(t, dt)
        t += dt





