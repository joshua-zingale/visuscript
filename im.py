#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *


class Custom(Drawing):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.with_children([
            Rect(width=100,height=100, transform=Transform(translation=[-600,200])).with_children([
            Circle(radius=25, transform=Transform(translation=[0,0,0])),
            Circle(radius=10, transform=Transform(translation=[0,0,0]))]
        )
        ])

        
canvas = Canvas(width=960, height=540).with_children([
    circle := Circle(radius=4, color=Color(opacity=0.0), outline=Color('blue'), outline_thickness=15).with_children([
        Text(text="-----", font_size=3, anchor=Drawing.CENTER)
    ]),
    # Rect(width=200, height=400, transform=Transform(translation=[200,100])),
    # Custom()
]).zoom(Transform(translation=[0,0], scale=3))


# print(canvas.color.opacity)

# print(canvas._children[0].fill)

# canvas.draw()

print_frame(canvas) # This sends a png file to stdout, to be used by ffmpeg
