#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawable import *
from visuscript.output import *
from visuscript.canvas import Canvas
from visuscript.text import Text
from visuscript.animation import *
from visuscript.scene import Scene

s = Scene(width=480, height=270)


s << (rect := Rect(width=50, height=50, anchor=Drawing.CENTER).add_child(c := Circle(5, anchor=Drawing.CENTER)))



s.animations << AnimationBundle(
    PathAnimation(rect, path=Path().Q(55,-30,115,0)),
    NoAnimation(fps=30, duration=1),
    AnimationBundle([ScaleAnimation(rect, 3)]),
    RotationAnimation(rect, 45)
    )

s.pf()

# s.animations << PathAnimation(s, Path().M(*s.transform.xy).l(-200,0), fps = 24, duration=3)

# for frame in s.run():
#     print_frame(frame)

# s.animations << TransformInterpolation(s, Transform([-100,100], scale = 4), fps = 24, duration=3)

# for frame in s.run():
#     print_frame(frame)

