from visuscript.canvas import Canvas
from visuscript.scene import Scene
from visuscript.text import *
from visuscript.drawable import *
from visuscript.primatives import *
from visuscript.segment import *
from visuscript.animation import *
from visuscript.output import save_svg, save_png
from utility import *
from visuscript.utility import *

i = 2
j = 1
def save_slide(c: Canvas):
    global i
    global j
    save_svg(c, f"./midterm_slides/{i-1}-{j}.svg")
    i += 1
    j = 1
def save_subslide(c: Canvas):
    global i
    global j
    save_svg(c, f"./midterm_slides/{i-1}-{j}.svg")
    j += 1

ss = self_string().split("## SLIDE")
def curr_code():
    global ss
    global i
    return ss[i]

## SLIDE
c = Canvas()
c << (t := Text(text="Visuscript", font_size=50, fill='pale_green').set_transform([0,-40]).with_children([
    Text(text="A Vector Graphics Library for Didactic Animations", font_size=20).set_transform([0,50]),
    Text(text="by Joshua Zingale", font_size=20).set_transform([0,90]),
]))


save_slide(c)

## SLIDE

c = Canvas()
c << Text(text="Visuscript", font_size=50, fill='pale_green').set_transform([0,-40]).with_children([
    Text(text="A Vector Graphics Library for Didactic Animations", font_size=20).set_transform([0,50]),
    Text(text="by Joshua Zingale", font_size=20).set_transform([0,90]),
])
c << get_multiline_texts(curr_code(), 7, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])

save_slide(c)

## SLIDE
c = Canvas()
c << Rect(width=300, height=100).with_children([
    Drawing(path=Path().L(0,50).L(75,50).Z(), transform=[-100,0]),
    Rect(width=30,height=30, stroke='blue'),
    Circle(37.5, fill=Color("purple",0.5), stroke="blue"),
    Drawing(path=Path().L(10,30).L(20,0).L(10,15).Z().M(35,8).l(-20,0).l(10,5).q(10,7,-10,17),
            stroke='pale_green', fill="off_white", stroke_width=3).set_transform([100,0])
])

c << get_multiline_texts(curr_code(), 7, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])

save_slide(c)

## SLIDE
s = Scene()
graphic = Drawing(path=Path().L(10,30).L(20,0).L(10,15).Z().M(35,8).l(-20,0).l(10,5).q(10,7,-10,17),
            stroke='pale_green', fill="off_white", stroke_width=3)
s << graphic
s.animations << AnimationSequence(
    PathAnimation(graphic, Path().Q(50,-30, 100,30), fps=24, duration=1),
    NoAnimation(duration=0.2)
    )
s << get_multiline_texts(curr_code(), 7, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])
for frame in s.frames:
    save_subslide(frame)
save_slide(s)

## SLIDE
s = Scene()
graphic = Drawing(path=Path().L(10,30).L(20,0).L(10,15).Z().M(35,8).l(-20,0).l(10,5).q(10,7,-10,17),
            stroke='pale_green', fill="off_white", stroke_width=3)
s << graphic
s.animations << AnimationSequence(
    PathAnimation(graphic, Path().Q(50,-30, 30,-50), fps=24, duration=1),
    NoAnimation(duration=0.2)
    )
s.animations << ScaleAnimation(graphic, 2, duration=1)
s << get_multiline_texts(curr_code(), 7, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])

for frame in s.frames:
    save_subslide(frame)
save_slide(s)

## SLIDE
c = Canvas()
c << get_multiline_texts(curr_code(), 7, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])
"""
def Var:
    ...
    def __gt__(self, other: Self):
        og_transform = deepcopy(self.text_element.transform)
        width = self.text_element.width
        comparison = Text(text=f" > {other.value}", transform=Transform([width/2,0], scale=0), font_size=self.text_element.font_size, anchor=Anchor.LEFT).set_parent(self.text_element)
        total_width = width + comparison.width

        scale = width/total_width

        xy = self.text_element.transform.xy

        self._scene.animations << AnimationSequence(
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=Transform(xy + [-comparison.width/2*scale, 0], scale=scale)),ScaleAnimation(comparison, 1)),
            NoAnimation(),
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=og_transform), ScaleAnimation(comparison, 0.0)),
            RF(lambda : comparison.set_parent(None))
            )

        self._scene.pf()
        return self.value > other.value
"""

c << Text(text="Data structure updates can be auto visualized by overloading opperators.", font_size=15, anchor=Anchor.LEFT, transform=[c.x(0.01),c.y(0.85)])

save_slide(c)

## SLIDE
c = Canvas()
arrow = lambda : Drawing(path=Path().L(25,0).l(0,-3).l(2,3).l(-2,3).l(0,-3), anchor=Anchor.LEFT).set_fill('off_white')
fs = 10
c << Text(text="Video Pipeline", font_size=30).set_transform([0,-100])
c << Text(font_size=13, text="  visuscript      magick convert        ffmpeg").set_transform([0,-18])
c << Text(text="Python", font_size=fs, anchor=Anchor.LEFT).set_transform([-150,0]).with_child(arrow().set_transform([6*fs,0])
                                                  .with_child(
                                                      Text(text="svg", font_size=fs,anchor=Anchor.LEFT).set_transform([6*fs,0])
                                                        .with_child(arrow().set_transform([3*fs,0])
                                                            .with_child(Text(text="png", font_size=fs,anchor=Anchor.LEFT).set_transform([6*fs,0])
                                                                        .with_child(arrow().set_transform([3*fs,0])
                                                                            .with_child(Text(text="mp4", font_size=fs,anchor=Anchor.LEFT).set_transform([6*fs,0])
                                                                        ))))))
save_slide(c)


## SLIDE
c = Canvas()
c << get_multiline_texts(curr_code(), 10, anchor=Anchor.TOP_LEFT).set_transform([c.x(0.01),c.y(0)])

c << Text(text="Video demos to follow for two basic sorting algorithms." , font_size = 15)

save_slide(c)


