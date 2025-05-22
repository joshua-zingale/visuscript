from visuscript import *
from visuscript.element import Element
import numpy as np
from typing import Tuple
from copy import deepcopy
import sys
from visuscript.primatives import Vec2
from PIL import Image as PILImage
canvas = Canvas()
# print(canvas.xy(0,.5))

phi = 1.618

def heading(text: str):
    return Text(text=text, font_size=30, anchor=Anchor.LEFT).set_transform(canvas.xy(0.025, 0.10)).add_child(
        Drawing(path=Path().M(0, 25).l(canvas.width/phi, 0), stroke="red", stroke_width=2))

bullet_grid = GridOrganizer((10,1),(18,18), canvas.xy(0.075, 0.30))

def bullet(text: str, num: int = 0, font_size=15):
    global bullet_grid
    return Circle(2, anchor=Anchor.CENTER).add_child(
        Text(text=text, font_size=font_size, anchor=Anchor.LEFT).set_transform([6, -1])
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

canvas << Text(text="Work by Zhengzhe Liu et al.", font_size=4).set_transform(canvas.xy(0.025, 0.975)).set_anchor(Anchor.LEFT)
canvas << Text(text="Presentation by Joshua Zingale", font_size=4).set_transform(canvas.xy(0.975, 0.975)).set_anchor(Anchor.RIGHT)


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

    c << (t := Text(text="New Training Data", font_size = 10, transform=[-60,0], anchor=Anchor.RIGHT))
    c << (t2 := Text(text="Fine-Tuned Model for Deocclusion", font_size = 10, transform=[60,0], anchor=Anchor.LEFT))

    c << arrow(t, r)
    c << arrow(r, t2)

with canvas as c:

    c << heading("Diffusion")

    with PILImage.open("deocclusion-images/flower.jpg") as im:
        image = np.array(im)
        image = image[:,:,:3]

    pollute = lambda im: abs(im + np.random.randn(*im.shape)*100)

    flower = Image(filename=image).set_transform(Transform(translation=[-150,-15],scale=0.1))
    flower_1 = Image(filename=pollute(image)).set_transform(Transform(translation=[-50,-15],scale=0.1))
    flower_2 = Image(filename=pollute(pollute(image))).set_transform(Transform(translation=[50,-15],scale=0.1))
    flower_3 = Image(filename=pollute(pollute(pollute(pollute(pollute(image)))))).set_transform(Transform(translation=[150,-15],scale=0.1))

    flower4 = deepcopy(flower_3).set_transform(Transform(translation=[150,40],scale=0.1))
    flower5 = deepcopy(flower_2).set_transform(Transform(translation=[50,40],scale=0.1))
    flower6 = deepcopy(flower_1).set_transform(Transform(translation=[-50,40],scale=0.1))
    flower7 = deepcopy(flower).set_transform(Transform(translation=[-150,40],scale=0.1))

    c << flower
    c << flower_1
    c << flower_2
    c << flower_3
    c << [flower4, flower5, flower6, flower7]

    c << Text(text="forward", font_size=5, anchor=Anchor.RIGHT).set_transform(flower.shape.left + [-5,0])

    c << Text(text="backward", font_size=5, anchor=Anchor.LEFT).set_transform(flower4.shape.right + [5,0])

    c << [
        arrow(flower, flower_1),
        arrow(flower_1, flower_2),
        arrow(flower_2, flower_3),
        arrow(flower4, flower5),
        arrow(flower5, flower6),
        arrow(flower6, flower7)
    ]

with canvas as c:
    c << heading("Latent Diffusion")

    with PILImage.open("deocclusion-images/flower.jpg") as im:
        image = np.array(im)
        image = image[:,:,:3]


    def max_pool(im: np.ndarray, n=16):
        out = np.zeros(((im.shape[0] + 1 - n)//n, (im.shape[1] + 1 - n)//n, im.shape[2]))

        for i in range(out.shape[0]):
            for j in range(out.shape[1]):
                for k in range(out.shape[2]):
                    out[i][j][k] = im[i*n:i*n+n, j*n:j*n+n, k].flatten().max()

        return out

    pollute = lambda im: abs(im + np.random.randn(*im.shape)*35)


    flower = Image(filename=image).set_transform(Transform(translation=[-175,0],scale=0.15))

    pooled_image = max_pool(image)

    pflower = Image(filename=pooled_image).set_transform(Transform(translation=[-100,0],scale=0.15*4))
    pflower1 =Image(filename=pollute(pooled_image)).set_transform(Transform(translation=[-66,0],scale=0.15*4))
    pflower2 =Image(filename=pollute(pollute(pooled_image))).set_transform(Transform(translation=[-33,0],scale=0.15*4))
    pflower3 =Image(filename=pollute(pollute(pollute(pollute(pooled_image))))).set_transform(Transform(translation=[0,0],scale=0.15*4))

    dflower = deepcopy(flower).set_transform(Transform(translation=[175,0],scale=0.15))
    dpflower = deepcopy(pflower).set_transform(Transform(translation=[100,0],scale=0.15*4))
    dpflower1 = deepcopy(pflower1).set_transform(Transform(translation=[66,0],scale=0.15*4))
    dpflower2 = deepcopy(pflower2).set_transform(Transform(translation=[33,0],scale=0.15*4))

    c << Drawing(path=Path().M(*(pflower.shape.top_left + [3,-5])).l(*(pflower3.shape.center - pflower.shape.left - [6,0])), fill='pale_green')
    c << Drawing(path=Path().M(*(pflower3.shape.bottom + [3,5])).l(*(dpflower.shape.right - pflower3.shape.center - [6,0])), fill='blue')

    c << [
        flower,
        pflower,
        pflower1,
        pflower2,
        pflower3,
        line_with_head(flower.shape.top_right, pflower.shape.top_left, head_size=0),
        line_with_head(flower.shape.bottom_right, pflower.shape.bottom_left, head_size=0),
        arrow(pflower, pflower1),
        arrow(pflower1, pflower2),
        arrow(pflower2, pflower3),
        dflower,
        dpflower,
        dpflower1,
        dpflower2,
        line_with_head(dflower.shape.top_left, dpflower.shape.top_right, head_size=0),
        line_with_head(dflower.shape.bottom_left, dpflower.shape.bottom_right, head_size=0),
        arrow(pflower3, dpflower2),
        arrow(dpflower2, dpflower1),
        arrow(dpflower1, dpflower),
    ]





with canvas as c:
    c << heading("Latent Diffusion")
    c << Image(filename='deocclusion-images/latent-diffusion.png').set_transform(Transform(translation=[0,-10],scale=0.125))
    c << Image(filename='deocclusion-images/latent-diffusion-loss.png').set_transform(Transform(translation=[0,80],scale=0.3))

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
    c << Image(filename=('deocclusion-images/lr.png'), anchor=Anchor.LEFT).set_transform(Transform(translation=[0,(1-4)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/lp.png'), anchor=Anchor.LEFT).set_transform(Transform(translation=[0,(1-3)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/lm.png'), anchor=Anchor.LEFT).set_transform(Transform(translation=[0,(1-1)*18], scale=0.25))
    c << Image(filename=('deocclusion-images/l.png'), anchor=Anchor.LEFT).set_transform(Transform(translation=[0,(1-0)*18], scale=0.25))


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
        "E_2c is initialized with E_1.",
        "Each Z_i convolution is initialized to a zero convolution.",
        "Train decoder to recover full-view latent space with partial-view and prompt.",
        font_size=10
        )

    c << Image(filename=('deocclusion-images/figure4.png')).set_transform(Transform(translation=[0,38], scale=0.18))

    c << Image(filename=('deocclusion-images/loss-stage-2.png')).set_transform(Transform(translation=[0,105], scale=0.2))


with canvas as c:
    c << heading("Inference")

    c << bullets(
        "Segment input image using auxilary model, yielding each m_i.",
        "Classify each segment using GPT-4V.",
        "Get partial view latent encoding.",
        "Recover plausible full-view latent encoding.",
        "Decode output image(s) from recovered full-view latent encoding.",
        font_size=12
        )

    c << Image(filename=('deocclusion-images/inference-diagram.png')).set_transform(Transform(translation=[0,67.5], scale=0.215))

with canvas as c:
    c << heading("Layer-wise Deocclusion")

    c << Image(filename=('deocclusion-images/figure5.png')).set_transform(Transform(translation=[0,10], scale=0.18))

with canvas as c:
    c << heading("Results")
    c << Image(filename="deocclusion-images/figure6.png").set_transform(Transform(translation=[0,15],scale=0.2))

with canvas as c:
    c << heading("Results")
    c << Image(filename="deocclusion-images/figure7.png").set_transform(Transform(translation=[0,-30],scale=0.2))
    c << Image(filename="deocclusion-images/figure8.png").set_transform(Transform(translation=[0,45],scale=0.2))


with canvas as c:
    c << heading("Results")
    c << Image(filename="deocclusion-images/figure9.png").set_transform(Transform(translation=[0,-30],scale=0.2))
    c << Image(filename="deocclusion-images/figure10.png").set_transform(Transform(translation=[0,45],scale=0.2))

with canvas as c:
    c << heading("Results")
    c << Image(filename="deocclusion-images/figure13.png").set_transform(Transform(translation=[0,18],scale=0.125))

with canvas as c:
    c << heading("Results")
    c << Image(filename="deocclusion-images/figure14.png").set_transform(Transform(translation=[0,18],scale=0.125))
# with canvas as c:
#     c << heading("Architecture Overview")

#     c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))


# with canvas as c:
#     c << heading("Diffusion Models")

#     c << Image(filename="deocclusion-images/figure3.png").set_transform(Transform(scale=0.25))