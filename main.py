#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawable import *
from visuscript.output import *
from visuscript.canvas import Canvas
from visuscript.text import Text
from visuscript.animation import *
from visuscript.scene import Scene

s = Scene(width=480, height=270)



rect = Rect(width=100, height=100, transform=s.xy(0,0)).with_children([
    Circle(50),
    Rect(width=50,height=50, transform=[0, 75]).with_child(
        Rect(width=25, height=25, transform=Transform(rotation=45))
    )
])

s << rect
s << (rect2 := Rect(width=50, height=20, transform=[100, 50]))

s.animations << TransformInterpolation(rect, Transform(translation=s.xy(0.5,0.5), scale=0.25, rotation=135), fps = 24, duration = 3)
s.animations << TransformInterpolation(rect2, Transform(translation=s.xy(0.5,0.5), scale=0.25, rotation=135), fps = 24, duration = 1.5)

s.animations << ScaleAnimation(s, 3, fps = 24, duration=3)


for frame in s.run():
    print_frame(frame)

s.animations << ScaleAnimation(s, 0.5, fps = 24, duration=1)

for frame in s.run():
    print_frame(frame)

# s.animations << PathAnimation(s, Path().M(*s.transform.xy).l(-200,0), fps = 24, duration=3)

# for frame in s.run():
#     print_frame(frame)

# s.animations << TransformInterpolation(s, Transform([-100,100], scale = 4), fps = 24, duration=3)

# for frame in s.run():
#     print_frame(frame)

