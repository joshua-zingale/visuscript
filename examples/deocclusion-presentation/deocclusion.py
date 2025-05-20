from visuscript import *
from visuscript.element import Element
import numpy as np
from typing import Tuple
import sys
from visuscript.primatives import Vec2
canvas = Canvas()
# print(canvas.xy(0,.5))

phi = 1.618

def heading(text: str):
    return Text(text=text, font_size=30, anchor=Drawable.LEFT).set_transform(canvas.xy(0.025, 0.10)).add_child(
        Drawing(path=Path().M(0, 25).l(canvas.width/phi, 0), stroke="red", stroke_width=2))

bullet_grid = Grid((10,1),(18,18), canvas.xy(0.075, 0.30))

def bullet(text: str, num: int = 0, font_size=15):
    global bullet_grid
    return Circle(2, anchor=Drawable.CENTER).add_child(
        Text(text=text, font_size=font_size, anchor=Drawable.LEFT).set_transform([6, -1])
    ).set_transform(bullet_grid[num])

def bullets(*args: Tuple[str, ...], font_size=15):
    return [bullet(arg, i, font_size=font_size) for i, arg in enumerate(args)]


def line_with_head(source: Vec2, destination: Vec2, stroke=None, stroke_width = 1, head_size = 2, fill=None):

    distance = np.linalg.norm(destination - source)
    direction = (destination - source) / distance
    
    ortho = Vec2(-direction.y, direction.x)

    line_end =source + direction*(distance-head_size)
    return Drawing(
        stroke=stroke,
        stroke_width=stroke_width,
        fill=fill,
        path=(
            Path()
            .M(*source)
            .L(*line_end)
            .L(*(line_end + ortho*head_size/2))
            .L(*(source + direction*distance))
            .L(*(line_end - ortho*head_size/2))
            .L(*line_end)
        ))


def arrow(source: Element, destination: Element, stroke=None, stroke_width = 1, head_size = 2, fill='off_white'):

    s_xy = source.shape.center
    d_xy = destination.shape.center

    direction = (d_xy - s_xy) / np.linalg.norm(d_xy - s_xy)

    start_xy = s_xy + direction * source.shape.circumscribed_radius
    end_xy = d_xy - direction * destination.shape.circumscribed_radius

    return line_with_head(start_xy, end_xy, stroke=stroke, stroke_width=stroke_width, head_size=head_size, fill=fill)



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
    c << heading("Overview")
    
    c << (r := Rect(width=80,height=30).add_child(
        Text(text="Stable Diffusion", font_size=10)
    ))

    c << (t := Text(text="New Training Data", font_size = 10, transform=[-60,0], anchor=Drawable.RIGHT))
    c << (t2 := Text(text="Fine-Tuned Model for Deocclusion", font_size = 10, transform=[60,0], anchor=Drawable.LEFT))

    c << arrow(t, r)
    c << arrow(r, t2)

with canvas as c:
    c << heading("Latent Diffusion Models")
    c << Image(filename='deocclusion-images/latent-diffusion.png').set_transform(Transform(translation=[0,15],scale=0.175))

with canvas as c:
    c << heading("Training Data")
    c << bullets(
        "85,000 objects from COCO dataset.",
        "Combine two to eight objects to form one image with occlusion."
    )

    c << (i1 := Image(filename="deocclusion-images/coco-dataset.png").set_transform(Transform(scale=0.075, translation=[-130,30])))
    c << (i2 := Image(filename="deocclusion-images/separate-objects.png").set_transform(Transform(scale=0.15, translation=[0,30])))
    c << (i3 := Image(filename="deocclusion-images/stacked-objects.png").set_transform(Transform(scale=0.225, translation=[120,30])))
    
    c << Text(text="Sample from COCO Dataset", font_size=5).set_transform(i1.shape.center + [0,i1.shape.height/2 + 7.5])
    c << Text(text="Objects Extracted from COCO", font_size=5).set_transform(i2.shape.center + [0,i2.shape.height/2 + 7.5])
    c << Text(text="COCO Objects Stacked into Single Image", font_size=5).set_transform(i3.shape.center + [0,i3.shape.height/2 + 7.5])

    c << [
        arrow(i1, i2),
        arrow(i2, i3)
    ]

with canvas as c:
    c << heading("Parallel Variational Autoencoder")

    c << bullets(
        "Use SD encoder to embed each object to latent space;",
        "Sum these embeddings to get a \"full-view\" latent space;",
        "Fine-tune the SD decoder to reconstruct a full object from a partial mask.",
        font_size=12
    )

    c << Image(filename="deocclusion-images/stage-one.png").set_transform(Transform(translation=[0,55],scale=0.15))

with canvas as c:
    c << heading("Decoder Cross Attention")

    c << bullets(
        "Fine-tune the SD decoder to reconstruct a full object from a partial mask.",
        "Before decoding via the SD decoder, cross attention gets a latent space for object i, f_i.",
        font_size=10
    )

    c << Image(filename="deocclusion-images/stage-1-cross-attention-diagram.png").set_transform(Transform(translation=[0,18],scale=0.15))
    c << Image(filename="deocclusion-images/stage-1-cross-attention.png").set_transform(Transform(translation=[0,78],scale=0.25))


with canvas as c:
    c << heading("Decoder Training Loss")

    c << bullets(
        "L_r is pixel similarity.",
        "L_p is for \"fidelity\".",
        "L_adv and L_kl are used for an adversarial loss.",
        "L_m is pixel-wise cross entropy for the mask.",
        "The total loss is a magic linear combination of these losses.",
        font_size=7
    )
    c << Image(filename=('deocclusion-images/lr.png'), anchor=Drawable.LEFT).set_transform(Transform(translation=[0,(1-4)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/lp.png'), anchor=Drawable.LEFT).set_transform(Transform(translation=[0,(1-3)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/lm.png'), anchor=Drawable.LEFT).set_transform(Transform(translation=[0,(1-1)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/l.png'), anchor=Drawable.LEFT).set_transform(Transform(translation=[0,(1-0)*18], scale=0.25))


with canvas as c:
    c << heading("Visible-to-Complete Latent Space")

    c << bullets(
        "Take as input a composite image.",
        "Encode the partial views into latent space f_p.",
        "Train decoder to recover full-view latent space with partial-view and prompt.",
        font_size=12
        )

    c << Image(filename=('deocclusion-images/stage-2.png')).set_transform(Transform(translation=[0,35], scale=0.18))

with canvas as c:
    c << heading("Close Up: Partial-to-Full View")

    c << bullets(
        "E_2 is initialized with E_1",
        "Each Z_i convolution is initialized to a zero convolution.",
        "Train decoder to recover full-view latent space with partial-view and prompt.",
        font_size=12
        )

    c << Image(filename=('deocclusion-images/figure4.png')).set_transform(Transform(translation=[0,45], scale=0.18))

# with canvas as c:
#     c << heading("Architecture Overview")

#     c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))


# with canvas as c:
#     c << heading("Diffusion Models")

#     c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))