from visuscript import *
from visuscript.config import config
from copy import deepcopy
config.canvas_color='off_white'
config.drawing_stroke='dark_slate'
config.drawing_stroke_width = 2

with Canvas() as c:

    c << (circ := Circle(radius=20).add_children(
        Rect(5,5),
        Drawing(path=Path().M(-40,5).Q(0,80,40,5))
    )).rotate(180)


    c << (circ2 := deepcopy(circ).translate(100))
    
    c << Drawing(path=Path().Q(10,30,20,0),anchor=Anchor.CENTER).translate(
        ((circ2.transform + circ.transform)/2).translation.x, 50
    )