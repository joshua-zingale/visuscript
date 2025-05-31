from visuscript.drawable import Drawable
#TODO These functions should actually take a "Canvas", but they are used thereby. Consider moving into one file.
def print_svg(canvas: Drawable, file = None) -> None:
    """
    Prints `canvas` to the standard output as an SVG file.
    """
    print(canvas.draw(), file=file)

def save_svg(canvas: Drawable, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(canvas.draw())