

from typing import Concatenate, ParamSpec, Callable, TypeVar
import os


from xml.sax.saxutils import escape
from ..primatives import *
from PIL import ImageFont


from visuscript.drawable.mixins import HierarchicalDrawable, AnchorMixin, FillMixin, GlobalShapeMixin
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG

# TODO Figure out why league mono is not centered properly
fonts: dict[str, str] = {
    "league mono": "LeagueMono-2.300/static/TTF/LeagueMono-WideLight.ttf",
    "arimo": "Arimo/Arimo-VariableFont_wght.ttf",
    "arial": "Arimo/Arimo-VariableFont_wght.ttf",
}


def xml_escape(data: str) -> str:
    # Trailing spaces lead to odd display behavior where A's with circumflexes appear wherever there should be a space.
    # Therefore is the input string right-stripped.
    return escape(
        data.rstrip(),
        entities={
            " ": "&#160;",
        },
    )




_P = ParamSpec("_P")
_T = TypeVar("_T")
_Text = TypeVar("_Text", bound="Text")

class Text(GlobalShapeMixin, HierarchicalDrawable, AnchorMixin, FillMixin):
    
    @staticmethod
    def update_size(
        foo: Callable[Concatenate[_Text, _P], _T],
    ) -> Callable[Concatenate[_Text, _P], _T]:
        def size_updating_method(self: _Text, *args: _P.args, **kwargs: _P.kwargs):
            global fonts
            r = foo(self, *args, **kwargs)

            dir_path = os.path.dirname(os.path.realpath(__file__))
            font_path = os.path.join(dir_path, "fonts", fonts[self.font_family])
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Font file not found: {font_path}")

            # Hack to get bounding box from https://stackoverflow.com/a/46220683
            # TODO Use an appropriate public API from PIL to get these metrics
            font = ImageFont.truetype(font_path, self.font_size)
            ascent, _descent = font.getmetrics()
            (width, _height), (_offset_x, offset_y) = font.font.getsize(self.text)  # type: ignore
            self._width = width
            self._height = ascent - offset_y

            if hasattr(self, "shape"):
                del self.shape
            if hasattr(self, "global_shape"):
                del self.global_shape

            return r

        return size_updating_method

    def __init__(
        self,
        text: str,
        font_size: float | ConfigurationDeference = DEFER_TO_CONFIG,
        font_family: str | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        
        if isinstance(font_size, ConfigurationDeference):
            font_size = config.text_font_size
        if isinstance(font_family, ConfigurationDeference):
            font_family = config.text_font_family
        
        self._text: str = text
        self._font_size: float = font_size
        self._font_family: str = font_family
   

        # Initialized by the wrapper returned by "update_size"
        Text.update_size(lambda self: None)(self)
        self._width: float
        self._height: float

        super().__init__()
        self.set_fill(config.text_fill)

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

    def set_text(self, text: str) -> Self:
        self.text = text
        return self

    @property
    def font_size(self) -> float:
        return self._font_size

    @font_size.setter
    @update_size
    def font_size(self, value: float):
        self._font_size = value


    def calculate_top_left(self) -> Vec2:
        return Vec2(0, -self._height)
    def calculate_width(self) -> float:
        return self._width
    def calculate_height(self) -> float:
        return self._height

    def draw_self(self):
        x, y = self.anchor_offset
        return f"""\
<text \
x="{x}" \
y="{y}" \
transform="{self.global_transform.svg_transform}" \
font-size="{self.font_size}" \
font-family="{self.font_family}" \
font-style="normal" \
fill="{self.fill.rgb}" \
fill-opacity="{self.fill.opacity}" \
opacity="{self.global_opacity}"\
>{xml_escape(self.text)}</text><text/>""" # The extra tag is to skirt a bug in the rendering of the SVG