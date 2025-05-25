from visuscript.constants import Anchor, OutputFormat
from visuscript.primatives import Color
from typing import TypeAlias
import sys

class _AnimationConfig:
    def __init__(self):
        # Animation
        self.fps = 30
        self.animation_duration = 0.5

        # Canvas
        self.canvas_width = 480
        self.canvas_height = 270
        self.canvas_logical_width = 480
        self.canvas_logical_height = 270
        self.canvas_output_format = OutputFormat.SVG
        self.canvas_color = Color('dark_slate', 1)
        self.canvas_output_stream = sys.stdout

        # Drawing
        self.drawing_stroke = Color('off_white', 1)
        self.drawing_stroke_width = 1
        self.drawing_fill = Color('off_white', 0.0)

        # Text
        self.text_font_size = 16
        self.text_font_family = 'arial'
        self.text_fill = Color('off_white', 1)




config: _AnimationConfig = _AnimationConfig()
"""
The singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
"""

ConfigurationDeference: TypeAlias = object
"""
As an parameter type hint, specifies that passing in `DEFER_TO_CONFIG` as the argument will lead to the global configuration setting the value.
"""

DEFER_TO_CONFIG: ConfigurationDeference = object()
"""Indicates that this parameter should be set by the global configuration."""




# class _Config:
#     def __init__(self):
#         self._data = {}

#     def __getattr__(self, name):
#         if name not in self._data:
#             self._data[name] = _Config()
#         return self._data[name]

#     def __setattr__(self, name, value):
#         if name == '_data':
#             super().__setattr__(name, value)
#         else:
#             self._data[name] = value

#     def __delattr__(self, name):
#         if name in self._data:
#             del self._data[name]

#     def __repr__(self):
#         return f"<Config {self._data}>"

# config: _Config
# """
# The singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
# """
