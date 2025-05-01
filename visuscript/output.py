from wand.image import Image
from .drawings import Drawing
from io import BytesIO
import sys

def make_frame(drawing: Drawing) -> Image:
    img_bytes = BytesIO(drawing.draw().encode('utf-8'))
    img = Image(blob=img_bytes, format='svg')
    img.format = 'png'
    img.resize(1920, 1080)
    return img


def print_frame(drawing: Drawing) -> None:
    make_frame(drawing).save(file=sys.stdout.buffer)