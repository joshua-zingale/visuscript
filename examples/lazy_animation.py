"""
LazyAnimation allows the initialization of an Animation to be delayed until its first advance.
This helps in cases where two animations are sequenced in a way that the initialization arguments
for the second animation depend on the final state resultant from the first animation.

This example shows the difference between sequencing animations with and without LazyAnimation.
The goal is to move the circle first down and then to the right.
"""
from visuscript import *

scene = Scene()
text = Text("Without LazyAnimation: Incorrect Sequencing").set_anchor(Anchor.TOP_LEFT).translate(*scene.xy(0.02,0.02))
scene << text
with scene as s:
    circle = Circle(20)
    s << circle
    # Without LazyAnimation, the second translation's target is relative to the initial circle's transform,
    # not the transform after the first translation.
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0]),
        NoAnimation()
    )

text.set_text("With LazyAnimation: Correct Sequencing")

with scene as s:
    circle = Circle(20)
    s << circle
    # With LazyAnimation, the second translation's target is relative to the circle's transform
    # AFTER the first translation completes.
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        LazyAnimation(lambda:TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0])),
        NoAnimation()
    )