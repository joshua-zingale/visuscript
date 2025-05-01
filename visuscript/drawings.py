from .primatives import *
from PIL import ImageFont
from io import StringIO
from typing import Self
import numpy as np
import svg

class DrawingMetaclass(type):
    @classmethod
    def globify(cls, method):
        def globified_method(self: Self):
            return method(self, self.global_transform)
        return globified_method

    def __new__(cls, name, bases, attrs):
        method_name_to_globify = "draw_self"
        if method_name_to_globify in attrs:
            attrs[method_name_to_globify] = DrawingMetaclass.globify(attrs[method_name_to_globify])
        return super().__new__(cls, name, bases, attrs)


class Drawing(metaclass=DrawingMetaclass):

    CENTER = 1
    TOP_LEFT = 2

    def __init__(self, *, transform = Transform(), anchor: int = CENTER):

        self.transform: Transform = transform
        self._children: list["Drawing"] = []
        self._parent: "Drawing" | None = None
        self.anchor = anchor
    
    def set_transform(self, transform: Transform) -> Self:
        self.transform = transform
        return self
    
    def set_global_transform(self, transform: Transform) -> Self:
        self.global_transform = transform
        return self

    def has_ancestor(self, other: "Drawing"):
        ancestor = self
        while (ancestor := self._parent) is not None:
            if ancestor == other:
                return True
        return False
    
    def set_parent(self, parent: "Drawing", preserve_global_transform: bool = True) -> Self:
        """        
        A drawing are placed, scaled, and rotated relative to its parent.
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
        
    def add_child(self, child: "Drawing", preserve_global_transform: bool = True) -> Self:
        child.set_parent(self, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(self, children: list["Drawing"], preserve_global_transform: bool = True) -> Self:
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self
    
    def with_children(self, children: list["Drawing"]) -> Self:
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

    def __iter__(self):
        """
        Iterate over self and children in ascending z order, secondarily self before children
        """
        drawings = [self]
        for child in self._children:
            drawings.extend(child)

        yield from sorted(drawings, key=lambda d: d.global_transform.z)


    def draw_self(self, global_transform: Transform) -> str:
        return ""

    def draw(self) -> str:
        string_builder = StringIO()
        for drawing in self:
            string_builder.write(drawing.draw_self())
        return string_builder.getvalue()

class ColorableDrawing(Drawing):
    def __init__(self, *, color: str | Color = Color(), **kwargs):
        super().__init__(**kwargs)
        self._color = Color(color)


    def set_color(self, color: str | Color) -> Self:
        self._color = Color(color)
        return self

    

    @property
    def color(self) -> Color:
        return self._color
    
    @color.setter
    def color(self, value: str | np.ndarray | Color):
        self._color = Color(value)

class OutlineableDrawing(ColorableDrawing):
    def __init__(self, *, outline: str | np.ndarray | Color = Color(opacity=0.0), outline_thickness: int = 1,  **kwargs):
        super().__init__(**kwargs)
        self._outline: Color = Color(outline)
        self.outline_thickness: int = outline_thickness

    def set_outline(self, color: str | Color) -> Self:
        self._color = Color(color)
        return self
    


    @property
    def outline(self) -> Color:
        return self._outline
    
    
    @outline.setter
    def outline(self, value: str | np.ndarray | Color | None):
        self._outline = Color(self.outline.rgb, opacity=0.0) if value is None else Color(value)


class Canvas(ColorableDrawing):
    def __init__(self, *, width=1920, height=1080, anchor: int = Drawing.TOP_LEFT, **kwargs):
        super().__init__(anchor = anchor, **kwargs)
        self.width=width
        self.height=height


    def draw_self(self, tfm: Transform) -> str:


        width = self.width * tfm.scale_x
        height = self.height * tfm.scale_y

        if self.anchor == Drawing.CENTER:
            offset_x = -width/2
            offset_y = -height/2
        elif self.anchor == Drawing.TOP_LEFT:
            offset_x = 0
            offset_y = 0

        background = Rect(width=width, height=height, color = self.color, anchor=Drawing.TOP_LEFT)

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(-(tfm.x + offset_x), -(tfm.y + offset_y), width, height),
            elements= [background] + list(self.iter_components())).as_str()
    
    def iter_components(self):
        yield from filter(lambda x: x is not self, super().__iter__())

    def __iter__(self):
        yield self


class Circle(OutlineableDrawing):

    def __init__(self, *, radius, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def draw_self(self, tfm: Transform) -> str:
        if self.anchor == Drawing.CENTER:
            offset_x = 0
            offset_y = 0
        elif self.anchor == Drawing.TOP_LEFT:
            offset_x = -self.radius
            offset_y = -self.radius 
        return svg.Circle(
            cx=tfm.x + offset_x,
            cy=tfm.y + offset_y,
            r=self.radius,
            fill=self.color.rgb,
            stroke=self.outline.rgb,
            fill_opacity=self.color.opacity,
            stroke_opacity=self.outline.opacity).as_str()



class Rect(OutlineableDrawing):
    def __init__(self, *, width, height, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def draw_self(self, tfm: Transform) -> str:

        if self.anchor == Drawing.CENTER:
            offset_x = -width/2
            offset_y = -height/2
        elif self.anchor == Drawing.TOP_LEFT:
            offset_x = 0
            offset_y = 0

        width = self.width*tfm.scale[0]
        height = self.height*tfm.scale[1]
        return svg.Rect(
            x=tfm.x + offset_x,
            y=tfm.y + offset_y,
            width=width, height=height,
            fill=self.color.rgb,
            stroke=self.outline.rgb,
            fill_opacity=self.color.opacity,
            stroke_opacity=self.outline.opacity
            ).as_str()
    

class Text(ColorableDrawing):
    def __init__(self, *, text: str, font_size: int = 32, font_family: str = 'arial', **kwargs):
            super().__init__(**kwargs)
            self.text: str = text
            self.font_size: int = font_size
            self.font_family: str = font_family

    @property
    def width(self) -> int:
        font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
        size = font.getsize(self.text)
        return size[0][0]
    
    @property
    def height(self) -> int:
        font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
        size = font.getsize(self.text)
        return size[0][1]
    
    def draw_self(self, tfm: Transform):

        width = self.width*tfm.scale_x
        height = self.height*tfm.scale_y


        if self.anchor == Drawing.CENTER:
            offset_x = -width/2
            offset_y = height/2
        elif self.anchor == Drawing.TOP_LEFT:
            offset_x = 0
            offset_y = height

        return svg.Text(
            text=self.text,
            x=tfm.x + offset_x,
            y=tfm.y + offset_y,
            font_size=self.font_size,
            font_family=self.font_family,
            fill= self.color.rgb,
            ).as_str()

