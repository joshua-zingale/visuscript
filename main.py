#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawable import *
from visuscript.output import *
from visuscript.canvas import Canvas
from visuscript.text import Text
from visuscript.animation import *
class AnimatedList(list):
    pass

path = Path().L(10,10).L(0,10).L(64,20)

c = Canvas(width=480, height=270)
c.with_elements([
        rect1 := Rect(width=c.w(1/8), height=c.w(1/8)).with_child(Circle(c.w(1/16))),
        rect2 := Rect(width=c.w(1/8), height=c.w(1/8), transform=[60, 100]).with_child(Circle(c.w(1/16))),
        rect3 := Rect(width=c.w(1/8), height=c.w(1/8), transform=[200, 100]).with_child(circ3 := Circle(c.w(1/16)))
    ])

# print_frame(c)

animation1 = PathAnimation(rect1, Path().M(60,200).l(420,0), fps=24, duration=2)

animation2 = RotationAnimation(rect2, 135, fps=24, duration=2)

animation3 = ScaleAnimation(rect3, 2, fps=24, duration=2)

while animation1.advance() and animation2.advance() and animation3.advance():
    print_frame(c)
