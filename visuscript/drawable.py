from .primatives import *
from typing import Self
from abc import ABC, abstractmethod


class Shape:
    def __init__(self, drawable: "Drawable", external_transform: Transform = Transform()):
        transform = external_transform(drawable.transform)


        self.top_left: Vec2 = transform @ (drawable.top_left + drawable.anchor_offset)
        self.width: float = drawable.width * transform.scale.x
        self.height: float = drawable.height * transform.scale.y
        self.circumscribed_radius: float = drawable.circumscribed_radius * transform.scale.xy.max()

        self.center: Vec2 = self.top_left + [self.width/2, self.height/2]
class Drawable(ABC):

    DEFAULT: int = 0
    TOP_LEFT: int = 1
    RIGHT: int = 4
    BOTTOM_LEFT: int = 7
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
    def anchor_offset(self) -> Vec2:
        """
        The (x,y) offset of this drawable for it to be anchored properly.
        """
        if self.anchor == Drawable.DEFAULT:
            return Vec2(0,0)
        if self.anchor == Drawable.RIGHT:
            return -(self.top_left + [self.width, self.height/2])
        if self.anchor == Drawable.BOTTOM_LEFT:
            return -(self.top_left + [0, self.height])
        if self.anchor == Drawable.LEFT:
            return -(self.top_left + [0, self.height/2])
        if self.anchor == Drawable.TOP_LEFT:
            return -self.top_left
        if self.anchor == Drawable.CENTER:
            return -(self.top_left + [self.width/2, self.height/2])
        

    @property
    def center(self) -> Vec2:
        return self.top_left + [self.width/2, self.height/2]

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