import sys

from visuscript.constants import OutputFormat
from visuscript.primatives.mixins.color import Color


class _AnimationConfig:
    def __init__(self):
        # Animation
        self.fps = 30
        self.animation_duration = 1

        # Scene
        self.scene_width = 480
        self.scene_height = 270
        self.scene_logical_width = 480
        self.scene_logical_height = 270
        self.scene_output_format = OutputFormat.SVG
        self._scene_color = Color("dark_slate", 1)
        self.scene_output_stream = sys.stdout

        # Drawing
        self._element_stroke = Color("off_white", 1)
        self.element_stroke_width = 1
        self._element_fill = Color("off_white", 0.0)

        # Text
        self.text_font_size = 16
        self.text_font_family = "arial"
        self._text_fill = Color("off_white", 1)


        # Slideshow
        self.slideshow_metadata_output_stream = sys.stderr

    @property
    def scene_color(self):
        return Color.construct(self._scene_color)

    @scene_color.setter
    def scene_color(self, value: Color):
        self._scene_color = Color.construct(value)

    @property
    def element_stroke(self):
        return Color.construct(self._element_stroke)

    @element_stroke.setter
    def element_stroke(self, value: Color):
        self._element_stroke = Color.construct(value)

    @property
    def element_fill(self):
        return Color.construct(self._element_fill)

    @element_fill.setter
    def element_fill(self, value: Color):
        self._element_fill = Color.construct(value)

    @property
    def text_fill(self):
        return Color.construct(self._text_fill)

    @text_fill.setter
    def text_fill(self, value: Color):
        self._text_fill = Color.construct(value)


config: _AnimationConfig = _AnimationConfig()
"""
The global singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
"""


class ConfigurationDeference:
    """As an parameter type hint, specifies that passing in `DEFER_TO_CONFIG` as the argument will lead to the global configuration setting the value."""


DEFER_TO_CONFIG: ConfigurationDeference = ConfigurationDeference()
"""Indicates that this parameter should be set by the global configuration."""
