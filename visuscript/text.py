from .drawable import Element
from xml.sax.saxutils import escape as xml_escape
from .primatives import *
from PIL import ImageFont
import svg
import sys

def escape_with_leading_spaces(data):
    """
    Escapes a string for XML while preserving leading spaces.

    Args:
        data: The input string.

    Returns:
        The XML-escaped string with leading spaces preserved.
    """
    leading_spaces = ""
    for char in data:
        if char == " ":
            leading_spaces += "&#160;"
        else:
            break
    return leading_spaces + xml_escape(data.lstrip(" "))

class Text(Element):
     @staticmethod
     def update_size(foo):
          
          def size_updating_method(self, *args, **kwargs):
               r = foo(self, *args, **kwargs)
               font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
               size = font.getsize(self.text)
               self._width = size[0][0]
               self._height = size[0][1]

               return r
          return size_updating_method

     @update_size
     def __init__(self, *, text: str, font_size: float, font_family: str = 'arial', fill: Color | None = None, **kwargs):
               super().__init__(**kwargs)
               self._text: str = text
               self._font_size: float = font_size
               self._font_family: str = font_family
               self.fill: Color = Color(fill) if fill is not None else Color()


     @property
     def font_family(self) -> str:
          return self._font_family

     @font_family.setter
     @update_size
     def font_family(self, value: str):
          self._font_family = value


     @property
     def text(self) -> str:
          return self._text

     @text.setter
     @update_size
     def text(self, value: str):
          self._text = value


     @property
     def font_size(self) -> float:
          return self._font_size

     @font_size.setter
     @update_size
     def font_size(self, value: float):
          self._font_size = value

     @property
     def top_left(self) -> np.ndarray:
          return np.array([0, -self.height], dtype=float)


     @property
     def width(self) -> float:
          return self._width


     @property
     def height(self) -> float:
          return self._height


     # @Element.anchor
     # @Element.globify
     def draw_self(self):
          x, y = self.anchor_offset
          return svg.Text(
               x=x,
               y=y,
               text=escape_with_leading_spaces(self.text),
               transform=str(self.global_transform),
               font_size=self.font_size,
               font_family=self.font_family,
               fill=self.fill.rgb,
               fill_opacity=self.fill.opacity
               ).as_str() + "<text/>" # The extra tag is to skirt a bug in the rendering of the SVG


