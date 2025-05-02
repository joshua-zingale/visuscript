#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *

# print(Rect(width=200, height=200, fill='blue'))

canvas = Canvas(elements=[
    Rect(width=20, height=20, transform=Transform(translation=[32, 16])).with_children(Rect(width=5,height=5))
])


# print(canvas.draw())
# print(canvas.transform)
print_frame(canvas) # This sends a png file to stdout, to be used by ffmpeg
