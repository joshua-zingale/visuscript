#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *


class Custom(Drawing):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.with_children([
            Rect(width=100,height=100, transform=Transform(translation=[200,200])).with_children([
            Circle(radius=25, color="red", transform=Transform(translation=[0,0,0])),
            Circle(radius=10, color="green", transform=Transform(translation=[0,0,0]))]
        )
        ])

        
canvas = Canvas(color="black", anchor=Drawing.CENTER).set_transform(Transform(translation=[1920/2,1080/2])).with_children([
    Circle(radius=200, transform=Transform(translation=[0,0])).with_children([
        Text(text="WiW", color="yellow", font_size=400, anchor=Drawing.CENTER)
    ])
    
])


# print(canvas.color.opacity)

# print(canvas._children[0].fill)

print_frame(canvas) # This sends a png file to stdout, to be used by ffmpeg
