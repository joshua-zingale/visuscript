from visuscript.canvas import Canvas
from visuscript.drawable import *
from visuscript.text import *
from visuscript.organizer import Grid
canvas = Canvas()
# print(canvas.xy(0,.5))

phi = 1.618

with canvas as c:
    c << Drawing(path=Path().M(*canvas.xy(0,.20)).l(canvas.width/2, -10).l(canvas.width/2, 10), stroke="red", stroke_width=3)
    c << Drawing(path=Path().M(*canvas.xy(0,.80)).l(canvas.width/2, 10).l(canvas.width/2, -10), stroke="red", stroke_width=3)
    c << Text(text="Object-level Scene Deocclusion", font_size=30).set_transform([0,-10]).add_child(
        Text(text="Work by Zhengzhe Liu et al.", font_size=15).set_transform([0,25]).add_child(
            Text(text="SIGGRAPH '24", font_size=15).set_transform([0,20]).add_child(
                Text(text="Presentation by Joshua Zingale", font_size=10).set_transform([0,15])
                )
        )
    )

canvas << Text(text="Work by Zhengzhe Liu et al.", font_size=4).set_transform(canvas.xy(0.025, 0.975)).set_anchor(Drawable.LEFT)
canvas << Text(text="Presentation by Joshua Zingale", font_size=4).set_transform(canvas.xy(0.975, 0.975)).set_anchor(Drawable.RIGHT)


def heading(text: str):
    return Text(text=text, font_size=30, anchor=Drawable.LEFT).set_transform(canvas.xy(0.025, 0.10)).add_child(
        Drawing(path=Path().M(0, 25).l(canvas.width/phi, 0), stroke="red", stroke_width=2))

bullet_grid = Grid((10,1),(18,18), canvas.xy(0.075, 0.30))

def bullet(text: str, num: int = 0, font_size=15):
    global bullet_grid
    return Circle(2).add_child(
        Text(text=text, font_size=font_size, anchor=Drawable.LEFT).set_transform([6, 0])
    ).set_transform(bullet_grid[num])

def bullets(*args: Tuple[str, ...], font_size=15):
    return [bullet(arg, i, font_size=font_size) for i, arg in enumerate(args)]


with canvas as c:
    c << heading("Scene Deocclusion")

    c << Image(filename="deocclusion-images/figure1.png").set_transform(Transform(scale=0.175))


with canvas as c:
    c << heading("Why Not Use Standard Inpainting?")

    c << bullets(
        "The following image demonstrates attempted infilling via stable diffusion (SD).",
        "In the first (b), SD fails to deocclude and completes the occluder instead of the occludee.",
        "In the second (b), SD adds a non-existent object, a teddy bear, instead of revealing the occludee.",
        font_size=10
    )

    c << Image(filename="deocclusion-images/figure2.png").set_transform(Transform([0,60],scale=0.18))

with canvas as c:
    c << heading("Architecture Overview")

    c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))


with canvas as c:
    c << heading("Diffusion Models")

    c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))