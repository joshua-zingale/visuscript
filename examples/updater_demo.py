from visuscript import *
from visuscript.animation import linear_easing
with Scene() as s:

    circle = Circle(20)
    rectangle = Rect(40,40).translate(*s.shape.bottom_left + [20, -40])

    s << [circle, rectangle]

    s.updaters << TranslationUpdater(rectangle.transform, circle.transform, max_velocity=300, acceleration=200)
    s.animations << PathAnimation(circle.transform, Path()
                                  .M(*circle.shape.center)
                                  .Q(*(s.shape.center + s.shape.right)/2 + UP*80, *s.shape.right)
                                  .Q(*s.shape.center + DOWN*80, *s.shape.left)
                                  .L(*s.shape.top_left)
                                  .L(*s.shape.bottom_right)
                                  .Q(*(s.shape.bottom_right + s.shape.center)/2 + UP*30 + RIGHT*30, *s.shape.center),
                                  duration=7, easing_function=linear_easing)
    

    s.updaters << TranslationUpdater(s.transform, circle.transform, acceleration=500)