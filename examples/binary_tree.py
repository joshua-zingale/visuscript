from visuscript import *
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray

def main():

    config.canvas_color='off_white'
    config.drawing_stroke='dark_slate'
    config.drawing_fill=Color('dark_slate', 0)
    config.text_fill=Color('dark_slate', 1)
    config.animation_duration = 1
    radius = 16

    scene = Scene()

    with scene as s:

        arr = AnimatedBinaryTreeArray([0,1,2,3,4,5], radius=radius, transform=[0,-75])

        s << (circ := Circle(50))

        s << arr.structure_element

        s.player << arr.organize()

        s.animations << ScaleAnimation(circ.transform, 2)

        with s as s:
            s.animations << arr.swap(1,5)
            s.animations << arr.swap(0,3)
        
        s.player << AnimationBundle(
            arr.swap(0,2),
            arr.swap(1,3),
            arr.swap(4,5)
        )

            





if __name__ == '__main__':
    main()