from visuscript import *
with Scene() as s:
    rect = Rect(20,20).add_child(Rect(5,5).translate(y=20, z=-1))
    s << rect
    s.animations << AnimationSequence(
        AnimationBundle(
            TranslationAnimation(rect.transform, [-30,-60]),
            ScaleAnimation(rect.transform, 2),
            RotationAnimation(rect.transform, 135)
        ),
        TransformAnimation.lazy(rect.transform, Transform([0,0], 1, 0)),
        )
    s.animations << RgbAnimation(rect.stroke, Rgb(255,0,0))
    s.animations << RgbAnimation(rect.fill, "yellow")
    s.animations << OpacityAnimation(rect.fill, 1)
    s.animations << OpacityAnimation(rect, 0.5)

    