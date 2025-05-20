from visuscript import *
from random import choice
with Canvas() as c:
    grid = Grid((15,10), sizes=(10,10), offset=[-50,-50])
    for transform in grid:
        c << Rect(width=10,height=10, fill=choice(['red', 'blue', 'green'])).set_transform(transform)
    c <<  Image(filename=[
        [[255,0,0], [0,255,0]],
        [[0,255,0], [0,0,255]],
        ],
        width=50).set_transform([100,0])
    
    c <<  Image(filename="deocclusion-presentation/deocclusion-images/tractor.png", width=150)

   