from .primatives import *
from .segments import Path, Segment
from io import StringIO
from typing import Self, Generator, Tuple
import numpy as np
import svg
from abc import ABC, abstractmethod
import sys


class Drawable(ABC):

    DEFAULT: int = 0
    TOP_LEFT: int = 1
    LEFT: int = 8
    CENTER: int = 9
    BEGINNING: int = 10

    def __init__(self, *, transform: Transform | None = None, anchor: int = CENTER):

        self.transform: Transform = Transform() if transform is None else Transform(transform)
        self.anchor = anchor
    
    def set_transform(self, transform: Transform) -> Self:
        self.transform = Transform(transform)
        return self
    
    def set_anchor(self, anchor: int):
        self.anchor = anchor
        return self
    
    @property
    def anchor_offset(self) -> np.ndarray[float]:
        """
        The (x,y) offset of this drawable for it to be anchored properly.
        """
        if self.anchor == Drawable.DEFAULT:
            return np.array([0.0,0.0], dtype=float)
        if self.anchor == Drawable.LEFT:
            return -(self.top_left + [0, self.height/2])
        if self.anchor == Drawable.TOP_LEFT:
            return -self.top_left
        if self.anchor == Drawable.CENTER:
            return -(self.top_left + [self.width/2, self.height/2])    

    @abstractmethod
    def draw(self) -> str:
        """
        Returns the SVG representation of this drawable.
        """
        ...
    
    @property
    @abstractmethod
    def top_left(self) -> np.ndarray:
        """
        The top left coordinate for this drawable.
        """
        ...
            
    @property
    @abstractmethod
    def width(self) -> np.ndarray:
        """
        The width of this drawable.
        """
        ...
    @property
    @abstractmethod
    def height(self) -> float:
        """
        The height of this drawable.
        """
        ...


class Element(Drawable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._children: list["Element"] = []
        self._parent: "Element" | None = None
        self._svg_pivot = None
        self._deleted = False
    
    def set_global_transform(self, transform: Transform) -> Self:
        """
        The global transform on this Element.
        
        Returns the composition of all transforms, including that on this Element, up this Element's hierarchy.
        """
        self.global_transform = transform
        return self

    def has_ancestor(self, element: "Element") -> bool:
        """
        Returns True if `element` is an ancestor of this Element.
        """
        ancestor = self
        while (ancestor := ancestor._parent) is not None:            
            if ancestor == element:
                return True
        return False
    
    def set_parent(self, parent: "Element", preserve_global_transform: bool = False) -> Self:
        """        
        Sets this Element's parent, replacing any that may have already existed.
        
        Also adds this Element as a child of the new parent and removes it as a child of any previous parent.
        """
        if parent is None:
            self._parent._children.remove(self)
            self._parent = None
        else:

            if parent.has_ancestor(self):
                raise ValueError("Cannot set an Element's descendant as its parent")
            
            if parent is self:
                raise ValueError("Cannot set an Element to be its own parent.")

            if preserve_global_transform:
                global_transform = self.global_transform

            parent._children.append(self)
            self._parent = parent

            if preserve_global_transform:
                self.global_transform = global_transform

        return self
        
    def add_child(self, child: "Element", preserve_global_transform: bool = False) -> Self:
        """
        Adds `child` as a child to this Element. If `preserve_global_transform` is True, then the
        transform on `child` is set such that its global transform not change.
        """
        child.set_parent(self, preserve_global_transform=preserve_global_transform)
        return self
    
    def remove_child(self, child: "Element", preserve_global_transform: bool = True) -> Self:
        """
        Removes `child` as a child to this Element. If `preserve_global_transform` is True, then the
        transform on `child` is set such that its global transform not change.
        """
        if child not in self._children:
            raise ValueError("Attempted to remove a child from an Element that is not a child of the Element.")
        child.set_parent(None, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(self, children: Tuple["Element", ...], preserve_global_transform: bool = False) -> Self:
        """
        Adds each input child as a child of this Element. If `preserve_global_transform` is True, then the
        transform on each child is set such that its global transform not change.
        """
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self
    
    # def with_child(self, child: "Element"):
    #     return self.add_child(child)
    
    # def with_children(self, children: list["Element"], preserve_global_transform: bool = False) -> Self:
    #     return self.add_children(children, preserve_global_transform=preserve_global_transform)

    @property
    def global_transform(self) -> Transform:
        """
        The global transform of this Element.
        
        Returns the composition of all ancestor transforms and this Element's transform.
        """
        curr = self

        transform = self.transform

        while curr._parent is not None:
            transform = curr._parent.transform(transform)
            curr = curr._parent

        return transform
    
    @global_transform.setter
    def global_transform(self, value: Transform):
        """
        Sets the global transform of this Element.
        """
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

    def __iter__(self) -> Generator["Element"]:
        """
        Iterate over this Element and its children in ascending z order, secondarily ordering parents before children.
        """
        elements = [self]
        for child in self._children:
            elements.extend(child.__iter__())

        yield from sorted(elements, key=lambda d: d.global_transform.z)

    def draw(self) -> str:
        string_builder = StringIO()
        for element in self:
            assert element.deleted == False
            string_builder.write(element.draw_self())
        return string_builder.getvalue()
    
    @abstractmethod
    def draw_self(self) -> str:
        """
        Returns the SVG representation for this Element but not for its children.
        """
        ...

    @property
    def deleted(self) -> bool:
        return self._deleted
    
    def delete(self):
        for element in self:
            element._deleted = True
            element.set_parent(None)



class Pivot(Element):
    @property
    def top_left(self) -> np.ndarray:
        return np.array([0,0], dtype=float)
    @property
    def width(self) -> float:
        return 0.0
    @property
    def height(self) -> float:
        return 0.0
    def draw_self(self):
        return ""

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


    def set_fill(self, color: Color) -> Self:
        self.fill = Color(color)
        return self
    
    def set_stroke(self, color: Color) -> Self:
        self.stroke = Color(color)
        return self
        
    def point(self, length: float) -> np.ndarray:
        return self.transform(Transform(self._path.set_offset(*self.anchor_offset).point(length))).xy
    
    def point_percentage(self, p: float) -> np.ndarray:
        return self.transform(Transform(self._path.set_offset(*self.anchor_offset).point_percentage(p))).xy
    
    def global_point(self, length: float) -> np.ndarray:

        return self.global_transform(Transform(self._path.set_offset(*self.anchor_offset).point(length))).xy

    @property
    def top_left(self) -> np.ndarray:
        return self._path.top_left

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
    def path_str(self):
        return self._path.path_str
    @property
    def set_offset(self, x_offset, y_offset):
        return self._path.set_offset(x_offset, y_offset)
    
    @property
    def width(self):
        return self._path.width
    @property
    def height(self):
        return self._path.height
    
    def draw_self(self):
        self._path.set_offset(*self.anchor_offset)
        return svg.Path(
                d=self._path.path_str,
                transform=self.global_transform.svg_transform,
                stroke=self.stroke.rgb,
                stroke_opacity=self.stroke.opacity,
                fill=self.fill.rgb,
                fill_opacity=self.fill.opacity,
                stroke_width=self.stroke_width).as_str()
    

class Circle(Drawing):

    def __init__(self, radius: float, **kwargs):
        # TODO replace path with circle approximate
        path = Path().L(radius, 0).L(radius, radius).Z()
        super().__init__(path = path, **kwargs)

        self.radius = radius

    @property
    def top_left(self) -> np.ndarray:
        return np.array([-self.radius, -self.radius], dtype=float)

    @property
    def width(self):
        return self.radius * 2
    @property
    def height(self):
        return self.radius * 2

    def draw_self(self):
        x, y = self.anchor_offset
        return svg.Circle(
            cx = x,
            cy = y,
            r=self.radius,
            transform=self.global_transform.svg_transform,
            stroke=self.stroke.rgb,
            stroke_opacity=self.stroke.opacity,
            fill=self.fill.rgb,
            fill_opacity=self.fill.opacity,
            stroke_width=self.stroke_width).as_str()


def Rect(width, height, anchor: int = Drawable.CENTER, **kwargs):

    path = Path().l(width, 0).l(0, height).l(-width, 0).Z()

    return Drawing(path=path, anchor=anchor, **kwargs)


# TODO Finish this
class Box(Drawing):

    def __init__(self, element: Element):
        super().__init__(path=None)

        self._element = element

    @property
    def _path(self) -> Path:
        return Path().l(self._element.width, 0).l(0,self._element.height).l(-self._element.width,0).Z()

    @_path.setter
    def _path(self, value):
        pass
