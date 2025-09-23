from visuscript import *

s = Scene()
rect = Rect(20, 20).translate(100).set_fill("green")
s << rect
s.player << bundle(
    sequence(
        bundle(
            animate_translation(rect.transform, [-30, -60]),
            animate_scale(rect.transform, [2,3])),
        animate_rotation(rect.transform, 135),
        animate_scale(rect.transform, 4)),
    animate_rgb(rect.stroke, Rgb(201,13,100)),
    animate_rgb(rect.fill, "blue"),
    animate_opacity(rect.fill, 0.0, duration=4))