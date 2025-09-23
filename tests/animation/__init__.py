from dataclasses import dataclass
from visuscript.lazy_object import Lazible

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