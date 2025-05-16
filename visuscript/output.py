from wand.image import Image
from visuscript.drawable import Drawable
from io import BytesIO
import sys


def get_image(drawable: Drawable) -> Image:
    img_bytes = BytesIO(drawable.draw().encode('utf-8'))
    img = Image(blob=img_bytes, format='svg')
    img.format = 'png'
    img.resize(drawable.width, drawable.height)
    return img

def print_png(drawable: Drawable) -> None:
    """
    Prints `drawable` to the standard output as a png blob.
    """
    sys.stdout.buffer.write(get_image(drawable).make_blob())

def save_png(drawable: Drawable, filename: str) -> None:
    get_image(drawable).save(filename=f"{filename}")

def print_svg(drawable: Drawable) -> None:
    """
    Prints `drawable` to the standard output as an SVG file.
    """
    print(drawable.draw())

def save_svg(drawable: Drawable, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(drawable.draw())