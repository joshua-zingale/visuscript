from visuscript.element import Element
from xml.sax.saxutils import escape
from .primatives import *
from PIL import ImageFont
import svg

# TODO Figure out why league mono is not centered properly
fonts: dict[str, str] =  {
    "league mono": "LeagueMono-2.300/static/TTF/LeagueMono-WideLight.ttf",
    "arimo": "Arimo/Arimo-VariableFont_wght.ttf",
    "arial": "Arimo/Arimo-VariableFont_wght.ttf"
}

def xml_escape(data: str) -> str:
     # Trailing spaces lead to odd display behavior where A's with circumflexes appear wherever there should be a space.
     # Therefore is the input string right-stripped.
     return escape(data.rstrip(), entities={
        " ": "&#160;",
    })


class Text(Element):
     @staticmethod
     def update_size(foo):
          def size_updating_method(self: "Text", *args, **kwargs):
               global fonts
               r = foo(self, *args, **kwargs)

               # Hack to get bounding box from https://stackoverflow.com/a/46220683
               # TODO Use an appropriate public API from PIL to get these metrics
               font = ImageFont.truetype(f"fonts/{fonts[self.font_family]}", self.font_size)
               ascent, descent = font.getmetrics()
               (width, height), (offset_x, offset_y) = font.font.getsize(self.text)
               self._width = width
               self._height = ascent - offset_y

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

     def draw_self(self):
          x, y = self.anchor_offset
          return svg.Text(
               x=x,
               y=y,
               text=xml_escape(self.text),
               transform=self.global_transform.svg_transform,
               font_size=self.font_size,
               font_family=self.font_family,
               font_style="normal",
               fill=self.fill.rgb,
               fill_opacity=self.fill.opacity
               ).as_str() + "<text/>" # The extra tag is to skirt a bug in the rendering of the SVG



def get_multiline_texts(text: str, font_size: float, **kwargs) -> Text:

     head = None
     for i, line in enumerate(text.split("\n")):
          text_obj = Text(text=line, font_size=font_size, **kwargs).set_transform([0,i*font_size])
          if i == 0:
               head = text_obj
          else:
               text_obj.set_parent(head)

     return head

     