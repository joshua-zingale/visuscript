from visuscript import *
s = Scene()
rect = Rect(20,20)
s << rect
s.player << AnimationBundle(
    TranslationAnimation(rect.transform, [-30,-60]),
    RotationAnimation(rect.transform, 135)
    )