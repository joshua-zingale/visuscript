"""An example that demonstrates Updaters."""

from visuscript import *
from visuscript.animation import linear_easing
with Scene() as s:

    circle = Circle(20).add_child(Rect(10,10).set_fill('green').set_stroke('green')).set_stroke("blue")
    rectangle = Rect(40,40).translate(*s.shape.bottom_left + [20, -40]).set_stroke("red").add_child(
        Text("E")
    )

    crosshair = Drawing(Path().M(0, -5).L(0,5).M(-5,0).L(5,0)).set_anchor(Anchor.CENTER).set_opacity(0.5)


    for color, (xp, yp) in zip(['red','blue','green','yellow'], [(.25, .25), (.25, .75), (.75,.25),(.75,.75)]):
        s << Rect(10,10).translate(*s.xy(xp, yp)).set_fill(color)

    s << [rectangle, circle, crosshair]

    s.updaters << TranslationUpdater(rectangle.transform, circle.transform, max_speed=300, acceleration=200)
    s.updaters << TranslationUpdater(s.transform, circle.transform, acceleration=500)
    s.updaters << TranslationUpdater(crosshair.transform, s.transform)


    s.animations << AnimationSequence(
        PathAnimation(circle.transform, Path()
                        .M(*circle.shape.center)
                        .Q(*(s.shape.center + s.shape.right)/2 + UP*80, *s.shape.right)
                        .Q(*s.shape.center + DOWN*80, *s.shape.left)
                        .L(*s.shape.top_left)
                        .l(120,0)
                        .l(150,80)
                        .L(*s.shape.bottom_right)
                        .Q(*(s.shape.bottom_right + s.shape.center)/2 + UP*50 + RIGHT*50, *s.shape.center),
                        duration=7, easing_function=linear_easing),
        NoAnimation()
        )