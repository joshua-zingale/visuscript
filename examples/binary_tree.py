from visuscript import *
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray

def main():

    # config.canvas_color='off_white'
    # config.drawing_stroke='dark_slate'
    # config.drawing_fill=Color('dark_slate', 0)
    # config.text_fill=Color('dark_slate', 1)
    config.animation_duration = 1
    radius = 16

    scene = Scene()


    with scene as s:

        arr = AnimatedBinaryTreeArray([0,1,2,3,4,5], radius=radius, transform=[0,-75])

        s << arr.structure_element

        for e in arr.elements:
                e.opacity = 0
                e.transform.scale = 0.6
                s.animations << OpacityAnimation(e, 1)

        s.animations << arr.organize()

        
            





if __name__ == '__main__':
    main()