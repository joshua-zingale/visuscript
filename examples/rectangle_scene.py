from visuscript import *
with Scene() as s:
    rect = Rect(20,20)
    s << rect
    s.animations << TransformAnimation(
        rect.transform,
        Transform(
            translation=[40,20],
            scale=2,
            rotation=45))