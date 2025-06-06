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
    # Without LazyAnimation, the second translation will begin where the first did
    # leading to a jump in the animation.
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0]),
        NoAnimation()
    )

text.set_text("With .lazy: Half Correct Sequencing")

with scene as s:
    circle = Circle(20)
    s << circle
    # With .lazy, the second translation's starting point is where the previous left off.
    # This is correct, but the destination is still relative to the pre-animated circle.
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        TranslationAnimation.lazy(circle.transform, circle.transform.translation + [100, 0, 0]),
        NoAnimation()
    )

text.set_text("With LazyAnimation: Correct Sequencing")
with scene as s:
    circle = Circle(20)
    s << circle
    # We can also use LazyAnimation, which will behave differently than .lazy
    # because all arguments, including the destination, are evaluated lazily.
    # This will lead to the intended sequence: down and then to the right.
    s.animations << AnimationSequence(
        TranslationAnimation(circle.transform, circle.transform.translation + [0, 75, 0]),
        LazyAnimation(lambda:TranslationAnimation(circle.transform, circle.transform.translation + [100, 0, 0])),
        NoAnimation()
    )