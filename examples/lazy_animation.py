"""
.lazy and :class:`LazyAnimation` allow the initialization of an Animation to be delayed until its first advance.
This helps in cases where two animations are sequenced in a way that the initialization arguments
for the second animation depend on the final state resultant from the first animation.

This example shows the difference between sequencing animations with and without .lazy and LazyAnimation.
The goal is to move the circle first down and then to the right.
"""
from visuscript import *
from visuscript.animation import LazyAnimation
from visuscript.code import get_all_code_blocks, PythonText
code_blocks = get_all_code_blocks(__file__)
scene = Scene()
text = Text("Without LazyAnimation: Incorrect Sequencing").set_anchor(Anchor.TOP_LEFT).translate(*scene.xy(0.02,0.02))
scene << text
##1
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0]),
        NoAnimation()
    )
    s << PythonText(code_blocks[1], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(*s.shape.top_left + [10,22.5])
##

text.set_text("With .lazy: Half Correct Sequencing")
##2
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation.lazy(circle.transform, circle.transform.translation + [100, 0, 0]),
        NoAnimation()
    )
    s << PythonText(code_blocks[2], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(*s.shape.top_left + [10,22.5])
##

text.set_text("With .lazy & lazy argument: Correct Sequencing")
##3
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation.lazy(circle.transform, circle.transform.lazy.translation.add([100, 0, 0])),
        NoAnimation()
    )
    s << PythonText(code_blocks[3], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(*s.shape.top_left + [10,22.5])
##

text.set_text("With LazyAnimation: Correct Sequencing")
##4
with scene as s:
    circle = Circle(20)
    s << circle
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        LazyAnimation(lambda:TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0])),
        NoAnimation()
    )
    s << PythonText(code_blocks[4], font_size=6).set_anchor(Anchor.TOP_LEFT).translate(*s.shape.top_left + [10,22.5])
##