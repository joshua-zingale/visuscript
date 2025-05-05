#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawable import *
from visuscript.output import *
from visuscript.canvas import Canvas
from visuscript.text import Text
class AnimatedList(list):
    pass

c = Canvas()

# c.with_elements([
#     Text(text="I love Cassidy, my wife and my love", font_size=c.a(0.03), transform=c.p(0.5,0.5), fill=Color('blue')),
#     rect := Rect(width=c.w(1/8), height=c.w(1/8), transform=c.p(7/8, 2/3)).with_child(Text(text="h", font_size=c.a(0.03))),
#     Drawing(path=Path().M(*rect.point_percentage(7/8)).L(*rect.point_percentage(3/8)), anchor=Drawing.TOP_LEFT, fill=Color(opacity=0.0), stroke=Color())
# ])

c.with_elements([
    Text(text="I love Cassidy, my wife and my love", font_size=c.h(0.03), transform=c.p(0.5,0.5), fill=Color('blue')),
    rect := Rect(width=c.w(1/8), height=c.w(1/8), transform=c.p(7/8, 2/3)),
    Drawing(path=Path().M(*rect.point_percentage(7/8)).L(*rect.point_percentage(2/8)), anchor=Drawing.TOP_LEFT, fill=Color(opacity=0.0), stroke=Color())
]).set_zoom((c.zoom*10 + 2*Transform(translation=rect.transform.translation, scale=1.0))/12)

# canvas.draw()
print_frame(c)
