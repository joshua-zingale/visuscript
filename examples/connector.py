from visuscript import *
from visuscript.drawable.connector import Arrow, LineTarget

s = Scene()
c1 = Circle(10).translate(y=50)
c2 = Circle(10).translate(100, 50)
l = Arrow(source=c1, destination=c2, source_target=LineTarget.CENTER)
s << (c1, c2, l)

s.player << animate_path(c2.transform, Path().M(*c2.gshape.center).Q(0, -100, -100, 0), duration=3)
