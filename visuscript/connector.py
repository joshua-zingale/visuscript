from visuscript.drawable import Drawable
from visuscript.element import Drawing, Path, Element
from visuscript.segment import Segment
from visuscript.primatives import Vec2, Transform
from visuscript.constants import LineTarget
from visuscript.config import *
from abc import abstractmethod
import numpy as np


class Connector(Element):
    """A connector visually connects one Element to another or one location to another."""

    POSITIVE = 1
    NEGATIVE = -1


    def __init__(self, *, source: Vec2 | Element, destination: Vec2 | Element, source_target: LineTarget = LineTarget.RADIAL, destination_target: LineTarget = LineTarget.RADIAL, **kwargs):
        super().__init__(**kwargs)
        self._source = source
        self._destination = destination

        self._source_target = source_target
        self._destination_target = destination_target

    @property
    def height(self) -> float:
        return abs(self._destination.global_shape.center[1] - self._source.global_shape.center[1])
    @property
    def width(self) -> float:
        return abs(self._destination.global_shape.center[0] - self._source.global_shape.center[0])
    @property
    def top_left(self) -> float:
        return Vec2(min(self._destination.global_shape.center[0], self._source.global_shape.center[0]), min(self._destination.global_shape.center[1], self._source.global_shape.center[1]))

    @property
    def _unit_between(self) -> Vec2:
        diff = self._destination.global_shape.center - self._source.global_shape.center
        eps = 1e-16
        return diff/max(np.linalg.norm(diff), eps)


    def _get_vec2(self, vec2_or_element: Vec2 | Element, target: LineTarget, offset_sign: int):
        if isinstance(vec2_or_element, Element):
            if target == LineTarget.CENTER:
                return vec2_or_element.global_shape.center
            elif target == LineTarget.RADIAL:
                center = vec2_or_element.global_shape.center
                return center + offset_sign * vec2_or_element.global_shape.circumscribed_radius * self._unit_between
        else:
            return Vec2(*vec2_or_element)

    @property
    def source(self) -> Vec2:
        """The (x,y) source for this Connector, updated to the source's global Shape."""
        return self._get_vec2(self._source, self._source_target, Line.POSITIVE)
    
    @property
    def destination(self) -> Vec2:
        """The (x,y) destination for this Connector, updated to the destination's global Shape."""
        return self._get_vec2(self._destination, self._destination_target, Line.NEGATIVE)
    
    @property
    def overlapped(self) -> bool:
        """True if and only if the source and destination are overlapped."""
        distance = 0
        if self._source_target == LineTarget.RADIAL:
            distance += self._source.global_shape.circumscribed_radius
        if self._destination_target == LineTarget.RADIAL:
            distance += self._destination.global_shape.circumscribed_radius

        return np.linalg.norm(self._destination.global_shape.center - self._source.global_shape.center) < distance

    def draw_self(self, transform: Transform):
        return self.get_connector(
            source=self.source,
            destination=self.destination,
            stroke=self.stroke,
            stroke_width=self.stroke_width,
            fill=self.fill,
            opacity=self.global_opacity,
            overlapped=self.overlapped).draw()
    
    @abstractmethod
    def get_connector(self, source: Vec2, destination: Vec2, stroke: Color, stroke_width: float, fill: Color, opacity: float, overlapped: bool) -> Drawable:       
        """Returns a drawable connector from source to destination""" 
        ...

class Line(Connector):
    """A Line is a straight-line Connector."""
    def get_connector(self, source: Vec2, destination: Vec2, stroke: Color, stroke_width: float, fill: Color, opacity: float, overlapped: bool) -> Drawing:
        return Drawing(
            path=Path().M(*source).L(*destination),
            stroke=stroke,
            stroke_width=stroke_width,
            fill=fill,
            opacity=0.0 if overlapped else opacity
            )
    
class Arrow(Connector):
    """An Arrow is a straight-line Connector with an optional arrowhead on either side."""

    def __init__(self, *, start_size: float | ConfigurationDeference = DEFER_TO_CONFIG, end_size: float | ConfigurationDeference = DEFER_TO_CONFIG, source: Vec2 | Element, destination: Vec2 | Element, source_target: LineTarget = LineTarget.RADIAL, destination_target: LineTarget = LineTarget.RADIAL, **kwargs):
        super().__init__(source=source, destination=destination, source_target=source_target, destination_target=destination_target, **kwargs)
        self._start_size = 0.0 if start_size is DEFER_TO_CONFIG else start_size
        self._end_size = config.element_stroke_width*5 if end_size is DEFER_TO_CONFIG else end_size

    def get_connector(self, source: Vec2, destination: Vec2, stroke: Color, stroke_width: float, fill: Color, opacity: float, overlapped: bool) -> Drawing:
        unit = self._unit_between
        diff = destination - source
        dist = max(np.linalg.norm(diff), 1e-16)
        unit = diff/dist
        ortho = Vec2(-unit.y, unit.x)


        line_start = source + unit*self._start_size
        line_end =source + unit*(dist-self._end_size)

        return Drawing(
            stroke=stroke,
            stroke_width=stroke_width,
            fill=fill,
            opacity=0.0 if overlapped else opacity,
            path=(
                Path()
                .M(*source)
                .L(*(line_start - ortho*self._start_size/2))
                .M(*source)
                .L(*(line_start + ortho*self._start_size/2))
                .L(*line_start)
                .L(*line_start)
                .L(*line_end)
                .L(*(line_end + ortho*self._end_size/2))
                .L(*(source + unit*dist))
                .L(*(line_end - ortho*self._end_size/2))
                .L(*line_end)
            ))