from .utility import ellipse_arc_length
from .primatives import *
from PIL import ImageFont
from io import StringIO
from typing import Self, Generator
import numpy as np
import svg

class Drawable:

    TOP_LEFT: int = 1
    CENTER: int = 2

    def __init__(self, *, transform: Transform | None = None, anchor: int = CENTER):

        self.transform: Transform = Transform() if transform is None else transform
        self.anchor = anchor
    
    def set_transform(self, transform: Transform) -> Self:
        self.transform = transform
        return self

    def draw(self) -> str:
        raise NotImplementedError()
    
    @property
    def anchor_transform(self) -> Transform:
        if self.anchor == Drawable.TOP_LEFT:
            return Transform()
        if self.anchor == Drawable.CENTER:
            return Transform(translation=[-self.width/2, -self.height/2])
    @property
    def width(self) -> float:
        raise NotImplementedError()
    @property
    def height(self) -> float:
        raise NotImplementedError()


class Element(Drawable):

    @staticmethod
    def anchor(method):
        def anchored_method(self: Element, *args, **kwargs):
            transform = self.transform
            self.transform = self.anchor_transform(self.transform)
            r = method(self, *args, **kwargs)
            self.transform = transform
            return r
        return anchored_method
    
    @staticmethod
    def globify(method):
        def globified_method(self: Element, *args, **kwargs):
            transform = self.transform
            self.transform = self.global_transform
            r = method(self, *args, **kwargs)
            self.transform = transform
            return r
        return globified_method

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._children: list["Element"] = []
        self._parent: "Element" | None = None
    
    def set_global_transform(self, transform: Transform) -> Self:
        self.global_transform = transform
        return self

    def has_ancestor(self, other: "Element"):
        ancestor = self
        while (ancestor := self._parent) is not None:
            if ancestor == other:
                return True
        return False
    
    def set_parent(self, parent: "Element", preserve_global_transform: bool = True) -> Self:
        """        
        An Element is placed, scaled, and rotated relative to its parent.
        """
        if parent == None:
            self._parent = None
        else:

            if parent.has_ancestor(self):
                raise ValueError("Cannot set the parent to a descendant.")

            if preserve_global_transform:
                global_transform = self.global_transform

            parent._children.append(self)
            self._parent = parent

            if preserve_global_transform:
                self.global_transform = global_transform

        return self
        
    def add_child(self, child: "Element", preserve_global_transform: bool = True) -> Self:
        child.set_parent(self, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(self, children: list["Element"], preserve_global_transform: bool = True) -> Self:
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self
    
    def with_children(self, children: list["Element"]) -> Self:
        return self.add_children(children, preserve_global_transform=False)

    @property
    def global_transform(self) -> Transform:
        curr = self

        transform = self.transform

        while curr._parent is not None:
            transform = curr._parent.transform(transform)
            curr = curr._parent

        return transform
    
    @global_transform.setter
    def global_transform(self, value: Transform):
        if self._parent is None:
            self.transform = value
        else:
            self.transform = self._parent.global_transform.inv(value)

    
    def __str__(self) -> str:
        return self.draw_self()

    def __iter__(self) -> Generator["Element"]:
        """
        Iterate over self and children in ascending z order, secondarily self before children
        """
        elements = [self]
        for child in self._children:
            elements.extend(child.__iter__())

        yield from sorted(elements, key=lambda d: d.global_transform.z)

    def draw(self) -> str:
        string_builder = StringIO()
        for element in self:
            string_builder.write(element.draw_self())

        return string_builder.getvalue()
    
    def draw_self(self) -> str:
        raise NotImplementedError()
    

class Head(Element):
    # @property
    # def _parent(self):
    #     return self._parent
    # @_parent.setter
    # def _parent(self, value):
    #     if value is not None:
    #         raise ValueError("Cannot set Head's parent to anything but None.")
        
    def draw_self(self):
        return ""
    

class Canvas(Drawable):
    def __init__(self, *, elements: list[Element] | None = None, width=1920, height=1080, logical_width = 64, logical_height = 36, color = 'dark_slate', **kwargs):

        super().__init__(**kwargs)
        elements = [] if elements is None else elements
        self.anchor = Drawable.CENTER
        self.color: Color = Color(color)
        self._head = Head().with_children(elements)


        assert width/height == logical_width/logical_height and width/logical_width == height/logical_height

        self._width = width
        self._height = height
        self._logical_width = logical_height
        self._logical_height = logical_width
        self._logical_scaling = width/logical_width


        self._head.transform.scale = np.array([self._logical_scaling, self._logical_scaling, 1])

    
    @property
    def width(self) -> float:
        return self._width
    @property
    def height(self) -> float:
        return self._height
    
    def zoom(self, transform: Transform):
        self._head.transform.scale = transform.scale * self._logical_scaling
        self._head.transform.translation = [self.width/2, self.height/2, 0] + -transform.translation*transform.scale*self._logical_scaling
        return self

    def draw(self) -> str:
        background = Rect(width=self.width, height=self.height, fill = self.color, anchor=Drawable.TOP_LEFT)
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.width, self.height),
            elements= [background] + list(self._head)).as_str()


class Segment:

    def __init__(self):
        self._x1: float
        self._y1: float


    @property
    def start(self) -> np.ndarray:
        return np.array([self._x1, self._y1],dtype=float)
    
    def point_percentage(self, percentage: float):
        assert 0 <= percentage and percentage <= 1
        return self.point(percentage * self.arc_length)

    def point(self, length: float) -> np.ndarray:
        raise NotImplementedError()

    @property
    def arc_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def end(self) -> np.ndarray:
        raise NotImplementedError()
    
    def __str__(self) -> str:
        raise NotImplementedError()
    

    
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
        self._start = self._cursor.copy()

    def __str__(self) -> str:
        return "M 0 0 " + " ".join(
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
        return np.array([0.0,0.0]) if len(self._segments) == 0 else self._segments[0].end()
    
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

        self._cursor[:] = x, y
        self._start[:] = x, y

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


# class DrawingMetaclass(type):
#     @staticmethod
#     def globify(method):
#         def globified_method(self: Element):
#             transform = self.transform
#             self.transform = self.global_transform
#             r = method(self)
#             self.transform = transform
#             return r
#         return globified_method
    
#     @staticmethod
#     def anchor(method):
#         def anchored_method(self: Element):
#             transform = self.transform
#             self.transform = self.anchor_transform(self.transform)
#             r = method(self)
#             self.transform = transform
#             return r
#         return anchored_method


#     def __new__(cls, name, bases, attrs):
#         method_name_to_globify = "draw_self"
#         if method_name_to_globify in attrs:
#             attrs[method_name_to_globify] = DrawingMetaclass.anchor(DrawingMetaclass.globify(attrs[method_name_to_globify]))
#         return super().__new__(cls, name, bases, attrs)


class Drawing(Element):
    def __init__(self, *,
                 path: Path,
                 stroke: Color | None = None,
                 stroke_width: float = 1,
                 fill: Color | None = None,
                 **kwargs):
        
        super().__init__(**kwargs)


        if fill is not None and stroke is None:
            self.stroke: Color = Color(fill)
        else:
            self.stroke: Color = Color(stroke) if stroke is not None else Color()

        self.fill: Color = Color(fill) if fill is not None else Color(opacity=0.0)
        self.stroke_width: float = stroke_width

        self._path: Path = path
        
    @Element.anchor
    def point(self, length: float) -> np.ndarray:
        return self.transform(Transform(self._path.point(length))).translation
    
    @Element.anchor
    def global_point(self, length: float) -> np.ndarray:
        return self.global_transform(Transform(self._path.point(length))).translation


    @property
    def arc_length(self):
        return self._path.arc_length

    @property
    def width(self):
        return self._path.width
    @property
    def height(self):
        return self._path.height
    
    @Element.anchor
    @Element.globify
    def draw_self(self):
        return svg.Path(
                d=str(self._path),
                transform=str(self.transform),
                stroke=self.stroke.rgb,
                stroke_opacity=self.stroke.opacity,
                fill=self.fill.rgb,
                fill_opacity=self.fill.opacity,
                stroke_width=self.stroke_width).as_str()
    

class Circle(Drawing):

    def __init__(self, radius: float, **kwargs):
        path = Path().L(radius, 0).L(radius, radius).Z()
        super().__init__(path = path, **kwargs)

        self.radius = radius

    @property
    def width(self):
        return self.radius * 2
    @property
    def height(self):
        return self.radius * 2

    @Element.globify
    def draw_self(self):

        if self.anchor == Drawable.TOP_LEFT:
            anchor_align = Transform(translation=[-self.radius, -self.radius])
        elif self.anchor == Drawable.CENTER:
            anchor_align = Transform()

        return svg.Circle(
            r=self.radius,
            transform=str(anchor_align(self.transform)),
            stroke=self.stroke.rgb,
            stroke_opacity=self.stroke.opacity,
            fill=self.fill.rgb,
            fill_opacity=self.fill.opacity,
            stroke_width=self.stroke_width).as_str()


def Rect(width, height, **kwargs):

    path = Path().L(width, 0).L(width, height).L(0, height).Z()

    return Drawing(path=path, **kwargs)
    


class Text():
    def __init__(self, *, text: str, font_size: int = 32, font_family: str = 'arial', **kwargs):
            super().__init__(**kwargs)
            self.text: str = text
            self.font_size: int = font_size
            self.font_family: str = font_family

    # @property
    # def width(self) -> int:
    #     font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
    #     size = font.getsize(self.text)
    #     return size[0][0]
    
    # @property
    # def height(self) -> int:
    #     font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
    #     size = font.getsize(self.text)
    #     return size[0][1]
    
    def draw_self(self, tfm: Transform):

        font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size*tfm.scale_x).font
        size = font.getsize(self.text)

        width = size[0][0]
        height = size[0][1]


        if self.anchor == Element.CENTER:
            offset_x = -width/2
            offset_y = height/2
        elif self.anchor == Element.TOP_LEFT:
            offset_x = 0
            offset_y = height

        # print(self.font_size * tfm.scale_x)

        return svg.Text(
            text=self.text,
            x=tfm.x + offset_x,
            y=tfm.y + offset_y,
            font_size=self.font_size * tfm.scale_x,
            font_family=self.font_family,
            fill=self.color.rgb,
            ).as_str()

