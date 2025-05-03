from .drawings import Element
from .primatives import *
from PIL import ImageFont
import svg

class Text(Element):

    def __init__(self, *, text: str, font_size: int, font_family: str = 'arial', fill = None, **kwargs):
            super().__init__(**kwargs)
            self.text: str = text
            self.font_size: int = font_size
            self.font_family: str = font_family
            self.fill: Color = Color(fill) if fill is not None else Color()

    @property
    def top_left(self) -> np.ndarray:
         return np.array([0, self.height], dtype=float)

    @property
    def width(self) -> float:
        font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
        size = font.getsize(self.text)
        return size[0][0]
    
    @property
    def height(self) -> float:
        font = ImageFont.truetype(f"fonts/{self.font_family.upper()}.ttf", self.font_size).font
        size = font.getsize(self.text)
        return size[0][1]

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



