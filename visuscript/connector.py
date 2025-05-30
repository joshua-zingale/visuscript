from visuscript.drawable import Drawable
from visuscript.element import Drawing, Path, Element
from visuscript.segment import Segment
from visuscript.primatives import Vec2
from visuscript.constants import LineTarget
from abc import ABC, abstractmethod
import numpy as np


class Connector(ABC, Drawable):
    """
    Visually connects one Element to another or one location to another.
    The source and destination of a Connector are automatically updated to match the Elements' positions whenever the Elements are transformed.
    """

    POSITIVE = 1
    NEGATIVE = -1

    def __init__(self, *, source: Vec2 | Element, destination: Vec2 | Element, source_target: LineTarget = LineTarget.RADIAL, destination_target: LineTarget = LineTarget.RADIAL):

        self._source = source
        self._destination = destination

        self._source_target = source_target
        self._destination_target = destination_target


    @property
    def _unit_between(self) -> Vec2:
        diff = self._destination.global_shape.center - self._source.global_shape.center
        return diff/np.linalg.norm(diff)


    def _get_vec2(self, vec2_or_element: Vec2 | Element, target: LineTarget, offset_sin: int):
        if isinstance(vec2_or_element, Element):
            if target == LineTarget.CENTER:
                return vec2_or_element.global_shape.center
            elif target == LineTarget.RADIAL:
                center = vec2_or_element.global_shape.center
                return center + offset_sin * vec2_or_element.global_shape.circumscribed_radius * self._unit_between
        else:
            return Vec2(*vec2_or_element)

    @property
    def source(self) -> Vec2:
        return self._get_vec2(self._source, self._source_target, Line.POSITIVE)
    
    @property
    def destination(self) -> Vec2:
        return self._get_vec2(self._destination, self._destination_target, Line.NEGATIVE)

    def draw(self):
        return self.get_connector(self.source, self.destination)
    
    @abstractmethod
    def get_connector(self, source: Vec2, destination: Vec2) -> Drawable:       
        """Returns a drawable line from source to destination""" 
        ...

class Line(Connector):
    def get_connector(self, source, destination) -> Drawable:
        return Drawing(path=Path().M(*source).L(*destination))



# def line_with_head(source: Vec2, destination: Vec2, stroke=None, stroke_width = 1, head_size = 2, fill=None):

#     distance = np.linalg.norm(destination - source)
#     direction = (destination - source) / distance
    
#     ortho = Vec2(-direction.y, direction.x)

#     line_end =source + direction*(distance-head_size)
#     return Drawing(
#         stroke=stroke,
#         stroke_width=stroke_width,
#         fill=fill,
#         path=(
#             Path()
#             .M(*source)
#             .L(*line_end)
#             .L(*(line_end + ortho*head_size/2))
#             .L(*(source + direction*distance))
#             .L(*(line_end - ortho*head_size/2))
#             .L(*line_end)
#         ))


# def arrow(source: Element, destination: Element, stroke=None, stroke_width = 1, head_size = 2, fill='off_white'):

#     s_xy = source.shape.center
#     d_xy = destination.shape.center

#     direction = (d_xy - s_xy) / np.linalg.norm(d_xy - s_xy)

#     start_xy = s_xy + direction * source.shape.circumscribed_radius
#     end_xy = d_xy - direction * destination.shape.circumscribed_radius

#     return line_with_head(start_xy, end_xy, stroke=stroke, stroke_width=stroke_width, head_size=head_size, fill=fill)
