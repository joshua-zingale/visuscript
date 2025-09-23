"""
:class:`~visuscript.lazy_object.LazyObject`` allows the initialization of
an Animation's constructor argument to be delayed until its first advance.
This helps in cases where two animations are sequenced in a way that the initialization arguments
for the second animation depend on the final state resultant from the first animation.

Objects like :class:`Transform` and :class:`Color` can have their attributes lazily accessed with `.lazy`.
For example, `Transform.lazy.translation` or `Color.lazy.rgb`.

This example shows the difference between sequencing animations with and without `.lazy`.
"""

from visuscript import *
from visuscript.drawable.code import get_all_code_blocks, PythonText

code_blocks = get_all_code_blocks(__file__)
scene = Scene()
text = (
    Text("Without any lazy arguments.")
    .set_anchor(Anchor.TOP_LEFT)
    .translate(scene.xy(0.02, 0.02))
)
scene << text
##1
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << sequence(
        animate_translation(circle.transform, circle.transform.translation + [0, 75]),
        animate_translation(circle.transform, circle.transform.translation + [100, 0]),
        wait(3),
    )
    s << PythonText(code_blocks[1], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(
        *s.ushape.top_left + [10, 22.5]
    )
##


text.set_text("With a lazy argument.")
##2
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << sequence(
        animate_translation(circle.transform, circle.transform.translation + [0, 75]),
        animate_translation(
            circle.transform, circle.transform.lazy.translation + [100, 0]
        ),
        wait(3),
    )
    s << PythonText(code_blocks[2], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(
        *s.ushape.top_left + [10, 22.5]
    )
##