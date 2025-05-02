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

        self.transform: Transform = transform or Transform()
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
        elements = elements or []
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
    def width(self) -> int:
        return self._width
    @property
    def height(self) -> int:
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
    def __str__(self):
        raise NotImplementedError()
    
    @property
    def end(self) -> np.ndarray:
        raise NotImplementedError()
    

    
class LinearSegment(Segment):
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def end(self):
        return np.array([self._x, self._y])

class Path:
    UNRESTRICTED: int = 1
    NO_ELLIPSE: int = 2
    NO_SEGMENTS: int = 3

    @staticmethod
    def verify_call(foo):
        def verified_method(self: Self, *args, **kwargs):
            if self._state == Path.UNRESTRICTED:
                self._state = Path.NO_ELLIPSE
                return foo(self, *args, **kwargs)
            elif self._state == Path.NO_ELLIPSE:
                raise RuntimeError("Cannot add an elliptical loop unless it is the only segment")
            elif self._state == Path.NO_SEGMENTS:
                raise RuntimeError("Cannot add segments to a Path after adding an elliptical loop.")
            return foo(self, *args, **kwargs) # Let function handle check for whether an sllipse is called or not            
            
        return verified_method
    
    def __init__(self):
        self._state = Path.UNRESTRICTED
        self._segments: list[Segment] = []
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

    def __str__(self) -> str:
        return "M 0 0 " + " ".join(
            map(lambda x: str(x), self._segments)
            )
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x    

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    
    @verify_call
    def L(self, x: int, y: int) -> Self:
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

        self._segments.append(Segment(f"L {x} {y}"))
        return self
    
    @verify_call
    def Z(self):
        
        return self


class DrawingMetaclass(type):
    @staticmethod
    def globify(method):
        def globified_method(self: Element):
            transform = self.transform
            self.transform = self.global_transform
            r = method(self)
            self.transform = transform
            return r
        return globified_method
    
    @staticmethod
    def anchor(method):
        def anchored_method(self: Element):
            transform = self.transform
            self.transform = self.anchor_transform(self.transform)
            r = method(self)
            self.transform = transform
            return r
        return anchored_method


    def __new__(cls, name, bases, attrs):
        method_name_to_globify = "draw_self"
        if method_name_to_globify in attrs:
            attrs[method_name_to_globify] = DrawingMetaclass.anchor(DrawingMetaclass.globify(attrs[method_name_to_globify]))
        return super().__new__(cls, name, bases, attrs)


class Drawing(Element, metaclass=DrawingMetaclass):
    def __init__(self,
                 stroke: Color | None = None,
                 stroke_width: float = 1,
                 fill: Color | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        if fill is not None and stroke is None:
            self.stroke: Color = Color(fill)
        else:
            self.stroke: Color = Color(stroke) if stroke else Color()
            
        self.fill: Color = Color(fill) if fill else Color(opacity=0.0)

        self._shape: Path = self.get_shape()
        self.stroke_width: float = stroke_width

    @property
    def width(self):
        return self._shape.width
    @property
    def height(self):
        return self._shape.height

    def get_shape(self) -> Path:
        raise NotImplementedError()
    
    def draw_self(self):
        return svg.Path(
                d=str(self._shape),
                transform=str(self.transform),
                stroke=self.stroke.rgb,
                stroke_opacity=self.stroke.opacity,
                fill=self.fill.rgb,
                fill_opacity=self.fill.opacity,
                stroke_width=self.stroke_width).as_str()
    

class Rect(Drawing):
    def __init__(self, *, width, height, **kwargs):
        self._width = width
        self._height = height
        super().__init__(**kwargs)

    def get_shape(self) -> Path:
        return Path().L(self._width, 0).L(self._width, self._height).L(0, self._height).L(0,0)
    
class Circle(Drawing):
    def __init__(self, *, radius, **kwargs):
        self._radius = radius
        super().__init__(**kwargs)

    def get_shape(self) -> Path:
        return Path()
    


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

