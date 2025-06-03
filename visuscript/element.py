from visuscript.drawable import Drawable, Shape
from visuscript.constants import Anchor
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG
from .primatives import *
from .segment import Path, Segment
from io import StringIO
from typing import Self, Generator, Iterator
import numpy as np
import svg
from abc import abstractmethod
from PIL import Image as PILImage
from io import BytesIO
import base64

def get_base64_from_pil_image(pil_image: PILImage) -> str:
    """
    Converts a PIL Image object to a base64 encoded string.
    """
    buffered = BytesIO()
    image_format = pil_image.format if pil_image.format else "PNG"  # Default to PNG if format is None
    pil_image.save(buffered, format=image_format)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode('utf-8')
    return img_str

class Element(Drawable):
    """An Element is a Drawable that can be placed in a hierarcy, where ancestor's transforms are applied to an Element for the Element to be drawn."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._children: list["Element"] = []
        self._parent: "Element" | None = None
        self._svg_pivot = None
        self._deleted = False

    def iter_children(self) -> Iterator["Element"]:
        yield from self._children

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

    with_child = add_child
    
    def remove_child(self, child: "Element", preserve_global_transform: bool = True) -> Self:
        """
        Removes `child` as a child to this Element. If `preserve_global_transform` is True, then the
        transform on `child` is set such that its global transform not change.
        """
        if child not in self._children:
            raise ValueError("Attempted to remove a child from an Element that is not a child of the Element.")
        child.set_parent(None, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(self, *children: "Element", preserve_global_transform: bool = False) -> Self:
        """
        Adds each input child as a child of this Element. If `preserve_global_transform` is True, then the
        transform on each child is set such that its global transform not change.
        """
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self
    
    with_children = add_children
    
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
    
    @property
    def global_opacity(self) -> float:
        """
        The global opacity of this Element.

        Returns the product of all ancestor opacities and that of this Element.
        """
        curr = self

        opacity = self.opacity

        while curr._parent is not None:
            opacity *= curr._parent.opacity
            curr = curr._parent

        return opacity

    
    @global_transform.setter
    def global_transform(self, value: Transform):
        """
        Sets the global transform of this Element.
        """
        if self._parent is None:
            self.transform = value
        else:
            self.transform = self._parent.global_transform.inv(value)


    def __iter__(self) -> Iterator["Element"]:
        """
        Iterate over this Element and its children in ascending z order, secondarily ordering parents before children.
        """
        elements = [self]
        for child in self._children:
            elements.extend(child.__iter__())

        yield from sorted(elements, key=lambda d: d.global_transform.translation.z)

    def draw(self) -> str:
        string_builder = StringIO()

        drawlist = [(self, Transform())]

        while drawlist:
            element, inherited_transform = drawlist.pop(0)
            transform = inherited_transform @ element.transform
            string_builder.write(element.draw_self(transform))

            for child in element.iter_children():
                drawlist.append((child, transform))
            
        return string_builder.getvalue()
    
    @property
    def deleted(self) -> bool:
        return self._deleted
    
    def delete(self):
        for element in self:
            element._deleted = True
            element.set_parent(None)

    @property
    def global_shape(self):
        return Shape(self, self.global_transform)
    
    # TODO make children not move with respect to parnet when parent's anchor is updated with keep_position=True
    def set_anchor(self, anchor, keep_position=False) -> Self:
        return super().set_anchor(anchor, keep_position=keep_position)
    

    @abstractmethod
    def draw_self(self, transform: Transform) -> str:
        """
        Returns the SVG representation for this Element but not for its children.
        """
        ...


class Image(Element):

    def __init__(self, *, filename: str | Collection[Collection[int]], width: float | None = None, **kwargs):
        super().__init__(**kwargs)

        if isinstance(filename, str):
            img =  PILImage.open(filename)
        else:
            filename = np.array(filename, dtype=np.uint8)
            assert len(filename.shape) == 3

            img = PILImage.fromarray(filename, mode="RGB")

        
        self._width, self._height = img.size
        self.resolution = (self._width, self._height)
        if width is None:
            self._resize_scale = 1
        else:
            self._resize_scale = width/self._width
        
        self._file_data = get_base64_from_pil_image(img)

        img.close()

    @property
    def anchor_offset(self):
        return super().anchor_offset/self._resize_scale
    @property
    def top_left(self):
        return Vec2(0,0)
    
    @property
    def width(self) -> float:
        return self._width * self._resize_scale
    @property
    def height(self) -> float:
        return self._height * self._resize_scale

    def draw_self(self, transform: Transform):
        x, y = self.anchor_offset

        transform = deepcopy(transform)
        transform.scale = transform.scale * self._resize_scale
        return svg.Image(
            x=x,
            y=y,
            opacity=self.global_opacity,
            transform=transform.svg_transform,
            href=f"data:image/png;base64,{self._file_data}",
        ).as_str()

class Pivot(Element):
    """A Pivot is an Element with no display for itself.
    
    A Pivot can be used to construct more complex object by adding children."""
    @property
    def top_left(self):
        return Vec2(0,0)
    @property
    def width(self) -> float:
        return 0.0
    @property
    def height(self) -> float:
        return 0.0
    def draw_self(self, transform: Transform):
        return ""

class Drawing(Element, Segment):
    """A Drawing is an Element for which the self-display is defined by a Path."""
    def __init__(self,
                 path: Path,
                 *,
                 anchor = Anchor.DEFAULT,
                 **kwargs):
        
        super().__init__(anchor=anchor, **kwargs)

        self._path: Path = path

    def point(self, length: float) -> Vec2:
        return self.transform(Transform(self._path.set_offset(*self.anchor_offset).point(length))).translation.xy
    
    def point_percentage(self, p: float) -> Vec2:
        return self.transform(Transform(self._path.set_offset(*self.anchor_offset).point_percentage(p))).translation.xy
    
    def global_point(self, length: float) -> Vec2:
        return self.global_transform(Transform(self._path.set_offset(*self.anchor_offset).point(length))).translation.xy

    @property
    def top_left(self) -> Vec2:
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
    
    def draw_self(self, transform: Transform):
        self._path.set_offset(*self.anchor_offset)
        return svg.Path(
                d=self._path.path_str,
                transform=transform.svg_transform,
                stroke=self.stroke.svg_rgb,
                stroke_opacity=self.stroke.opacity,
                fill=self.fill.svg_rgb,
                fill_opacity=self.fill.opacity,
                opacity=self.global_opacity,
                stroke_width=self.stroke_width).as_str()
    

#TODO Make Circle a Drawing by adding a Path that approximates the circle
class Circle(Element):
    """A Circle"""

    def __init__(self, radius: float, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    @property
    def top_left(self):
        return Vec2(-self.radius, -self.radius)

    @property
    def width(self):
        return self.radius * 2
    @property
    def height(self):
        return self.radius * 2
    
    @property
    def circumscribed_radius(self):
        return self.radius

    def draw_self(self, transform: Transform):
        x, y = self.anchor_offset
        return svg.Circle(
            cx = x,
            cy = y,
            r=self.radius,
            transform=transform.svg_transform,
            stroke=self.stroke.svg_rgb,
            stroke_opacity=self.stroke.opacity,
            stroke_width=self.stroke_width,
            fill=self.fill.svg_rgb,
            fill_opacity=self.fill.opacity,
            opacity=self.global_opacity,
            ).as_str()


class Rect(Drawing):
    """A Rectangle"""
    def __init__(self, width, height, anchor: Anchor = Anchor.CENTER, **kwargs):
        super().__init__(Path().l(width, 0).l(0, height).l(-width, 0).Z(), anchor=anchor, **kwargs)