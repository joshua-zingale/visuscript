#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import *
from visuscript.canvas import Canvas
from visuscript.text import Text
class AnimatedList(list):
    pass

path = Path().L(10,10).L(0,10).L(64,20)

N = 24*3
for i in range(0, N, 1):
    c = Canvas(width=480, height=270)

    c.with_elements([
        Text(text="I love Cassidy, my wife and my love", font_size=20, transform=Transform(translation=c.p(0.5,0.5)), fill=Color('blue'),),
        rect := Rect(width=c.w(1/8), height=c.w(1/8), transform=c.p(7/8, 2/3)).with_child(Circle(c.w(1/16))),
        Rect(width=c.w(1/8), height=c.w(1/8), transform=c.p(7/8, 0), anchor=Drawable.TOP_LEFT),
        Drawing(path=Path().M(*rect.point_percentage(7/8)).L(*rect.point_percentage(2/8)), anchor=Drawing.TOP_LEFT, fill=Color(opacity=0.0), stroke=Color())
    ]).set_zoom((c.zoom*(N-i) + (i)*Transform(translation=rect.transform.translation, scale=2.0))/N)

    # canvas.draw()
    print_frame(c)
