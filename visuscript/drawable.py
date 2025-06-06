"""This module contains the abstract base class for all Drawable objects."""

from .primatives import *
from .constants import Anchor
from .config import *
from typing import Self
from abc import ABC, abstractmethod
from visuscript._invalidator import Invalidatable
from functools import cached_property


class Shape:
    """A class that holds geometric properties for a Drawable"""

    def __init__(self, drawable: "Drawable", transform: Transform = Transform()):
        """
        :param drawable: The Drawable for which to initialize a Shape
        :type drawable: Drawable
        :param transform: Applies this transform to the Shape of drawable, defaults to Transform()
        :type transform: Transform, optional
        """        

        top_left = drawable.top_left + drawable.anchor_offset

        self.width: float = drawable.width * transform.scale.x
        """The width of the drawable's rectangular circumscription."""
        
        self.height: float = drawable.height * transform.scale.y
        """The height of the drawable's rectangular circumscription."""

        self.circumscribed_radius: float = drawable.circumscribed_radius * transform.scale.xy.max()
        """The radius of the smallest circle that circumscribes the drawable."""

        self.top_left: Vec2 =  transform @ (top_left)
        """The top-left coordinate of the drawable's rectangular circumscription."""

        self.top: Vec2 = transform @ (top_left + [drawable.width/2, 0])
        """The top-middle coordinate of the drawable's rectangular circumscription."""

        self.top_right: Vec2 = transform @ (top_left + [drawable.width, 0])
        """The top-right coordinate of the drawable's rectangular circumscription."""
        
        self.left: Vec2 = transform @ (top_left +[0, drawable.height/2])
        """The left-middle coordinate of the drawable's rectangular circumscription."""

        self.bottom_left: Vec2 = transform @ (top_left + [0, drawable.height])
        """The bottom-left coordinate of the drawable's rectangular circumscription."""

        self.bottom: Vec2 = transform @ (top_left + [drawable.width/2, drawable.height])
        """The bottom-middle coordinate of the drawable's rectangular circumscription."""

        self.bottom_right: Vec2 = transform @ (top_left + [drawable.width, drawable.height])
        """The bottom-right coordinate of the drawable's rectangular circumscription."""

        self.right: Vec2 = transform @ (top_left + [drawable.width, drawable.height/2])
        """The right-middle coordinate of the drawable's rectangular circumscription."""

        self.center: Vec2 = transform @ (top_left + [drawable.width/2, drawable.height/2])
        """The center coordinate of the drawable's rectangular circumscription."""

class Drawable(ABC, Invalidatable):
    """The base class of all Drawables."""

    def __init__(self, *,
                transform: Transform | None = None,
                anchor: Anchor = Anchor.CENTER,
                stroke: Color | ConfigurationDeference = DEFER_TO_CONFIG,
                stroke_width: float | ConfigurationDeference = DEFER_TO_CONFIG,
                fill: Color | ConfigurationDeference = DEFER_TO_CONFIG,
                opacity: float = 1.0,
                ):
        
        stroke = config.element_stroke if stroke is DEFER_TO_CONFIG else stroke
        stroke_width = config.element_stroke_width if stroke_width is DEFER_TO_CONFIG else stroke_width
        fill = config.element_fill if fill is DEFER_TO_CONFIG else fill
        
        self._transform: Transform = Transform() if transform is None else Transform(transform)
        self._transform._add_invalidatable(self)
        
        self.anchor: Anchor = anchor # TODO make Anchor an unmodifiable property

        self._stroke: Color = Color(stroke)
        self.stroke_width: float = stroke_width
        self._fill: Color = Color(fill)

        self.opacity: float = opacity


    def _invalidate(self):
        if hasattr(self, 'transformed_shape'):
            del self.transformed_shape

    @property
    def stroke(self):
        return self._stroke
    @property
    def fill(self):
        return self._fill
    @property
    def transform(self):
        return self._transform    

    def translate(self, x: float | None = None, y: float | None = None, z: float | None = None) -> Self:
        """Sets the translation on this Drawable's Transform.

        Any of x,y, and z not set will be set in the new translation to match the current value on this Drawable's Transfom.translation.
        """
        if x is None:
            x = self.transform.translation.x
        if y is None:
            y = self.transform.translation.y
        if z is None:
            z = self.transform.translation.z

        self.transform.translation = Vec3(x,y,z)
        return self
    
    def scale(self, scale: int | float | Collection[float]) -> Self:
        """Sets the scale on this Drawable's Transform."""
        self.transform.scale = scale
        return self
    
    def rotate(self, degrees: float) -> Self:
        """Sets the rotation on this Drawable's Transform."""
        self.transform.rotation = degrees
        return self

    
    def set_transform(self, transform: Transform) -> Self:
        """Sets this Drawable's Transform."""
        self._transform.update(Transform(transform))
        return self
    
    def set_anchor(self, anchor: Anchor, keep_position = False):
        """Sets this Drawable's anchor.

        :param anchor: The anchor to set for this Drawable
        :type anchor: Anchor
        :param keep_position: If True, updates this Drawable's translation such that the visual position of this Drawable will not change, defaults to False
        :type keep_position: bool, optional
        :return: self
        :rtype: Self
        """
        old_anchor_offset = self.anchor_offset

        self.anchor = anchor

        if keep_position:
            self.translate(*old_anchor_offset - self.anchor_offset)
            # Invalidate shapes
            if hasattr(self, 'shape'):
                del self.shape
            if hasattr(self, 'transformed_shape'):
                del self.transformed_shape
        return self
    
    @property
    def anchor_offset(self) -> Vec2:
        """The (x,y) offset of this drawable for it to be anchored properly."""
        if self.anchor == Anchor.DEFAULT:
            return Vec2(0,0)
        if self.anchor == Anchor.TOP_LEFT:
            return -self.top_left
        if self.anchor == Anchor.TOP:
            return -(self.top_left + [self.width/2, 0])
        if self.anchor == Anchor.TOP_RIGHT:
            return -(self.top_left + [self.width, 0])
        if self.anchor == Anchor.RIGHT:
            return -(self.top_left + [self.width, self.height/2])
        if self.anchor == Anchor.BOTTOM_RIGHT:
            return -(self.top_left + [self.width/2, self.height])
        if self.anchor == Anchor.BOTTOM:
            return -(self.top_left + [self.width/2, self.height])
        if self.anchor == Anchor.BOTTOM_LEFT:
            return -(self.top_left + [0, self.height])
        if self.anchor == Anchor.LEFT:
            return -(self.top_left + [0, self.height/2])
        if self.anchor == Anchor.CENTER:
            return -(self.top_left + [self.width/2, self.height/2])
        else:
            raise NotImplementedError()

    def set_opacity(self, value: float) -> Self:
        """Sets the opaciy for this Drawable."""
        self.opacity = value
        return self
    
    def set_stroke_width(self, value: float) -> Self:
        """Sets the stroke width for this Drawable."""
        self.stroke_width = value
        return self
    
    def set_fill(self, color: Color) -> Self:
        """Sets the fill for this Drawable."""
        color = Color(color)
        self.fill.rgb = color.rgb
        self.fill.opacity = color.opacity
        return self
    
    def set_stroke(self, color: Color) -> Self:
        """Sets the fill for this Drawable."""
        color = Color(color)
        self.stroke.rgb = color.rgb
        self.stroke.opacity = color.opacity
        return self
        
    @abstractmethod
    def draw(self) -> str:
        """Returns the SVG representation of this drawable."""
        ...
    
    @property
    @abstractmethod
    def top_left(self) -> Vec2:
        """The un-transformed top-left (x,y) coordinate for this Drawable."""
        ...
            
    @property
    @abstractmethod
    def width(self) -> float:
        """The un-transformed width of this Drawable."""
        ...
    @property
    @abstractmethod
    def height(self) -> float:
        """The un-transformed height of this Drawable."""
        ...

    @property
    def circumscribed_radius(self):
        """The radius of the smallest circle centered at this un-transformed Drawable's center that can circumscribe this Drawable."""
        return (self.width**2 + self.height**2)**0.5/2    
    
    #TODO use a more robust caching system.
    # As of writing, Shape is invalidated by updating the Anchor position
    @cached_property
    def shape(self):
        """The un-transformed Shape for this Drawable."""
        return Shape(self)
    
    @cached_property
    def transformed_shape(self):
        """The Shape for this Drawable when it has been transformed by its Transform."""
        return Shape(self, self.transform)