"""This example shows uses :class:`~visuscript.slideshow.Slideshow` to create a demonstration slideshow.

Compile this slideshow using `visuscript demo_slideshow.py --slideshow --output slideshow.mp4`.
To run the slideshow, use `vs_slideshow slideshow.mp4`
"""

from visuscript import *
from visuscript.slideshow import Slideshow, SlideTemplate


slideshow = Slideshow()
slideshow.templates["default"] = SlideTemplate().add_drawables(
    Text("Demo Slideshow").set_anchor(Anchor.TOP_LEFT).translate(-200, 120)
)

slideshow.templates["other"] = SlideTemplate().add_drawables(
    Text("This is another template").set_anchor(Anchor.TOP_LEFT).translate(-200, 120)
)

slide = slideshow.create_slide()

c = Circle(10)
slide << c
slide.animations << TranslationAnimation(c.transform, [100, 100], duration=2)


slide = slideshow.create_slide()
slide << c
slide.animations << TranslationAnimation(c.transform, [-100, -100])


slide = slideshow.create_slide("other")
slide << Text("Some Text for slide 3")

slide = slideshow.create_slide("other")
text = Text("Some Text for slide 4")
slide << text
slide.animations << RotationAnimation(text.transform, 360)


slideshow.export_slideshow()
