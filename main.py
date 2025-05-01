#!.venv/bin/python
from visuscript.primatives import *
from visuscript.drawings import *
from visuscript.output import print_frame

for x in range(400, 600, 12):
    elements = []

    item = Circle(radius=240, transform=Transform([x, 360])).with_children([
        Circle(radius=100, color="blue")
    ])

    canvas = Canvas().with_children([item])


    # Convert SVG to PNG using wand
    print_frame(canvas)


    # elements.append(
    #     svg.SVG(
    #         elements=[
    #             svg.Style(
    #                 text=dedent("""
    #                     .small { font: italic 13px sans-serif; }
    #                     .heavy { font: bold 30px sans-serif; }

    #                     /* Note that the color of the text is set with the    *
    #                     * fill property, the color property is for HTML only */
    #                     .Rrrrr { font: italic 40px serif; fill: red; }
    #                 """),
    #             ),
    #             svg.Text(x=0, y=100, class_=["small"], text="My"),
    #             svg.Text(x=0, y=120, class_=["heavy"], text="cat"),
    #             svg.Text(x=0, y=130, class_=["small"], text="is"),
    #             svg.Text(x=0, y=170, class_=["Rrrrr"], text="Grumpy!"),
    #         ],
    #     )
    # )