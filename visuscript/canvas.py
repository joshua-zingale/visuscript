from .drawings import Element, Drawable, Rect
from .primatives import *
from typing import Tuple
import numpy as np
import svg

class Head(Element):
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
    

class Canvas(Drawable):
    def __init__(self, *, elements: list[Element] | None = None, width=1920, height=1080, logical_width = 480, logical_height = 270, color = 'dark_slate', **kwargs):

        super().__init__(**kwargs)
        elements = [] if elements is None else elements
        self.anchor = Drawable.CENTER
        self.color: Color = Color(color)
        self._head = Head().with_children(elements)


        assert width/height == logical_width/logical_height and width/logical_width == height/logical_height

        self._width = width
        self._height = height
        self._logical_width = logical_width
        self._logical_height = logical_height
        self._logical_scaling = width/logical_width


        self._head.transform.scale = np.array([self._logical_scaling, self._logical_scaling, 1])

    
    def with_elements(self, elements: list[Element]) -> Self:
        self._head.with_children(elements)
        return self
    


    def a(self, percentage: float) -> float:
        """
        Returns a percentage of the total logical canvas area.
        """
        return percentage * self._logical_width * self._logical_height
    def w(self, x_percentage: float) -> float:
        return self._logical_width * x_percentage
    def h(self, y_percentage: float) -> float:
        return self._logical_height * y_percentage
    def p(self, x_percentage: float, y_percentage: float) -> Tuple[float, float]:
        return (
            self._logical_width * x_percentage,
            self._logical_height * y_percentage
        )
    
    @property
    def top_left(self) -> np.ndarray:
        return np.array([0,0], dtype=float)

    @property
    def width(self) -> float:
        return self._width
    @property
    def height(self) -> float:
        return self._height
    
    @property
    def zoom(self) -> Transform:
        transform = self._head.transform.copy()

        scale = transform.scale / self._logical_scaling
        translation = ([self.width/2, self.height/2, 0] - transform.translation)/(scale * self._logical_scaling)

        transform.translation = translation
        transform.scale = scale
        return transform

    @zoom.setter
    def zoom(self, zoom: Transform):
        self._head.transform.scale = zoom.scale * self._logical_scaling
        self._head.transform.translation = [self.width/2, self.height/2, 0] - zoom.translation*zoom.scale*self._logical_scaling
    
    def set_zoom(self, zoom: Transform):
        self.zoom = zoom
        return self
    


    def draw(self) -> str:
        background = Rect(width=self.width, height=self.height, fill = self.color, anchor=Drawable.TOP_LEFT)
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.width, self.height),
            elements= [background] + list(self._head)).as_str()
