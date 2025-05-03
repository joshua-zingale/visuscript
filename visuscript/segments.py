import numpy as np
from typing import Self

class Segment:
    def point_percentage(self, percentage: float):
        assert 0 <= percentage and percentage <= 1
        return self.point(percentage * self.arc_length)

    def point(self, length: float) -> np.ndarray:
        raise NotImplementedError()

    @property
    def arc_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def start(self) -> np.ndarray:
        raise NotImplementedError()
    
    @property
    def end(self) -> np.ndarray:
        raise NotImplementedError()
    
    def __str__(self) -> str:
        raise NotImplementedError()
    

class MSegment(Segment):
    def __init__(self, x1: float, y1: float):
        self._x1 = x1
        self._y1 = y1
        
    @property
    def start(self) -> np.ndarray:
        return np.array([self._x1, self._y1],dtype=float)

    def point(self, length: float) -> np.ndarray:
        assert length == 0
        return np.array([self._x1, self._y1],dtype=float)

    @property
    def arc_length(self) -> float:
        return 0.0
    
    @property
    def end(self) -> np.ndarray:
        return np.array([self._x1, self._y1],dtype=float)
    
    def __str__(self) -> str:
        return f"M {self._x1} {self._y1}"


class LinearSegment(Segment):
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    def point(self, length: float) -> np.ndarray:
        assert 0 <= length and length <= self.arc_length
        p = length / self.arc_length
        return np.array([
            self._x2 * p + self._x1 * (1 - p),
            self._y2 * p + self._y1 * (1 - p)
        ])

    @property
    def arc_length(self) -> float:
        return np.sqrt( (self._x2 - self._x1)**2 + (self._y2 - self._y1)**2)
    
    @property
    def start(self) -> np.ndarray:
        return np.array([self._x1, self._y1],dtype=float)
    
    @property
    def end(self) -> np.ndarray:
        return np.array([self._x2, self._y2])
    
    def __str__(self) -> str:
        return f"L {self._x2} {self._y2}"
    
class ZSegment(LinearSegment):
    def __init__(self, x1: float, y1: float):
        self._x1 = x1
        self._y1 = y1
        self._x2 = 0
        self._y2 = 0

    def __str__(self) -> str:
        return f"Z"


class ArcSegment(Segment):
    def __init__(
            self, x1: float, y1: float, rx: float, ry: float, x_axis_rotation: float,
            large_arc_flag: bool, sweep_flag: bool, x2: float, y2: float):
        self._x1 = x1
        self._y1 = y1
        self._rx = rx
        self._ry = ry
        self._x_axis_rotation = x_axis_rotation
        self._large_arc_flag = 1 if large_arc_flag else 0
        self._sweep_flag = 1 if sweep_flag else 0
        self._x2 = x2
        self._y2 = y2

    def point(self, length: float) -> np.ndarray:
        assert 0 <= length and length <= self.arc_length
        raise NotImplementedError()


    @property
    def arc_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def end(self) -> np.ndarray:
        return np.array([self._x2, self._y2])
    
    def __str__(self) -> str:
        return f"A {self._rx} {self._ry} {self._x_axis_rotation} {self._large_arc_flag} {self._sweep_flag} {self._x2} {self._y2}"
    

# class CircularSegment(Segment):
#     def __init__(self, x1: float, y1: float, r: float, start_angle: float, end_angle: float):
#         self._x1 = x1
#         self._y1 = y1
#         self._r = r
#         self._start_angle = start_angle
#         self._end_angle = end_angle

#         assert abs(start_angle - end_angle) < 360

#     def point(self, length: float) -> np.ndarray:
#         assert 0 <= length and length <= self.arc_length

#         p = length / self.arc_length

#         delta = np.array([
#             self._r*np.cos(self._end_angle*np.pi/180 * p + self._start_angle*np.pi/180 * (1-p)),
#             self._r*np.sin(self._end_angle*np.pi/180 * p + self._start_angle*np.pi/180 * (1-p)),
#         ]) - np.array([
#             self._r*np.cos(self._start_angle*np.pi/180),
#             self._r*np.sin(self._start_angle*np.pi/180),         
#         ])
        
#         return np.array([self._x1, self._y1]) + delta

#     @property
#     def arc_length(self) -> float:
#         return 2*np.pi *self._r * abs(self._start_angle - self._end_angle)/360 
    
#     @property
#     def end(self) -> np.ndarray:
#         return self.point(self.arc_length)
    
#     def __str__(self) -> str:
#         x2, y2 = self.end
#         large_arc_flag = 1 if abs(self._start_angle - self._end_angle) > 180 else 0
#         sweep_flag = 1 if self._end_angle > self._start_angle else 0
#         return f"A {self._r} {self._r} {0} {large_arc_flag} {sweep_flag} {x2} {y2}"


class Path(Segment):    
    def __init__(self):
        self._segments: list[Segment] = []
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

        self._cursor = np.array([0.0,0.0], dtype=float)

    @property
    def top_left(self) -> np.ndarray:
        return np.array([self.min_x, self.min_y])

    def __str__(self) -> str:

        if len(self._segments) == 0 or str(self._segments[0])[0] != "M":
            string = "M 0 0"
        else:
            string = ""


        return string + " ".join(
            map(lambda x: str(x), self._segments)
            )
    
    def point(self, length: float) -> np.ndarray:
        assert length < self.arc_length

        traversed = 0.0
        i = 0
        while traversed + self._segments[i].arc_length < length:
            traversed += self._segments[i].arc_length
            i += 1

        return self._segments[i].point(length - traversed)

    
    @property
    def arc_length(self) -> float:
        return sum(map(lambda x: x.arc_length, self._segments))
    
    @property
    def start(self) -> np.ndarray:
        return np.array([0.0,0.0]) if len(self._segments) == 0 else self._segments[0].start()
    
    @property
    def end(self) -> np.ndarray:
        return np.array([0.0,0.0]) if len(self._segments) == 0 else self._segments[-1].end()
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x    

    @property
    def height(self) -> float:
        return self.max_y - self.min_y
    
    def M(self, x: float, y: float) -> Self:
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

        segment = MSegment(x, y)
        self._cursor = segment.end
        self._segments.append(segment)
        return self

    
    def L(self, x: float, y: float) -> Self:
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

        segment = LinearSegment(self._cursor[0],self._cursor[1], x, y)
        self._cursor = segment.end
        self._segments.append(segment)
        return self
    
    def Z(self):
        segment = ZSegment(self._cursor[0],self._cursor[1])
        self._cursor = segment.end
        self._segments.append(segment)
        return self
        