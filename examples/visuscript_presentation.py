"""An example presentation using Visuscript.

In addition to creating a video file, the **visuscript** utility has
a parameter for specifying that a PDF should be created instead.
This is done with the following command:

.. code-block:: bash

    visuscript visuscript_presentation.py visuscript_presentation.pdf --mode slideshow --output

To use this presentation effectively, you need a way to handle in embedded animations.
The slideshow mode of the visuscript utility outputs each frame of the video as one
page in the PDF document, leaving no built-in way to handle the animations.

What I have done is write up a simple script to listen to my keyboard inputs:
when I press return the script issues 30 next-pages over one second;
when I press delete the script issues 30 previous-pages over one second;
and if I hold either for some time before decompressing, the issues keep
coming until the end of the quantized second in which I decompressed the key.
Some PDF viewers are too slow for clicking through the pages thirty times a second.
I found that Google's Chrome browser is fast enough, so I use that.
Chrome does have a problem, however, in that there is some partial zoom and
translation applied when in present mode for some reason.
To account for this I simply counter-scale and -translate the Scene when
producing my slides for use in Google Chrome.
This is all very hacky right now but it works.
"""

from visuscript import *
from visuscript.animation import flash, fade_out
from visuscript.drawable.code import PythonText
from visuscript.drawable.connector import Arrow

with open(__file__, "r") as f:
    SELF_STRING = f.read()


import re

PAGINATION = 7
HEADING = 30
NORMAL = 10
BULLET = 12
MARGIN = 10


class Slideshow(Scene):
    def __init__(self):
        self._slide_count = 0
        super().__init__(print_initial=False)

    def print(self):
        self._slide_count += 1
        count = (
            Text(str(self._slide_count), font_size=PAGINATION)
            .translate(*self.ushape.bottom_right - [MARGIN, MARGIN])
            .set_anchor(Anchor.BOTTOM_RIGHT)
        )
        self.add_drawable(count)
        super().print()
        self.remove_drawable(count)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, *args, **kwargs):
        self.print()
        super().__exit__(*args, **kwargs)


scene = Slideshow()
scene.transform.set_translation([25, 0]).set_scale(
    1.125
)  # Hack for Google Chrome correction


def main():
    code_blocks = get_all_code_blocks()
    with scene as s:
        title = Text("Visuscript", font_size=HEADING).translate(*UP * 20)
        subtitle = (
            Text(
                "A Vector-Graphics-Based Animation Library for Python", font_size=NORMAL
            )
            .set_anchor(Anchor.TOP)
            .translate(*title.tshape.bottom + DOWN * 10)
        )
        attribution = (
            Text("by Joshua Zingale", font_size=NORMAL)
            .set_anchor(Anchor.TOP)
            .set_anchor(Anchor.TOP)
            .translate(*subtitle.tshape.bottom + DOWN * 10)
        )
        s << (title, subtitle, attribution)

        organizer = GridOrganizer((2, 2), (s.ushape.height / 2, s.ushape.width / 2))
        get_rect = (
            lambda: Rect(20, 20)
            .set_opacity(0.0)
            .add_children(
                Circle(5).translate(-10, -10),
                Circle(5).translate(10, -10),
                Circle(5).translate(-10, 10),
                Circle(5).translate(10, 10),
            )
        )

        rects: list[Rect] = []
        for transform in organizer:
            rects.append(get_rect())
            rects[-1].set_transform(
                Transform([-s.ushape.width / 4, -s.ushape.height / 4]) @ transform
            )

        s << rects

        for rect in rects:
            s.animations << [
                animate_opacity(rect, 1),
                animate_rotation(rect.transform, 360),
            ]

    bar = Drawing(
        Path()
        .M(
            *scene.ushape.top_left
            + DOWN * HEADING
            + DOWN * MARGIN
            + DOWN * 2
            + RIGHT * MARGIN
        )
        .l(scene.ushape.width / 3, 0)
    )
    scene << bar

    ##1
    with scene as s:
        s << heading("Features")
        s << bullets(
            "Create arbitrary 2D graphics with Drawing and Path.",
            "Create arbitrary animations through composition with bundle and sequence.",
            "Represent and animate datastructures with AnimatedCollection inheritors.",
            "Runtime checks for conflicting animations or updaters with PropertyLocker.",
            font_size=NORMAL,
        )
        s << (
            PythonText(code_blocks[1], font_size=9)
            .set_anchor(Anchor.BOTTOM_LEFT)
            .translate(*scene.ushape.bottom_left + [MARGIN, -MARGIN])
        )
    ##

    with scene as s:
        s << heading("API")

        def components(obj, *components):
            elements = [*components]
            scale_factor = obj.transform.scale[0] / 1.75
            for i, component in enumerate(components):
                component.scale(scale_factor).translate(
                    *obj.tshape.center
                    + Vec2((-130 + 130 * i) * scale_factor, 110 * scale_factor**0.25)
                    * scale_factor
                )
                elements.append(Arrow(source=component, destination=obj))
            return elements

        scene_node = (
            Circle(HEADING)
            .add_child(Text("Scene", font_size=NORMAL))
            .scale(1.5)
            .translate(0, -50)
        )
        drawable_node = Circle(HEADING).add_child(Text("Drawables", font_size=NORMAL))
        animation_node = Circle(HEADING).add_child(Text("Animations", font_size=NORMAL))
        updater_node = Circle(HEADING).add_child(Text("Updaters", font_size=NORMAL))
        s << scene_node
        s << components(scene_node, drawable_node, animation_node, updater_node)
        s << components(
            drawable_node,
            Circle(NORMAL)
            .add_child(Text("Circle", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("Rect", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("Arrow", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
        )
        s << components(
            animation_node,
            Circle(NORMAL)
            .add_child(Text("TransformAnimation", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("RgbAnimation", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("sequence", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
        )
        s << components(
            updater_node,
            Circle(NORMAL)
            .add_child(Text("TranslationUpdater", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("FunctionUpdater", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
            Circle(NORMAL)
            .add_child(Text("UpdaterBundle", font_size=NORMAL).rotate(-15))
            .set_stroke(Color("off_white", opacity=0)),
        )

    with scene as s:
        s << heading("Animation Pipeline")

        steps = [Text("Python"), Text("SVG"), Text("PNG"), Text("MP4")]
        converters = [Text("Visuscript"), Text("librsvg"), Text("ffmpeg")]

        separation = steps[0].ushape.width * 1.5

        GridOrganizer((1, 4), (1, separation)).set_transform(
            Transform([-separation * (len(steps) - 1) / 2, 0])
        ).organize(steps)

        for prev, curr, converter in zip(steps, steps[1:], converters):
            arrow = Arrow(source=prev, destination=curr)
            s << arrow
            s << converter.translate(*arrow.ushape.top + 10 * UP).set_anchor(
                Anchor.BOTTOM
            ).scale(0.5)
        s << steps

        s << Text(
            "> visuscript my_animation_script.py --output my_animation.mp4"
        ).translate(0, 25).scale(0.40)

    ##2
    # You can define an arbitrary ushape using an SVG Path
    drawing = (
        Drawing(Path().M(0, 10).L(20, 10).L(20, 20).Q(100, 10, 20, 0).L(20, 20))
        .set_anchor(Anchor.CENTER)
        .translate(120, -10)
        .scale(3)
        .rotate(-120)
        .set_stroke("red")
    )
    scene << drawing
    with scene as s:
        s << heading("Arbitrary 2D Shape")
        s << (
            PythonText(code_blocks[2], font_size=8)
            .set_anchor(Anchor.BOTTOM_LEFT)
            .translate(*scene.ushape.bottom_left + [MARGIN, -MARGIN])
        )
    ##

    ##3
    with scene as s:
        s << heading("Animation")
        s.animations << sequence(
            bundle(
                animate_rotation(drawing.transform, drawing.transform.rotation + 360),
                animate_scale(drawing.transform, 1),
            ),
            animate_path(
                drawing.transform,
                Path()
                .M(*drawing.tshape.center)
                .L(0, 0)
                .Q(100, 100, *s.ushape.right)
                .Q(0, -100, *s.ushape.left)
                .L(*drawing.ushape.center),
                duration=2,
            ),
            animate_scale(drawing.transform, 3),
            fade_out(drawing),
        )
        s << (
            PythonText(code_blocks[3], font_size=7.5)
            .set_anchor(Anchor.BOTTOM_LEFT)
            .translate(*scene.ushape.bottom_left + [MARGIN, -MARGIN])
        )
    ##

    ##4
    with scene as s:


        s << heading("Updaters")
        circle = (
            Circle(20)
            .add_child(Rect(10, 10).set_fill("green").set_stroke("green"))
            .set_stroke("blue")
        )
        rectangle = (
            Rect(40, 40)
            .translate(*s.ushape.bottom_left + [20, -40])
            .set_stroke("red")
            .add_child(Text("E"))
        )
        crosshair = (
            Drawing(Path().M(0, -5).L(0, 5).M(-5, 0).L(5, 0))
            .set_anchor(Anchor.CENTER)
            .set_opacity(0.5)
        )

        for color, (xp, yp) in zip(
            ["red", "blue", "green", "yellow"],
            [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
        ):
            s << Rect(10, 10).translate(*s.xy(xp, yp)).set_fill(color)
        s << [rectangle, circle, crosshair]
        s.updaters << TranslationUpdater(
            rectangle.transform, circle.transform, max_speed=300, acceleration=200
        )
        s.updaters << TranslationUpdater(
            s.transform, circle.transform, acceleration=500
        )
        s.updaters << TranslationUpdater(crosshair.transform, s.transform)
        s.animations << sequence(
            animate_path(
                circle.transform,
                Path()
                .M(*circle.ushape.center)
                .Q(*(s.ushape.center + s.ushape.right) / 2 + UP * 80, *s.ushape.right)
                .Q(*s.ushape.center + DOWN * 80, *s.ushape.left)
                .L(*s.ushape.top_left)
                .l(120, 0)
                .l(150, 80)
                .L(*s.ushape.bottom_right)
                .Q(
                    *(s.ushape.bottom_right + s.ushape.center) / 2
                    + UP * 50
                    + RIGHT * 50,
                    *s.ushape.center + [25, 0],
                ),
                duration=7,
                easing_function=easing.linear_easing,
            ),
            wait(),
        )
        s << (
            PythonText(code_blocks[4], font_size=4)
            .set_anchor(Anchor.BOTTOM_LEFT)
            .translate(*scene.ushape.bottom_left + [MARGIN, -MARGIN])
        )
    ##

    with scene as s:
        s << heading("Inheriting from AnimatedList")
        s << bullets(
            "Define basic visual properties.",
            "Define special animations for operations.",
        )

        s << (PythonText(code_blocks[316], font_size=6).set_anchor(Anchor.RIGHT))
        s << (PythonText(code_blocks[317], font_size=6).set_anchor(Anchor.LEFT))

    with scene as s:
        s << heading("Using AnimatedLister Inheritor")
        s << bullets(
            "Animate algorithms by writing them as normal.",
            "Add animation hooks (compare, swap).",
            "Return an sequence and push to Scene to animate.",
        )

        s << (
            PythonText(code_blocks[318], font_size=10)
            .set_anchor(Anchor.BOTTOM)
            .translate(*s.ushape.bottom + LEFT * 12 * 2)
        )

    scene.remove_drawable(bar)
    with scene as s:
        s << Text("Example visuscripts are available in the GitHub repository.")


def heading(text, font_size=HEADING):
    return (
        Text(text, font_size=HEADING)
        .set_anchor(Anchor.TOP_LEFT)
        .translate(*scene.ushape.top_left + [MARGIN, MARGIN])
    )


def bullet(text: str, font_size=BULLET):
    circle = Circle(2).set_anchor(Anchor.LEFT)
    circle.add_child(
        Text(text=text, font_size=font_size)
        .translate(*circle.tshape.right + [6, -1])
        .set_anchor(Anchor.LEFT)
    )
    return circle


def bullets(*args, font_size=BULLET):
    points = [bullet(arg, font_size=font_size) for i, arg in enumerate(args)]
    GridOrganizer((len(args), 1), (font_size * 1.3, 1)).set_transform(
        Transform(scene.ushape.top_left + [MARGIN, HEADING * 2])
    ).organize(points)
    return points


def get_all_code_blocks():
    pattern = r"##(\d+)(.*?)##"
    matches = re.findall(pattern, SELF_STRING, re.DOTALL)

    segments_dict = {}
    for x_str, segment_content in matches:
        x = int(x_str)
        full_segment = f"{segment_content}"
        segments_dict[x] = full_segment.strip("\n")
    return segments_dict


def _unused():
    from visuscript.animated_collection import AnimatedList, Var

    WIDTH = 8
    STROKE_WIDTH = 1
    ##316
    #

    class AnimatedBarList(AnimatedList[Var, Rect]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.num_comparisons = 0
            self.num_swaps = 0

        def new_drawable_for(self, var: Var):
            return (
                Rect(WIDTH, var.value)
                .set_fill("blue")
                .set_anchor(Anchor.BOTTOM)
                .set_stroke_width(STROKE_WIDTH)
            )

        def get_organizer(self):
            return GridOrganizer((1, len(self)), (1, WIDTH))

        ##
        ##317
        def swap(self, a, b, *args, **kwargs):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return bundle(
                super().swap(a, b).compress(),
                run(self.add_swap),
                flash(self.drawables[a].fill, "green"),
                flash(self.drawables[b].fill, "green") if a != b else None,
            )

        def compare(self, a: int, b: int):
            return bundle(
                run(self.add_compare),
                flash(self.drawables[a].fill, "light_gray"),
                flash(self.drawables[b].fill, "light_gray") if a != b else None,
            )

        def add_compare(self):
            self.num_comparisons += 1

        def add_swap(self):
            self.num_swaps += 1

    ##

    ##318
    def bubble_sort(abl: AnimatedBarList) -> animation.Animation:
        seq = sequence()
        changed = True
        while changed:
            changed = False
            for i in range(1, len(abl)):
                seq << abl.compare(i - 1, i)
                if abl[i - 1] > abl[i]:
                    seq << abl.swap(i - 1, i)
                    changed = True
        return seq

    ##


if __name__ == "__main__":
    main()
