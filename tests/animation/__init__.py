from dataclasses import dataclass
from visuscript.lazy_object import Lazible
from visuscript.animation import Animation
from visuscript.config import config
from visuscript.property_locker import PropertyLocker


def run_for(animation: Animation, duration: int):
    total_frames = config.fps * duration
    for _ in range(total_frames):
        animation.advance()


def number_of_frames(animation: Animation):
    num_frames = 0
    while animation.next_frame():
        num_frames += 1
    return num_frames


class WFloat(float):
    def get_interpolated_object(self):
        return self
    def __add__(self, other):
        return WFloat(float(self) + other)
    def __sub__(self, other):
        return WFloat(float(self) - other)
    def __mul__(self, other):
        return WFloat(float(self) * other)
    def __rmul__(self, other):
        return WFloat(float(self) * other)
    def __truediv__(self, other):
        return WFloat(float(self) / other)
    def __rtruediv__(self, other: float):
        return WFloat(other / float(self))
    
@dataclass
class MockObject(Lazible):
    x: float 
    def __eq__(self, other: object) -> bool:
        return isinstance(other, MockObject) and self.x == other.x
    def __hash__(self) -> int:
        return hash(self.x)
    
class WMockObject(Lazible):

    def __init__(self, x: float):
        self._x = WFloat(x)

    def set_x(self, x: float):
        self._x = WFloat(x)
        return self
    
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, other: float):
        self._x = WFloat(other)


    def __eq__(self, other: object) -> bool:
        return isinstance(other, MockObject) and self.x == other.x
    def __hash__(self) -> int:
        return hash(self.x)

@dataclass
class MockAnimationState:
    obj: MockObject
    start: float
    destination: float
    total_frames: int
    num_processed_frames: int = 0


class MockAnimation(Animation):
    actual_advaces = 0
    total_advances = 0

    def __init__(
        self,
        total_advances,
        obj: list[int] = [0],
        adder: int = 1,
        locked: dict[object, list[str]] = dict(),
    ):
        super().__init__()
        self.actual_advances = 0
        self.total_advances = total_advances
        self.obj = obj
        self.obj_value = obj[0]
        self.adder = adder
        self.__locker__ = PropertyLocker(locked) # type: ignore

    def advance(self):
        self.actual_advances += 1
        if self.actual_advances > self.total_advances:
            return False
        self.obj[0] = self.obj_value + self.adder
        return True
    