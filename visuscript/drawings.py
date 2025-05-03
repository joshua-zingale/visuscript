from .primatives import *
from .segments import Path, Segment
from io import StringIO
from typing import Self, Generator
import numpy as np
import svg

class Drawable:

    TOP_LEFT: int = 1
    CENTER: int = 2
    BEGINNING: int = 3


    def __init__(self, *, transform: Transform | None = None, anchor: int = CENTER):

        self.transform: Transform = Transform() if transform is None else Transform(transform)
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
    
    @property
    def svg_transform(self) -> str:
        return f"translate({" ".join(self.transform.translation[:2].astype(str))}) scale({" ".join(self.transform.scale[:2].astype(str))}) rotate({self.transform.rotation} {" ".join(self.transform.translation[:2].astype(str))})"



class Element(Drawable):

    @staticmethod
    def lock_svg_pivot(method):
        def locked_svg_pivot_method(self: Element, *args, **kwargs):
            self._svg_pivot = " ".join((-self.anchor_transform.translation[:2]).astype(str))
            r = method(self, *args, **kwargs)
            self._svg_pivot = None
            return r
        return locked_svg_pivot_method
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
        self._svg_pivot = None

    @property
    def svg_transform(self) -> str:
        if self._svg_pivot:
            return f"translate({" ".join(self.transform.translation[:2].astype(str))}) scale({" ".join(self.transform.scale[:2].astype(str))}) rotate({self.transform.rotation} {self._svg_pivot})"
        else:
            return super().svg_transform
    
    def set_global_transform(self, transform: Transform) -> Self:
        self.global_transform = transform
        return self

    def has_ancestor(self, other: "Element"):
        ancestor = self
        while (ancestor := self._parent) is not None:
            if ancestor == other:
                return True
        return False
    

    def set_parent(self, parent: "Element", preserve_global_transform: bool = False) -> Self:
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
        
    def add_child(self, child: "Element", preserve_global_transform: bool = False) -> Self:
        child.set_parent(self, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(self, children: list["Element"], preserve_global_transform: bool = False) -> Self:
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self
    
    def with_child(self, child: "Element"):
        return self.add_child(child)
    
    def with_children(self, children: list["Element"], preserve_global_transform: bool = False) -> Self:
        return self.add_children(children, preserve_global_transform=preserve_global_transform)

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

    
    # @property
    # def global_width(self) -> float:
    #     return self.width * self.global_transform.scale_x
    # @property
    # def global_height(self) -> float:
    #     return self.height * self.global_transform.scale_y

    
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


class Drawing(Element, Segment):

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
        return self.transform(Transform(self._path.point(length))).translation[:2]
    
    @Element.anchor
    @Element.globify
    def global_point(self, length: float) -> np.ndarray:
        return self.transform(Transform(self._path.point(length))).translation[:2]

    @property
    def start(self):
        return self._path.start
    @property
    def end(self):
        return self._path.end
    @property
    def arc_length(self):
        return self._path.arc_length
    @property
    def width(self):
        return self._path.width
    @property
    def height(self):
        return self._path.height
    
    @Element.lock_svg_pivot
    @Element.anchor
    @Element.globify
    def draw_self(self):
        return svg.Path(
                d=str(self._path),
                transform=self.svg_transform,
                stroke=self.stroke.rgb,
                stroke_opacity=self.stroke.opacity,
                fill=self.fill.rgb,
                fill_opacity=self.fill.opacity,
                stroke_width=self.stroke_width).as_str()
    

class Circle(Drawing):

    @property
    def anchor_transform(self) -> Transform:
        if self.anchor == Drawable.TOP_LEFT:
            Transform(translation=[-self.width/2, -self.height/2])
        elif self.anchor == Drawable.CENTER:
            return Transform()

    def __init__(self, radius: float, **kwargs):
        # TODO replace path with circle approximate
        path = Path().L(radius, 0).L(radius, radius).Z()
        super().__init__(path = path, **kwargs)

        self.radius = radius

    @property
    def width(self):
        return self.radius * 2
    @property
    def height(self):
        return self.radius * 2

    @Element.lock_svg_pivot
    @Element.anchor
    @Element.globify
    def draw_self(self):

        return svg.Circle(
            r=self.radius,
            transform=self.svg_transform,
            stroke=self.stroke.rgb,
            stroke_opacity=self.stroke.opacity,
            fill=self.fill.rgb,
            fill_opacity=self.fill.opacity,
            stroke_width=self.stroke_width).as_str()


def Rect(width, height, **kwargs):

    path = Path().L(width, 0).L(width, height).L(0, height).Z()

    return Drawing(path=path, **kwargs)