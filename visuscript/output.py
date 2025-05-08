from wand.image import Image
from .canvas import Canvas
from io import BytesIO
import sys

def make_frame(drawing: Canvas) -> Image:
    img_bytes = BytesIO(drawing.draw().encode('utf-8'))
    img = Image(blob=img_bytes, format='svg')
    img.format = 'png'
    img.resize(drawing.width, drawing.height)
    return img

def save_svg(drawing: Canvas, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(drawing.draw())
def save_frame(drawing: Canvas, filename: str) -> None:
    make_frame(drawing).save(filename=f"{filename}")
def print_frame(drawing: Canvas) -> None:
    make_frame(drawing).save(file=sys.stdout.buffer)