#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *

class AnimatedList(list):
    pass

N = 24*5
for i in range(0, N, 1):
    rect = Rect(width=20, height=20, transform=Transform(translation=[32, 16]))

    circ = Rect(width=5,height=5, transform=Transform(translation=rect.point(i/N * rect.arc_length), rotation=i/N*360))

    canvas = Canvas(width=640, height=360, logical_width=64, logical_height=36, elements=[
        rect, circ
    ])


    print_frame(canvas)
