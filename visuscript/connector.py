from visuscript.drawable import Drawable
from visuscript.element import Drawing, Path, Element
from visuscript.primatives import Vec2, Transform
from visuscript.constants import LineTarget
from visuscript.config import *
from visuscript.math_utility import magnitude
from visuscript.animation import fade_in, fade_out, AnimationSequence, RunFunction
from abc import abstractmethod
from typing import Tuple, Generator

class Connector(Element):
    """A connector visually connects one Element to another or one location to another."""

    POSITIVE = 1
    NEGATIVE = -1


    def __init__(self, *, source: Vec2 | Element, destination: Vec2 | Element, source_target: LineTarget = LineTarget.RADIAL, destination_target: LineTarget = LineTarget.RADIAL, **kwargs):
        super().__init__(anchor=Anchor.DEFAULT, **kwargs)
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
        return diff/max(magnitude(diff), eps)


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

        return magnitude(self._destination.global_shape.center - self._source.global_shape.center) < distance

    def draw_self(self):
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
        dist = max(magnitude(diff), 1e-16)
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
    

class Edges(Drawable):
    def __init__(self):
        super().__init__()
        self._edges: dict[Tuple[Element, Element], Line] = dict()
        self._fading_away: set[Line] = set()

    @property
    def top_left(self):
        return Vec2(0,0)
    @property
    def width(self):
        return 0.0
    @property
    def height(self):
        return 0.0

    def get_edge(self, element1: Element, element2: Element):
        assert self.connected(element1, element2)
        return self._edges.get((element1, element2)) or self._edges[(element2, element1)]
    
    def connected(self, element1: Element, element2: Element):
        return (element1, element2) in self._edges or (element2, element1) in self._edges
    
    def connect(self, element1: Element, element2: Element):
        assert not self.connected(element1, element2)
        assert element1 is not element2

        edge = Line(source=element1, destination=element2).set_opacity(0.0)
        self._edges[(element1, element2)] = edge

        return fade_in(edge, duration=0.5)

    def disconnect(self, element1: Element, element2: Element):
        assert self.connected(element1, element2)
        if (element1, element2) in self._edges:
            edge = self._edges.pop((element1, element2))
        else:
            edge = self._edges.pop((element2, element1))
        
        self._fading_away.add(edge)

        return AnimationSequence(
            fade_out(edge),
            RunFunction(lambda:self._fading_away.remove(edge))
        )

    def draw(self):
        drawing = ""
        for edge in self._edges.values():
            drawing += edge.draw()
        for edge in self._fading_away:
            drawing += edge.draw()
        return drawing
    
    def lines_iter(self) -> Generator[Tuple[Vec2, Vec2]]:
        yield from map(lambda x: (x.source, x.destination),self._edges.values())