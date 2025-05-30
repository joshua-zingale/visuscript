from wand.image import Image
from visuscript.drawable import Drawable
from io import BytesIO
import sys

#TODO These functions should actually take a "Canvas", but they are used thereby. Consider moving into one file.
def get_image(canvas: Drawable) -> Image:
    img_bytes = BytesIO(canvas.draw().encode('utf-8'))
    img = Image(blob=img_bytes, format='svg')
    img.format = 'png'
    img.resize(canvas.width * canvas.logical_scaling, canvas.height * canvas.logical_scaling)
    return img

def print_png(canvas: Drawable, file = None) -> None:
    """
    Prints `canvas` to the standard output as a png blob.
    """
    print(get_image(canvas).make_blob(), file=file, end='')

def save_png(canvas: Drawable, filename: str) -> None:
    get_image(canvas).save(filename=f"{filename}")

def print_svg(canvas: Drawable, file = None) -> None:
    """
    Prints `canvas` to the standard output as an SVG file.
    """
    print(canvas.draw(), file=file)

def save_svg(canvas: Drawable, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(canvas.draw())