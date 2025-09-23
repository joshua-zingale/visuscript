from visuscript import *

with Scene() as s:
    text = Text("Hello, World!")
    s << text
    s.animations << sequence(
        animate_rgb(text.fill, "red", "white", "blue", duration=3, easing_function=easing.linear_easing),
    )

    s.animations << animate_transform(
        text.transform,
        Transform(
            translation=[100, -30],
            rotation=360,
            scale=2,
        ),
        duration=3,
    )
