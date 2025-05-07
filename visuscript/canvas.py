from .drawable import Element, Drawable, Rect, Pivot
from visuscript.config import *
from .primatives import *
from typing import Tuple
import numpy as np
import svg    

class Canvas(Drawable):
    def __init__(self, *, elements: list[Element] | None = None, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, logical_width = CANVAS_LOGICAL_WIDTH, logical_height = CANVAS_LOGICAL_HEIGHT, color = 'dark_slate', **kwargs):
        assert width/height == logical_width/logical_height and width/logical_width == height/logical_height

        super().__init__(**kwargs)
        self._width = width
        self._height = height
        self._logical_width = logical_width
        self._logical_height = logical_height
        self._logical_scaling = width/logical_width

        self._elements: list[Element] = [] if elements is None else list(elements)
        self.anchor = Drawable.CENTER
        self.color: Color = Color(color)

        
    
    def clear(self):
        self._elements = set()

    def with_element(self, element: Element) -> Self:
        self._elements.append(element)
        return self
    add_element = with_element

    def with_elements(self, elements: list[Element]) -> Self:
        self._elements.extend(elements)
        return self
    add_elements = with_elements

    def without_element(self, element: Element) -> Self:
        self._elements.remove(element)
        return self
    remove_element = without_element

    def without_elements(self, elements: list[Element]) -> Self:
        for element in elements:
            self._elements.remove(element)
        return self
    remove_elements = without_elements

    def __lshift__(self, other: Element | list[Element]):
        if isinstance(other, list):
            self.add_elements(other)
        elif isinstance(other, Element):
            self.add_element(other)
        else:
            raise TypeError("'<<' is implemented only for types Element and list[Element]")
        

    # def __rshift__(self, other: Element | list[Element]):
    #     if isinstance(other, list):
    #         self.remove_elements(other)
    #     elif isinstance(other, Element):
    #         self.remove_element(other)
    #     else:
    #         raise TypeError("'<<' is implemented only for types Element and list[Element]")

    def a(self, percentage: float) -> float:
        """
        Returns a percentage of the total logical canvas area.
        """
        return percentage * self._logical_width * self._logical_height
    def x(self, x_percentage: float) -> float:
        return self._logical_width * x_percentage - self._logical_width/2
    def y(self, y_percentage: float) -> float:
        return self._logical_height * y_percentage - self._logical_height/2
    def xy(self, x_percentage: float, y_percentage: float) -> np.ndarray:
        return np.array([
            self.x(x_percentage),
            self.y(y_percentage)
        ])
    
    @property
    def top_left(self) -> np.ndarray:
        return np.array([0,0], dtype=float)

    @property
    def width(self) -> float:
        return self._width
    @property
    def height(self) -> float:
        return self._height
    
    def set_zoom(self, zoom: Transform):
        self.zoom = zoom
        return self

    def draw(self) -> str:
        background = Rect(width=self.width, height=self.height, fill = self.color, anchor=Drawable.TOP_LEFT)

        transform = Transform(
            translation= [self.width/2, self.height/2, 0] + self.transform.translation*self._logical_scaling,
            scale = self.transform.scale * self._logical_scaling,
            rotation = self.transform.rotation
        )

        # removed deleted elements
        self._elements = list(filter(lambda x: not x.deleted, self._elements))
        
        # translation = ( - transform.translation * self._logical_scaling) * transform.scale
        # translation = (-transform.translation)/(scale * self._logical_scaling) * self.transform.scale



        head = Pivot().set_transform(transform).with_children(self._elements)
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.width, self.height),
            elements= [background] + list(head)).as_str()
    

