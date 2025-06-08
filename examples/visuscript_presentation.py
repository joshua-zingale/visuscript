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
from visuscript.code import PythonText
from visuscript.connector import Arrow
with open(__file__, 'r') as f:
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
        count = Text(str(self._slide_count), font_size=PAGINATION).translate(*self.shape.bottom_right - [MARGIN, MARGIN]).set_anchor(Anchor.BOTTOM_RIGHT)
        self.add_drawable(count)
        super().print()
        self.remove_drawable(count)
    def __enter__(self):
        return super().__enter__()
    def __exit__(self, *args, **kwargs):
        self.print()
        super().__exit__(*args, **kwargs)
scene = Slideshow()
scene.transform.set_translation([25,0]).set_scale(1.125) # Hack for Google Chrome correction
def main():
    code_blocks = get_all_code_blocks()
    with scene as s:
        title = Text("Visuscript", font_size=HEADING).translate(*UP*20)
        subtitle = Text("A Vector-Graphics-Based Animation Library for Python", font_size=NORMAL).set_anchor(Anchor.TOP).translate(*title.transformed_shape.bottom + DOWN*10)
        attribution = Text("by Joshua Zingale", font_size=NORMAL).set_anchor(Anchor.TOP).set_anchor(Anchor.TOP).translate(*subtitle.transformed_shape.bottom + DOWN*10)
        s << (title, subtitle, attribution)
        
        organizer = GridOrganizer((2,2), (s.height/2, s.width/2))
        get_rect = lambda: Rect(20,20).set_opacity(0.0).add_children(
            Circle(5).translate(-10,-10),
            Circle(5).translate(10,-10),
            Circle(5).translate(-10,10),
            Circle(5).translate(10,10),
        )

        rects: list[Rect] = []
        for transform in organizer:
            rects.append(get_rect())
            rects[-1].set_transform(Transform([-s.width/4, -s.height/4]) @ transform)

        s << rects


        for rect in rects:
            s.animations << [
                OpacityAnimation(rect, 1),
                RotationAnimation(rect.transform, 360),
            ]

    bar = Drawing(Path().M(*scene.shape.top_left + DOWN*HEADING + DOWN*MARGIN + DOWN*2 + RIGHT*MARGIN).l(scene.width/3,0))
    scene << bar

    ##1
    with scene as s:
        s << heading("Features")
        s << bullets(
            "Create arbitrary 2D graphics with Drawing and Path.",
            "Create arbitrary animations through composition with AnimationBundle and AnimationSequence.",
            "Represent and animate datastructures with AnimatedCollection inheritors.",
            "Runtime checks for conflicting animations or updaters with PropertyLocker.",
        font_size=NORMAL)
        s << (PythonText(code_blocks[1], font_size=9)
              .set_anchor(Anchor.BOTTOM_LEFT)
              .translate(*scene.shape.bottom_left + [MARGIN, -MARGIN]))
    ##

    with scene as s:
        s << heading("API")

        def components(obj, *components):
            elements = [*components]
            scale_factor = obj.transform.scale[0]/1.75
            for i, component in enumerate(components):
                component.scale(scale_factor).translate(*obj.transformed_shape.center +Vec2((-130 + 130*i)*scale_factor,110*scale_factor**0.25)*scale_factor)
                elements.append(Arrow(source=component, destination=obj))
            return elements
        scene_node = Circle(HEADING).add_child(Text("Scene", font_size=NORMAL)).scale(1.5).translate(0,-50)
        drawable_node = Circle(HEADING).add_child(Text("Drawables", font_size=NORMAL))
        animation_node = Circle(HEADING).add_child(Text("Animations", font_size=NORMAL))
        updater_node = Circle(HEADING).add_child(Text("Updaters", font_size=NORMAL))
        s << scene_node
        s << components(scene_node, drawable_node, animation_node, updater_node)
        s << components(drawable_node,
                        Circle(NORMAL).add_child(Text("Circle", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("Rect", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("Arrow", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0))
                        )
        s << components(animation_node,
                        Circle(NORMAL).add_child(Text("TransformAnimation", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("RgbAnimation", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("AnimationSequence", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0))
                        )
        s << components(updater_node,
                        Circle(NORMAL).add_child(Text("TranslationUpdater", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("FunctionUpdater", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0)),
                        Circle(NORMAL).add_child(Text("UpdaterBundle", font_size=NORMAL).rotate(-15)).set_stroke(Color(opacity=0))
                        )

    with scene as s:
        s << heading("Animation Pipeline")

        steps = [Text("Python"), Text("SVG"), Text("PNG"), Text("MP4")]
        converters = [Text("Visuscript"), Text("librsvg"), Text("ffmpeg")]
        
        separation = steps[0].width*1.5

        GridOrganizer((1,4),(1,separation)).set_transform(Transform([-separation*(len(steps)-1)/2,0])).organize(steps)

        for prev, curr, converter in zip(steps, steps[1:], converters):
            arrow =  Arrow(source=prev, destination=curr)
            s << arrow
            s << converter.translate(*arrow.shape.top + 10*UP).set_anchor(Anchor.BOTTOM).scale(0.5)
        s << steps

        s << Text("> visuscript my_animation_script.py --output my_animation.mp4").translate(0,25).scale(0.40)


        

    ##2
    # You can define an arbitrary shape using an SVG Path
    drawing = (Drawing(Path()
                          .M(0,10)
                          .L(20,10)
                          .L(20,20)
                          .Q(100,10,20,0)
                          .L(20,20))
                        .set_anchor(Anchor.CENTER)
                        .translate(120, -10)
                        .scale(3)
                        .rotate(-120)
                        .set_stroke('red'))
    scene << drawing
    with scene as s:
        s << heading("Arbitrary 2D Shape")
        s << (PythonText(code_blocks[2], font_size=8)
              .set_anchor(Anchor.BOTTOM_LEFT)
              .translate(*scene.shape.bottom_left + [MARGIN, -MARGIN]))
    ##

    ##3
    with scene as s:
        s << heading("Animation")
        s.animations << AnimationSequence(
            AnimationBundle(
                RotationAnimation(drawing.transform, drawing.transform.rotation + 360),
                ScaleAnimation(drawing.transform, 1)),
            PathAnimation(drawing.transform, Path()
                                      .M(*drawing.transformed_shape.center)
                                      .L(0,0)
                                      .Q(100,100, *s.shape.right)
                                      .Q(0,-100, *s.shape.left)
                                      .L(*drawing.shape.center),
                                      duration=2),
            ScaleAnimation.lazy(drawing.transform, 3),
            fade_out(drawing),
            )
        s << (PythonText(code_blocks[3], font_size=7.5)
              .set_anchor(Anchor.BOTTOM_LEFT)
              .translate(*scene.shape.bottom_left + [MARGIN, -MARGIN]))
    ##

    ##4        
    with scene as s:
        from visuscript.animation import linear_easing
        s << heading("Updaters")
        circle = Circle(20).add_child(Rect(10,10).set_fill('green').set_stroke('green')).set_stroke("blue")
        rectangle = Rect(40,40).translate(*s.shape.bottom_left + [20, -40]).set_stroke("red").add_child(
            Text("E")
        )
        crosshair = Drawing(Path().M(0, -5).L(0,5).M(-5,0).L(5,0)).set_anchor(Anchor.CENTER).set_opacity(0.5)

        for color, (xp, yp) in zip(['red','blue','green','yellow'], [(.25, .25), (.25, .75), (.75,.25),(.75,.75)]):
            s << Rect(10,10).translate(*s.xy(xp, yp)).set_fill(color)
        s << [rectangle, circle, crosshair]
        s.updaters << TranslationUpdater(rectangle.transform, circle.transform, max_speed=300, acceleration=200)
        s.updaters << TranslationUpdater(s.transform, circle.transform, acceleration=500)
        s.updaters << TranslationUpdater(crosshair.transform, s.transform)
        s.animations << AnimationSequence(
            PathAnimation(circle.transform, Path()
                            .M(*circle.shape.center)
                            .Q(*(s.shape.center + s.shape.right)/2 + UP*80, *s.shape.right)
                            .Q(*s.shape.center + DOWN*80, *s.shape.left)
                            .L(*s.shape.top_left)
                            .l(120,0)
                            .l(150,80)
                            .L(*s.shape.bottom_right)
                            .Q(*(s.shape.bottom_right + s.shape.center)/2+UP*50+RIGHT*50, *s.shape.center+[25,0]),
                            duration=7, easing_function=linear_easing),
            NoAnimation()
            )
        s << (PythonText(code_blocks[4], font_size=4)
              .set_anchor(Anchor.BOTTOM_LEFT)
              .translate(*scene.shape.bottom_left + [MARGIN, -MARGIN]))
    ##


    with scene as s:
        s << heading("Inheriting from AnimatedList")
        s << bullets("Define basic visual properties.",
                     "Define special animations for operations.")

        s << (PythonText(code_blocks[316], font_size=6).set_anchor(Anchor.RIGHT))
        s << (PythonText(code_blocks[317], font_size=6).set_anchor(Anchor.LEFT))

    with scene as s:
        s << heading("Using AnimatedLister Inheritor")
        s << bullets("Animate algorithms by writing them as normal.",
                     "Add animation hooks (compare, swap).",
                     "Return an AnimationSequence and push to Scene to animate.")
        
        s << (PythonText(code_blocks[318], font_size=10)
              .set_anchor(Anchor.BOTTOM)
              .translate(*s.shape.bottom + LEFT*12*2))
        
    
    scene.remove_drawable(bar)
    with scene as s:
        s << Text("Example visuscripts are available in the GitHub repository.")

        

def heading(text, font_size = HEADING):
    return Text(text, font_size=HEADING).set_anchor(Anchor.TOP_LEFT).translate(*scene.shape.top_left + [MARGIN,MARGIN])

def bullet(text: str, font_size=BULLET):
    circle = Circle(2, anchor=Anchor.LEFT)
    circle.add_child(
        Text(text=text, font_size=font_size, anchor=Anchor.LEFT).translate(*circle.transformed_shape.right + [6, -1])
    )
    return circle

def bullets(*args, font_size=BULLET):
    points = [bullet(arg, font_size=font_size) for i, arg in enumerate(args)]
    GridOrganizer((len(args), 1), (font_size*1.3, 1)).set_transform(Transform(scene.shape.top_left + [MARGIN, HEADING*2])).organize(points)
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
    ##316
    class AnimatedBarList(AnimatedList):
        def __init__(self, *args, **kwargs):
            super().__init__(*args,**kwargs)
            self.num_comparisons = 0
            self.num_swaps = 0

        def new_element_for(self, var: Var):
            return (Rect(WIDTH, var.value).set_fill("blue")
                    .set_anchor(Anchor.BOTTOM)
                    .set_stroke_width(STROKE_WIDTH))
        def get_organizer(self):
            return GridOrganizer((1,len(self)), (1,WIDTH))
    ##
    ##317
        def swap(self, a, b):
            return AnimationBundle(
                super().swap(a, b).compress(),
                RunFunction(self.add_swap),
                flash(self.elements[a].fill,
                      "green"),
                flash(self.elements[b].fill,
                      "green") if a != b else None,
                )
        def compare(self, a: int, b: int):
            return AnimationBundle(
                        RunFunction(self.add_compare),
                        flash(self.elements[a].fill,
                              "light_gray"),
                        flash(self.elements[b].fill,
                              "light_gray") if a != b else None,
                    )
        
        def add_compare(self):
            self.num_comparisons += 1
        def add_swap(self):
            self.num_swaps += 1
    ##



    ##318
    def bubble_sort(abl: AnimatedBarList) -> AnimationSequence:
        sequence = AnimationSequence()
        changed = True
        while changed:
            changed = False
            for i in range(1,len(abl)):
                sequence << abl.compare(i-1, i)
                if abl[i-1] > abl[i]:
                    sequence << abl.swap(i-1, i)
                    changed = True                
        return sequence
    ##


if __name__=="__main__":
    main()