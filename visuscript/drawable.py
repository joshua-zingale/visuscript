from .primatives import *
from .constants import Anchor
from typing import Self
from abc import ABC, abstractmethod


class Shape:
    """A class that holds geometric properties for a `drawable` under a possible transform."""

    def __init__(self, drawable: "Drawable", transform: Transform = Transform()):
        """Initializes a Shape for the input drawable alongisde an optional transform, which is applied to the local transform."""

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

class Drawable(ABC):

    def __init__(self, *, transform: Transform | None = None, anchor: Anchor = Anchor.CENTER):

        self.transform: Transform = Transform() if transform is None else Transform(transform)
        self.anchor = anchor

    def translate(self, x: float | None = None, y: float | None = None, z: float | None = None) -> Self:
        if x is None:
            x = self.transform.translation.x
        if y is None:
            y = self.transform.translation.y
        if z is None:
            z = self.transform.translation.z

        self.transform.translation = Vec3(x,y,z)
        return self
    
    def rotate(self, degrees: float) -> Self:
        self.transform.rotation = degrees
        return self

    def scale(self, scale: int | float | Collection[float]) -> Self:
        self.transform.scale = scale
        return self

    def rotate(self, rotation: int | float) -> Self:
        self.transform.rotation = rotation
        return self

    def set_transform(self, transform: Transform) -> Self:
        self.transform = Transform(transform)
        return self
    
    def set_anchor(self, anchor: Anchor):
        self.anchor = anchor
        return self
    
    @property
    def anchor_offset(self) -> Vec2:
        """
        The (x,y) offset of this drawable for it to be anchored properly.
        """
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
        
    

    @abstractmethod
    def draw(self) -> str:
        """
        Returns the SVG representation of this drawable.
        """
        ...
    
    @property
    @abstractmethod
    def top_left(self) -> Vec2:
        """
        The top left coordinate for this drawable.
        """
        ...
            
    @property
    @abstractmethod
    def width(self) -> float:
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

    @property
    def circumscribed_radius(self):
        return (self.width**2 + self.height**2)**0.5/2    
    
    
    @property
    def shape(self):
        return Shape(self)
    
    @property
    def transformed_shape(self):
        return Shape(self, self.transform)