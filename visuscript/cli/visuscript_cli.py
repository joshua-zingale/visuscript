"""
This is the core Visuscript CLI utility, which creates a movie from a Python script.
See :class:`~visuscript.canvas.Scene` for writing such a script.

Technically, this utility could create a movie from any Python script that outputs a stream of SVG elements
to :attr:`visuscript.config.config.canvas_output_stream`;
however, this is automatically done by :class:`~visuscript.canvas.Scene`.
"""

from argparse import ArgumentParser
import subprocess
import importlib.util
import sys
import os

from visuscript.config import config
from visuscript.primatives import Color

MODES = ["video", "slideshow"]
THEME = ["dark", "light"]

def main():

    parser = ArgumentParser(__doc__)

    parser.add_argument("input_script",type=str, help="Python script that prints a stream of SVG elements to standard output.")
    parser.add_argument("--output", default="output.mp4", type=str,help="Filename at which the output video will be stored.")
    parser.add_argument("--width", default=1920, type=int,help="Width in pixels of the output video.")
    parser.add_argument("--height", default=1080, type=int,help="Height in pixels of the output video.")
    parser.add_argument("--logical_width", default=480, type=int,help="Logical width of the output video.")
    parser.add_argument("--logical_height", default=270, type=int,help="Logical height of the output video.")
    parser.add_argument("--downscale", default=1, type=int,help="Both the output-video's dimensions are scaled down by this factor.")
    parser.add_argument("--fps", default=30, type=int,help="Frames Per Second of the output video file.")
    parser.add_argument("--mode", default="video", choices=MODES)
    parser.add_argument("--theme", default="dark", choices=THEME)


    args = parser.parse_args()
    
    input_filename: str = args.input_script
    output_filename: str = args.output

    width: int = int(args.width / args.downscale)
    height: int = int(args.height / args.downscale)
    logical_width: int = args.logical_width
    logical_height: int = args.logical_height

    fps: int = args.fps

    mode: str = args.mode
    theme: str = args.theme

    if not os.path.exists(input_filename):
        print(f"visuscript error: File \"{input_filename}\" does not exists.", file=sys.stderr)
        exit()


    dir_path = os.path.dirname(os.path.realpath(__file__))
    if mode == "video":
        animate_proc = subprocess.Popen(
            [f"{dir_path}{os.sep}scripts{os.sep}visuscript-animate", f"{fps}", f"{output_filename}"],
            stdin=subprocess.PIPE,
            text=True
        )
    elif mode == "slideshow":
        animate_proc = subprocess.Popen(
            [f"{dir_path}{os.sep}scripts{os.sep}visuscript-slideshow", f"{output_filename}"],
            stdin=subprocess.PIPE,
            text=True
        )

    if theme == "dark":
        config.canvas_color = Color("dark_slate", 1.0)
        config.text_fill = Color("off_white", 1)
        config.element_fill = Color("off_white", 0.0)
        config.element_stroke = Color("off_white", 1)
    elif theme == "light":
        config.canvas_color = Color("off_white", 1.0)
        config.text_fill = Color("dark_slate", 1)
        config.element_fill = Color("dark_slate", 0.0)
        config.element_stroke = Color("dark_slate", 1)


    config.canvas_width = width
    config.canvas_height = height
    config.canvas_logical_width = logical_width
    config.canvas_logical_height = logical_height

    config.fps = fps

    config.canvas_output_stream = animate_proc.stdin
    
    try:
        spec = importlib.util.spec_from_file_location("script", input_filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        if hasattr(mod, "main"):
            mod.main()
    finally:
        animate_proc.stdin.flush()
        animate_proc.stdin.close()
        animate_proc.wait()

    if animate_proc.returncode == 0:
        print(f"Successfully created \"{output_filename}\"")
    else:
        print(f"visuscript error: There was at least one problem with attempting to create \"{output_filename}\"", file=sys.stderr)
    


if __name__ == "__main__":
    main()
