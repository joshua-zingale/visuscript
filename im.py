#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *

# print(Rect(width=200, height=200, fill='blue'))

rect = Rect(width=20, height=20, transform=Transform(translation=[32, 16]))

circ = Rect(width=5, height=5, transform=Transform(rect.point(20)))

canvas = Canvas(logical_width=64, logical_height=36, elements=[
    rect, circ
])

# print(circ)


# print(Circle(radius=3, stroke_width = 0.2).get_shape()._segments[-1].end)
# print(canvas.draw())
# print(canvas.transform)
print_frame(canvas) # This sends a png file to stdout, to be used by ffmpeg
