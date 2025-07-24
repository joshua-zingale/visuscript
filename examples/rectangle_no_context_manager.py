from visuscript import *

s = Scene()
rect = Rect(20, 20).translate(100)
s << rect
s.print()
s.player << AnimationBundle(
    TranslationAnimation(rect.transform, [-30, -60]),
    RotationAnimation(rect.transform, 135),
)
