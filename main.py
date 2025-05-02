#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *

class AnimatedList(list):
    pass


for i in range(0, 24*5, 1):
    canvas = Canvas(width=640, height=360).with_children([
        Circle(radius=4, color=Color(opacity=0.0), outline=Color('blue'), outline_thickness=15).with_children([
            Text(text="-----", font_size=3, anchor=Drawing.CENTER)
        ]),
        Rect(width=200, height=400, transform=Transform(translation=[200,100])),
    ]).zoom(Transform(translation=[0,0], scale=1+ (i/24*5)))


    print_frame(canvas)
