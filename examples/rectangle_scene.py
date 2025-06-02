from visuscript import *
with Scene() as s:
    rect = Rect(20,20)
    s << rect
    s.animations << TranslationAnimation(rect.transform, [-30,-60])
    s.animations << RotationAnimation(rect.transform, 135)