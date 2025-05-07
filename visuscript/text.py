from .drawable import Element
from .primatives import *
from PIL import ImageFont
import svg

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
     def __init__(self, *, text: str, font_size: float, font_family: str = 'arial', fill = None, **kwargs):
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


     @Element.anchor
     @Element.globify
     def draw_self(self):
          x, y = self.anchor_offset

          return svg.Text(
               # x=x,
               # y=y,
               text=self.text,
               transform=self.svg_transform,
               font_size=self.font_size,
               font_family=self.font_family,
               fill=self.fill.rgb,
               fill_opacity=self.fill.opacity
               ).as_str()


