from visuscript import *
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray

def main():

    # config.canvas_color='off_white'
    # config.drawing_stroke='dark_slate'
    # config.drawing_fill=Color('dark_slate', 0)
    # config.text_fill=Color('dark_slate', 1)
    radius = 16

    scene = Scene()


    with scene as s:

        for _ in range(3):
            with s as s:
                text = Text("Binary Trees", font_size=50).set_opacity(0.0)
                s << text
                s.player << fade_in(text)
                s.player << TransformAnimation(text.transform, Transform(s.xy(0,0) + [text.width/2, text.height/2]))
                s.player << fade_out(text)


        arr = AnimatedBinaryTreeArray([0,1,2,3,4,5], radius=radius, transform=[0,-75])

        s << arr.structure_element

        for e in arr.elements:
                e.opacity = 0
                e.transform.scale = 0.6
                s.animations << OpacityAnimation(e, 1)

        s.animations << arr.organize()

        
            





if __name__ == '__main__':
    main()