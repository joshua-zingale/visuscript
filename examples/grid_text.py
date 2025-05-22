from visuscript import *
from random import choice
from visuscript.config import config

config.canvas_output = OutputFormat.SVG
config.canvas_color = 'off_white'
config.animation_duration = 1.5

with Scene() as c:
    c.set_transform(Transform([0,0], scale=1, rotation=0))
    grid = GridOrganizer((15,10), sizes=(10,10), offset=[-50,-50])
    for transform in grid:
        c << Rect(width=10,height=10, fill=choice(['red', 'blue', 'green'])).set_transform(transform)
    c <<  Image(filename=[
        [[255,0,0], [0,255,0]],
        [[0,255,0], [0,0,255]],
        ],
        width=50).set_transform([100,0])
    

    
    c <<  (im := Image(filename="deocclusion-presentation/deocclusion-images/figure4.png", width=150))

    c << (r := Rect(50,50, fill='red').translate(-100,-40))

    c.animations << ScaleAnimation(c, 1.2)
    c.animations << RotationAnimation(c, 360)
    c.animations << RotationAnimation(im, -360)
    c.animations << RotationAnimation(r, -360)
    # c.animations << TransformInterpolation(c, Transform(scale=2))