import numpy as np
from typing import Self
from abc import ABC, abstractmethod
from visuscript.primatives import Vec2
from visuscript.math_utility import magnitude

class Segment(ABC):

    @abstractmethod
    def point_percentage(self, percentage: float) -> Vec2:
        """
        The (x,y) point that is `percentage` along this segment, where `percentage` is between 0 and 1.
        """
        ...

    def point(self, length: float) -> Vec2:
        """
        The (x,y) point along this segment at `length` from the start.
        """
        assert 0 <= length and length <= self.arc_length + 1e-8, f"length={length}; arc_length={self.arc_length}"
        if length > self.arc_length and length - self.arc_length <= 1e-8:
            length = self.arc_length
        if self.arc_length == 0:
            return self.start
        return self.point_percentage(length/self.arc_length)

    @property
    @abstractmethod
    def arc_length(self) -> float:
        """
        The length in pixels of this segment.
        """
        ...
    @property
    @abstractmethod
    def start(self) -> Vec2:
        """
        The first (x,y) point in this segment.
        """
        ...    

    @property
    @abstractmethod
    def end(self) -> Vec2:
        """
        The last (x,y) point in this segment.
        """
        ...

    @abstractmethod
    def set_offset(self, x_offset: float, y_offset: float) -> Self:
        """
        Offsets the x and y coordinates of all points along this segment.

        The offset is always relative to the original segment without any offset applied.
        Thus, `segment.set_offset(0,0)` will always reset the segment to its initial state.
        """
        ...
    
    @property
    @abstractmethod
    def path_str(self) -> str:
        """
        The SVG encoding for this segment. This is what goes in the "d" property in a <path> element.
        """
        ...


class MSegment(Segment):
    def __init__(self, x1: float, y1: float):
        self._x1 = x1
        self._y1 = y1
        self._x1_og = x1
        self._y1_og = y1

    def set_offset(self, x_offset: float, y_offset: float) -> Self:
        self._x1 = self._x1_og + x_offset
        self._y1 = self._y1_og + y_offset
        return self
        
    @property
    def start(self):
        return Vec2(self._x1, self._y1)

    def point_percentage(self, p: float):
        return Vec2(self._x1, self._y1)

    @property
    def arc_length(self) -> float:
        return 0.0
    
    @property
    def end(self) -> Vec2:
        return Vec2(self._x1, self._y1)
    
    @property
    def path_str(self) -> str:
        return f"M {self._x1} {self._y1}"


class LSegment(Segment):
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

        self._x1_og = x1
        self._y1_og = y1
        self._x2_og = x2
        self._y2_og = y2


    def set_offset(self, x_offset: float, y_offset: float) -> Self:
        self._x1 = self._x1_og + x_offset
        self._y1 = self._y1_og + y_offset
        self._x2 = self._x2_og + x_offset
        self._y2 = self._y2_og + y_offset
        return self

    def point_percentage(self, p: float):
        if self._x1 == self._x2 and self._y1 == self._y2:
            return self.start
        # assert 0 <= p and p <= 1, f"Got {p}"
        return Vec2(
            self._x2 * p + self._x1 * (1 - p),
            self._y2 * p + self._y1 * (1 - p)
        )

    @property
    def arc_length(self) -> float:
        return ((self._x2 - self._x1)**2 + (self._y2 - self._y1)**2)**0.5
    
    @property
    def start(self):
        return Vec2(self._x1, self._y1)
    
    @property
    def end(self):
        return Vec2(self._x2, self._y2)
    
    @property
    def path_str(self) -> str:
        return f"L {self._x2} {self._y2}"
    
class ZSegment(LSegment):
    @property
    def path_str(self) -> str:
        return f"Z"
    

class QSegment(Segment):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        self._p1 = Vec2(x1, y1)
        self._p2 = Vec2(x2, y2)
        self._p3 = Vec2(x3, y3)
        self._p1_og = Vec2(x1, y1)
        self._p2_og = Vec2(x2, y2)
        self._p3_og = Vec2(x3, y3)

        self._arc_length = self._get_arc_length()


    def set_offset(self, x_offset: float, y_offset: float) -> Self:
        offset = Vec2(x_offset, y_offset)
        self._p1 = self._p1_og + offset
        self._p2 = self._p2_og + offset
        self._p3 = self._p3_og + offset
        return self


    def derivative(self, t: float):
        """Calculates the derivative of the Bezier curve at parameter t."""
        return 2 * (1 - t) * (self._p2 - self._p1) + 2 * t * (self._p3 - self._p2)

    def point_percentage(self, p: float) -> Vec2:
        assert 0 <= p and p <= 1

        l1 = self._p2 * p + self._p1 * (1 - p)
        l2 = self._p3 * p + self._p2 * (1 - p)

        return l2 * p + l1 * (1 - p)

    @property
    def arc_length(self) -> float:
        return self._arc_length

    def _get_arc_length(self) -> float:
        num_segments = 1000
        total_length = 0.0
        dt = 1.0 / num_segments

        for i in range(num_segments):
            t1 = i * dt
            t2 = (i + 1) * dt

            # Approximate the length of the small segment using the magnitude of the derivative
            derivative1 = self.derivative(t1)
            derivative2 = self.derivative(t2)

            segment_length = (magnitude(derivative1) + magnitude(derivative2)) / 2 * dt
            total_length += segment_length

        return float(total_length)
    
    @property
    def start(self) -> Vec2:
        return Vec2(*self._p1)
    
    @property
    def end(self) -> Vec2:
        return Vec2(*self._p3)
    
    @property
    def path_str(self) -> str:
        return f"Q {self._p2[0]} {self._p2[1]} {self._p3[0]} {self._p3[1]}"


# class ArcSegment(Segment):
#     def __init__(
#             self, x1: float, y1: float, rx: float, ry: float, x_axis_rotation: float,
#             large_arc_flag: bool, sweep_flag: bool, x2: float, y2: float):
#         self._x1 = x1
#         self._y1 = y1
#         self._rx = rx
#         self._ry = ry
#         self._x_axis_rotation = x_axis_rotation
#         self._large_arc_flag = 1 if large_arc_flag else 0
#         self._sweep_flag = 1 if sweep_flag else 0
#         self._x2 = x2
#         self._y2 = y2

#     def point(self, length: float) -> np.ndarray:
#         assert 0 <= length and length <= self.arc_length
#         raise NotImplementedError()


#     @property
#     def arc_length(self) -> float:
#         raise NotImplementedError()
    
#     @property
#     def end(self) -> np.ndarray:
#         return np.array([self._x2, self._y2])
    
#     @property
#     def path_str(self) -> str:
#         return f"A {self._rx} {self._ry} {self._x_axis_rotation} {self._large_arc_flag} {self._sweep_flag} {self._x2} {self._y2}"

# TODO Figure out a way to make Paths lazily constructible for use in PathAnimation.
class Path(Segment):    
    def __init__(self):
        self._segments: list[Segment] = []
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

        self._cursor = Vec2(0,0)

        self._x_offset = 0
        self._y_offset = 0

    def set_offset(self, x_offset: float, y_offset: float) -> Self:
        self._x_offset, self._y_offset = x_offset, y_offset

        for segment in self._segments:
            segment.set_offset(x_offset, y_offset)

        return self

    @property
    def top_left(self):
        return Vec2(self.min_x, self.min_y)

    @property
    def path_str(self) -> str:

        if len(self._segments) == 0 or str(self._segments[0])[0] != "M":
            string = f"M {self._x_offset} {self._y_offset}"
        else:
            string = ""


        return string + " ".join(
            map(lambda x: x.path_str, self._segments)
            )
    
    def point_percentage(self, percentage):
        return self.point(percentage * self.arc_length)
    
    def point(self, length: float):
        assert length <= self.arc_length

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
    def start(self) -> Vec2:
        return Vec2(0.0,0.0) if len(self._segments) == 0 else self._segments[0].start
    
    @property
    def end(self) -> Vec2:
        return Vec2(0.0,0.0) if len(self._segments) == 0 else self._segments[-1].end
    
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
    
    def m(self, dx: float, dy: float) -> Self:
        x,y = [dx,dy] + self._cursor
        return self.M(x, y)

    
    def L(self, x: float, y: float) -> Self:
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

        segment = LSegment(self._cursor[0],self._cursor[1], x, y)
        self._cursor = segment.end
        self._segments.append(segment)
        return self
    

    def l(self, dx: float, dy: float) -> Self:
        x,y = [dx,dy] + self._cursor
        return self.L(x, y)
    
    def Z(self):

        x2, y2 = 0, 0
        for segment in reversed(self._segments):
            if isinstance(segment, MSegment):
                x2, y2 = segment.start
                break

        segment = ZSegment(self._cursor[0],self._cursor[1], x2, y2)
        self._cursor = segment.end
        self._segments.append(segment)
        return self
    
    z = Z

    def Q(self, x1: float, y1: float, x: float, y: float) -> Self:

        segment = QSegment(self._cursor[0],self._cursor[1], x1, y1, x, y)

        for xi, yi in [segment.point_percentage(alpha) for alpha in np.linspace(0,1,25)]:
            self.min_x = min(self.min_x, xi)
            self.max_x = max(self.max_x, xi)
            self.min_y = min(self.min_y, yi)
            self.max_y = max(self.max_y, yi)

       
        self._cursor = segment.end
        self._segments.append(segment)
        return self
    
    def q(self, dx1: float, dy1: float, dx: float, dy: float) -> Self:
        x1,y1 = [dx1,dy1] + self._cursor
        x,y = [dx,dy] + self._cursor
        return self.Q(x1, y1, x, y)
        