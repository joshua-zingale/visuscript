from abc import ABC, abstractmethod
from visuscript.primatives import Transform
from visuscript.property_locker import PropertyLocker
from typing import Iterable, Self, Callable
import numpy as np

class UpdaterActivityError(ValueError):
    pass
class UpdaterAlreadyActiveError(UpdaterActivityError):
    pass
class UpdaterAlreadyDeactiveError(UpdaterActivityError):
    pass

class Updater(ABC):
    
    @property
    def active(self) -> bool:
        """Whether this Updater is active or not."""
        if not hasattr(self, '_active'):
            self._active = True
        return self._active
    
    def activate(self):
        """Activate this Updater."""
        if self._active:
            raise UpdaterAlreadyActiveError()
        self._active = True

    def deactivate(self):
        """Deactivate this Updater."""
        if not self._active:
            raise UpdaterAlreadyDeactiveError()
        self._active = True

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


class UpdaterBundle(Updater):
    def __init__(self, *updaters: Updater):
        self._updaters: list[Updater] = []
        self._locker: PropertyLocker = PropertyLocker()

        for updater in updaters:
            self.push(updater)

    def update(self, t: float, dt: float) -> Self:
        i = 0
        for updater in filter(lambda u: u.active, self._updaters):
            updater.update(t, dt)
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

    def __init__(self, transform: Transform, target: Transform, *, max_velocity: float | None = None, acceleration: float | None = None):
        self._transform = transform
        self._target = target
        self._max_velocity = max_velocity
        self._acceleration = acceleration

        self._locker = PropertyLocker()
        self._locker.add(transform, "translation")

        self._last_speed = 0.0

    @property
    def locker(self):
        return self._locker

    def update(self, t: float, dt: float) -> Self:

        if self._max_velocity is None and self._acceleration is None:
            self._transform.translation = self._target.translation
            return

        diff = self._target.translation - self._transform.translation
        dist = np.linalg.norm(diff)
        unit = diff/max(dist, 1e-16)
        

        if self._acceleration is None:
            max_velocity = self._max_velocity
        else:
            # Determine whether to increase or decrease velocity
            min_time_to_stop = self._last_speed/self._acceleration
            slowdown_distance = self._last_speed * min_time_to_stop - self._acceleration * min_time_to_stop**2 / 2
            acceleration = self._acceleration if dist > slowdown_distance else -self._acceleration



            max_velocity = min(self._last_speed + acceleration * dt, self._max_velocity or np.inf)
            self._last_speed = max_velocity

            desired_speed = dist/dt
            if desired_speed > max_velocity:
                self._transform.translation += unit*max_velocity*dt
            else:
                self._transform.translation = self._target.translation

        return self



