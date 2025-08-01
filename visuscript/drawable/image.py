from typing import no_type_check, Sequence
from io import BytesIO


from PIL import Image as PILImage
import base64
import svg
import numpy as np

from visuscript.primatives import *
from visuscript.primatives.mixins import (
    HierarchicalDrawable,
    GlobalShapeMixin,
    AnchorMixin,
)


def get_base64_from_pil_image(pil_image: PILImage.Image) -> str:
    """
    Converts a PIL Image object to a base64 encoded string.
    """
    buffered = BytesIO()
    image_format = pil_image.format if pil_image.format else "PNG"
    pil_image.save(buffered, format=image_format)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode("utf-8")
    return img_str


class Image(GlobalShapeMixin, HierarchicalDrawable, AnchorMixin):
    def __init__(
        self,
        *,
        filename: str | Sequence[Sequence[int]],
        width: float | None = None,
    ):
        super().__init__()

        if isinstance(filename, str):
            img = PILImage.open(filename)
        else:
            file = np.array(filename, dtype=np.uint8)
            assert len(file.shape) == 3

            img = PILImage.fromarray(file, mode="RGB")

        self._width, self._height = img.size
        self.resolution = (self._width, self._height)
        if width is None:
            self._resize_scale: float = 1
        else:
            self._resize_scale: float = width / self._width

        self._file_data = get_base64_from_pil_image(img)

        img.close()

    @property
    def anchor_offset(self) -> Vec2:
        return super().anchor_offset / self._resize_scale

    def calculate_top_left(self):
        return Vec2(0, 0)

    def calculate_width(self) -> float:
        return self._width * self._resize_scale

    def calculate_height(self) -> float:
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
