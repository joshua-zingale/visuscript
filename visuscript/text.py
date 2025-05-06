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
    

    @Element.lock_svg_pivot
    @Element.anchor
    @Element.globify
    def draw_self(self):

        # g_tfm = self.global_transform
        # scale = g_tfm.scale_x

        # font_size = self.font_size*scale
        # approximate_font_size = round(font_size, 1)
        # corrective_scaling = font_size/approximate_font_size

        # font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", approximate_font_size).font
        # size = font.getsize(self.text)

        # width = size[0][0] * corrective_scaling
        # height = size[0][1] * corrective_scaling

        # if self.anchor == Element.CENTER:
        #     anchor_transform = Transform([-width/2, height/2])
        # elif self.anchor == Element.TOP_LEFT:
        #     anchor_transform = Transform([0, height])

        # g_tfm = anchor_transform(g_tfm)

        return svg.Text(
            text=self.text,
            transform=self.svg_transform,
            font_size=self.font_size,
            font_family=self.font_family,
            fill=self.fill.rgb,
            fill_opacity=self.fill.opacity
            ).as_str()



