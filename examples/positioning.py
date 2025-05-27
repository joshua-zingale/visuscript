from visuscript import *


with Canvas() as c:
    c << (r:=Rect(50,50, anchor=Anchor.CENTER)).translate(50,50)

    c << (less_than := Text(f"<", font_size=30, anchor=Anchor.RIGHT)
                    .add_child(question_mark := Text("?", font_size=30).set_anchor(Anchor.BOTTOM)))
     
    question_mark.translate(*less_than.shape.top)

    c.set_transform(Transform(translation=r.transform.translation,))# rotation=45))
    print()