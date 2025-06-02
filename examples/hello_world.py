from visuscript import *
with Scene() as s:
    text = Text("Hello, World!")
    s << text
    s.animations << AnimationSequence(
        RgbAnimation(text.fill, 'red'),
        RgbAnimation(text.fill, 'white'),
        RgbAnimation(text.fill, 'blue'),
        )

    s.animations << TransformAnimation(text.transform, Transform(
        translation=[100,-30],
        rotation=360,
        scale=2,
    ))