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

def save_frame(drawing: Canvas, frame: int) -> None:
    make_frame(drawing).save(filename=f"./frames/{frame}.png")
def print_frame(drawing: Canvas) -> None:
    make_frame(drawing).save(file=sys.stdout.buffer)