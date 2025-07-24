from typing import no_type_check
from io import BytesIO


from PIL import Image as PILImage
import base64
import svg

from visuscript.primatives import *
from visuscript.segment import Path
from visuscript.drawable.mixins import HierarchicalDrawable, HasGlobalShape, HasAnchor, HasFill, HasStroke, HasOpacity



def get_base64_from_pil_image(pil_image: PILImage.Image) -> str:
    """
    Converts a PIL Image object to a base64 encoded string.
    """
    buffered = BytesIO()
    image_format = (
        pil_image.format if pil_image.format else "PNG"
    )  # Default to PNG if format is None
    pil_image.save(buffered, format=image_format)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode("utf-8")
    return img_str


class Image(HasGlobalShape, HierarchicalDrawable, HasAnchor):
    @no_type_check
    def __init__(
        self,
        *,
        filename: str | Sequence[Sequence[int]],
        width: float | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if isinstance(filename, str):
            img = PILImage.open(filename)
        else:
            filename = np.array(filename, dtype=np.uint8)
            assert len(filename.shape) == 3

            img = PILImage.fromarray(filename, mode="RGB")

        self._width, self._height = img.size
        self.resolution = (self._width, self._height)
        if width is None:
            self._resize_scale = 1
        else:
            self._resize_scale = width / self._width

        self._file_data = get_base64_from_pil_image(img)

        img.close()

    @property
    def anchor_offset(self):
        return super().anchor_offset / self._resize_scale

    @property
    def top_left(self):
        return Vec2(0, 0)

    @property
    def width(self) -> float:
        return self._width * self._resize_scale

    @property
    def height(self) -> float:
        return self._height * self._resize_scale

    @no_type_check
    def draw_self(self):
        x, y = self.anchor_offset

        return svg.Image(
            x=x,
            y=y,
            opacity=self.global_opacity,
            transform=self.global_transform.svg_transform,
            href=f"data:image/png;base64,{self._file_data}",
        ).as_str()


class Pivot(HierarchicalDrawable):
    """A Pivot is an Element with no display for itself.

    A Pivot can be used to construct more complex object by adding children."""

    @property
    def top_left(self):
        return Vec2(0, 0)

    @property
    def width(self) -> float:
        return 0.0

    @property
    def height(self) -> float:
        return 0.0

    def draw_self(self):
        return ""


class Drawing(HasGlobalShape, HierarchicalDrawable, HasFill, HasStroke, HasAnchor, HasOpacity):
    """A Drawing is an Element for which the self-display is defined by a Path."""

    def __init__(self, path: Path):
        super().__init__()

        self._path: Path = path

    def point(self, length: float) -> Vec2:
        return self.transform(
            Transform(self._path.set_offset(*self.anchor_offset).point(length))
        ).translation.xy

    def point_percentage(self, p: float) -> Vec2:
        return self.transform(
            Transform(self._path.set_offset(*self.anchor_offset).point_percentage(p))
        ).translation.xy

    def global_point(self, length: float) -> Vec2:
        return self.global_transform(
            Transform(self._path.set_offset(*self.anchor_offset).point(length))
        ).translation.xy
    

    def calculate_top_left(self):
        return self._path.top_left
    def calculate_width(self):
        return self._path.width
    def calculate_height(self):
        return self._path.height
    def draw_self(self):
        self._path.set_offset(*self.anchor_offset)
        return f"""<path \
d="{self._path.path_str}" \
transform="{self.global_transform.svg_transform}" \
stroke="{self.stroke.rgb}" \
stroke-opacity="{self.stroke.opacity}" \
stroke-width="{self.stroke_width}" \
fill="{self.fill.rgb}" \
fill-opacity="{self.fill.opacity}" \
opacity="{self.global_opacity}"\
/>"""


# TODO Make Circle a Drawing by adding a Path that approximates the circle
class Circle(HasGlobalShape, HierarchicalDrawable, HasFill, HasStroke, HasAnchor, HasOpacity):
    """A Circle"""

    def __init__(self, radius: float):
        super().__init__()
        self.radius = radius


    def calculate_top_left(self):
        return Vec2(-self.radius, -self.radius)

    def calculate_width(self):
        return self.radius * 2

    def calculate_height(self):
        return self.radius * 2

    def calculate_circumscribed_radius(self):
        return self.radius

    def draw_self(self):
        x, y = self.global_shape.center
        return f"""<path
        cx="{x}"
        cy="{y}"
        r="{self.radius}"
        transform="{self.global_transform.svg_transform}"
        stroke="{self.stroke.rgb}"
        stroke-opacity="{self.stroke.opacity}"
        stroke-width="{self.stroke_width}"
        fill="{self.fill.rgb}"
        fill-opacity="{self.fill.opacity}"
        opacity="{self.global_opacity}"
        >
        """

class Rect(Drawing):
    """A Rectangle"""

    def __init__(self, width, height):
        super().__init__(
            Path().l(width, 0).l(0, height).l(-width, 0).Z()
            )
