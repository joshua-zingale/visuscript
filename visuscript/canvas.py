from visuscript.drawable import Drawable
from visuscript.constants import Anchor, OutputFormat
from visuscript.element import Rect
from visuscript.updater import Updater, UpdaterBundle
from visuscript.primatives import *
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG
from typing import Iterable, Generator
from copy import copy
from visuscript.output import print_svg
import numpy as np
import svg

from visuscript.animation import AnimationBundle, Animation


class Canvas(Drawable):
    def __init__(self, *,
                 drawables: list[Drawable] | None = None,
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

        self._drawables: list[Drawable] = [] if drawables is None else list(drawables)
        self.color: Color = Color(color)
        self._output_format = output_format
        self._output_stream = output_stream

        
    
    def clear(self):
        self._drawables = set()

    def with_drawable(self, drawable: Drawable) -> Self:
        self._drawables.append(drawable)
        return self
    add_drawable = with_drawable

    def with_drawables(self, drawables: Iterable[Drawable]) -> Self:
        self._drawables.extend(drawables)
        return self
    add_drawables = with_drawables

    def without_drawable(self, drawable: Drawable) -> Self:
        self._drawables.remove(drawable)
        return self
    remove_drawable = without_drawable

    def without_drawables(self, drawables: list[Drawable]) -> Self:
        for drawable in drawables:
            self._drawables.remove(drawable)
        return self
    remove_drawables = without_drawables

    def __lshift__(self, other: Drawable | Iterable[Drawable]):
        if other is None:
            return
        
        if isinstance(other, Drawable):
            self.add_drawable(other)
        elif isinstance(other, Iterable):
            for drawable in other:
                self << drawable
        else:
            raise TypeError(f"'<<' is not implemented for {type(other)}, only for types Drawable and Iterable[Drawable]")

    def a(self, percentage: float) -> float:
        """
        Returns a percentage of the total logical canvas area.
        """
        return percentage * self._logical_width * self._logical_height
    def x(self, x_percentage: float) -> float:
        return self._logical_width * x_percentage + self.anchor_offset.x
    def y(self, y_percentage: float) -> float:
        return self._logical_height * y_percentage + self.anchor_offset.y
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
        return self._logical_width
    @property
    def height(self) -> float:
        return self._logical_height
    
    @property
    def logical_scaling(self):
        return self._logical_scaling
    
    
    def draw(self) -> str:

        inv_rotation = Transform(rotation=-self.transform.rotation)

        transform = Transform(
            translation = -inv_rotation(self.transform.translation*self.logical_scaling/self.transform.scale) - self.anchor_offset.extend(0)*self.logical_scaling,
            scale = self.logical_scaling/self.transform.scale,
            rotation = -self.transform.rotation
        )
        
        background = Rect(width=self.width*self.logical_scaling, height=self.height*self.logical_scaling, fill = self.color, stroke=self.color, anchor=Anchor.TOP_LEFT)

        # removed deleted drawables
        # self._drawables = list(filter(lambda x: not x.deleted, self._drawables))
        
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(0,0, self.width*self.logical_scaling, self.height*self.logical_scaling),
            elements= [background.draw(),
                       svg.G(elements=[drawable.draw() for drawable in self._drawables], transform=transform.svg_transform)
                       ]).as_str()

    def print(self):
        if self._output_format == OutputFormat.SVG:
            print_svg(self, file=self._output_stream)
        else:
            raise ValueError("Invalid image output format")

    def __enter__(self) -> Self:
        self._original_drawables = copy(self._drawables)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print()
        self._drawables = self._original_drawables
        del self._original_drawables


class _Player:
    def __init__(self, scene: "Scene"):
        self._scene = scene
    
    def __lshift__(self, animation: Animation):
        while animation.advance():
            self._scene.print()

class Scene(Canvas):

    def __init__(self, print_initial=True, **kwargs):
        super().__init__(**kwargs)
        self._print_initial = print_initial
        self._animation_bundle: AnimationBundle = AnimationBundle()
        self._player = _Player(self)

        self._original_drawables = []
        self._original_animation_bundle = []
        self._original_updater_bundle = []

        self._updater_bundle: UpdaterBundle = UpdaterBundle()
        self._number_of_frames_animated: int = 0

        # TODO the PropertLockers for the animation and updater bundles should be linked to ensure no contradictions
    
    @property
    def animations(self):
        return self._animation_bundle
    
    @property
    def updaters(self):
        return self._updater_bundle
    
    @property
    def player(self):
        return self._player
        
        
    def iter_frames(self) -> Generator[Self]:
        while self._animation_bundle.advance():
            time_since_beginning = self._number_of_frames_animated/config.fps
            self.updaters.update(time_since_beginning, 1/config.fps)
            self._number_of_frames_animated += 1
            yield self

        self._animation_bundle.clear()


    def print_frames(self):
        for _ in self.iter_frames():
            self.print()

    def __enter__(self) -> Self:
        self._original_drawables.append(copy(self._drawables))
        self._original_animation_bundle.append(self._animation_bundle)
        self._original_updater_bundle.append(self._updater_bundle)
        self._animation_bundle = AnimationBundle()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._print_initial:
            self.print()
        self.print_frames()
        self._drawables = self._original_drawables.pop()
        self._animation_bundle = self._original_animation_bundle.pop()
        self._updater_bundle = self._original_updater_bundle.pop()
