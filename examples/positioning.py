from visuscript import *
from visuscript.config import config
from visuscript.animation import sin_easing
import sys
config.canvas_color = "off_white"
config.drawing_stroke = "dark_slate"
config.text_fill = "dark_slate"

with Scene().set_anchor(Anchor.CENTER) as c:
    c << (r:=Rect(50,50, anchor=Anchor.CENTER)).translate(50,50)

    c << (less_than := Text(f"<", font_size=30, anchor=Anchor.RIGHT)
                    .add_child(question_mark := Text("?", font_size=30).set_anchor(Anchor.BOTTOM)))
     
    question_mark.translate(*less_than.shape.top)

    c.set_transform(Transform(translation=r.transform.translation,rotation=0, scale=1))

    c.animations << RotationAnimation(c.transform, 360)
    c.animations << RotationAnimation(r.transform, 360)
    c.animations << ScaleAnimation(c.transform, 2, easing_function=lambda a: sin_easing(3*a))