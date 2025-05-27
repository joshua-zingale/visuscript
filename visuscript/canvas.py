from visuscript.drawable import Drawable
from visuscript.constants import Anchor, OutputFormat
from visuscript.element import Element
from visuscript import Rect, Pivot
from visuscript.primatives import *
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG
from typing import Iterable, Generator
from copy import copy
from visuscript.output import print_svg, print_png
import numpy as np
import svg

from visuscript.animation import AnimationBundle, Animation


class Canvas(Drawable):
    def __init__(self, *,
                 elements: list[Element] | None = None,
                 width: int | ConfigurationDeference = DEFER_TO_CONFIG,
                 height: int | ConfigurationDeference = DEFER_TO_CONFIG,
                 logical_width: int | ConfigurationDeference = DEFER_TO_CONFIG,
                 logical_height: int | ConfigurationDeference = DEFER_TO_CONFIG,
                 color: str | Color | ConfigurationDeference = DEFER_TO_CONFIG,
                 output_format: OutputFormat | ConfigurationDeference = DEFER_TO_CONFIG,
                 output_stream: ConfigurationDeference = DEFER_TO_CONFIG,
                 **kwargs):
        

        # from visuscript.config import config
        width = config.canvas_width if width is DEFER_TO_CONFIG else width
        height = config.canvas_height if height is DEFER_TO_CONFIG else height
        logical_width = config.canvas_logical_width if logical_width is DEFER_TO_CONFIG else logical_width
        logical_height = config.canvas_logical_height if logical_height is DEFER_TO_CONFIG else logical_height
        color = config.canvas_color if color is DEFER_TO_CONFIG else color
        output_format = config.canvas_output_format if output_format is DEFER_TO_CONFIG else output_format
        output_stream = config.canvas_output_stream if output_stream is DEFER_TO_CONFIG else output_stream
        
        assert width/height == logical_width/logical_height and width/logical_width == height/logical_height

        super().__init__(**kwargs)
        self._width = width
        self._height = height
        self._logical_width = logical_width
        self._logical_height = logical_height
        self._logical_scaling = width/logical_width

        self._elements: list[Element] = [] if elements is None else list(elements)
        self.color: Color = Color(color)
        self._output_format = output_format
        self._output_stream = output_stream

        
    
    def clear(self):
        self._elements = set()

    def with_element(self, element: Element) -> Self:
        self._elements.append(element)
        return self
    add_element = with_element

    def with_elements(self, elements: Iterable[Element]) -> Self:
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

    def __lshift__(self, other: Drawable | Iterable[Drawable]):
        if other is None:
            return
        
        if isinstance(other, Drawable):
            self.add_element(other)
        elif isinstance(other, Iterable):
            for drawable in other:
                self << drawable
        else:
            raise TypeError(f"'<<' is not implemented for {type(other)}, only for types Drawable and Iterable[Drawable]")
        

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
    def top_left(self) -> Vec2:
        return Vec2(0,0)

    @property
    def width(self) -> float:
        return self._width
    @property
    def height(self) -> float:
        return self._height
    


    def draw(self) -> str:

        translation = self.transform.translation*self._logical_scaling

        transform = Transform(
            translation = translation * self._logical_scaling*self.transform.scale,
            scale = self.transform.scale * self._logical_scaling,
            rotation = self.transform.rotation
        )
        
        background = Rect(width=self.width, height=self.height, fill = self.color, stroke=self.color, anchor=Anchor.TOP_LEFT).translate(*self.anchor_offset)

        # removed deleted elements
        self._elements = list(filter(lambda x: not x.deleted, self._elements))
        
        # head = Pivot().set_transform(transform).add_children(*self._elements)
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(*self.anchor_offset, self.width, self.height),
            elements= [background.draw(),
                       svg.G(elements=[element.draw() for element in self._elements], transform=transform.svg_transform)
                       ]).as_str()

    def print(self):
        if self._output_format == OutputFormat.SVG:
            print_svg(self, file=self._output_stream)
        elif self._output_format == OutputFormat.PNG:
            print_png(self, file=self._output_stream)
        else:
            raise ValueError("Invalid image output format")

    def __enter__(self) -> Self:
        self._original_elements = copy(self._elements)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print()
        self._elements = self._original_elements
        del self._original_elements


class _Player:
    def __init__(self, scene: "Scene"):
        self._scene = scene
    
    def __lshift__(self, animation: Animation):
        while animation.advance():
            self._scene.print()

class Scene(Canvas):

    def __init__(self, **kwargs):
        self._animation_bundle: AnimationBundle = AnimationBundle()
        self._player = _Player(self)
        self._original_elements = []
        self._original_animation_bundle = []
        super().__init__(**kwargs)
    
    @property
    def animations(self):
        #TODO check if the elements to be animated are elements of this scene and not already being animated
        return self._animation_bundle
    
    @property
    def player(self):
        return self._player
        
        
    @property
    def frames(self) -> Generator[Self]:
        while self._animation_bundle.advance():
            yield self

        self._animation_bundle.clear()


    def print_frames(self):
        for _ in self.frames:
            self.print()

    def __enter__(self) -> Self:
        self._original_elements.append(copy(self._elements))
        self._original_animation_bundle.append(self._animation_bundle)
        self._animation_bundle = AnimationBundle()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print_frames()
        self._elements = self._original_elements.pop()
        self._animation_bundle = self._original_animation_bundle.pop()
