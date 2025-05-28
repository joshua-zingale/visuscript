from visuscript import *
import numpy as np
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray

def insert(var: Var, tree: AnimatedBinaryTreeArray) -> Var:
    # Get insert index
    node = tree[0]
    while not node.is_none:
        if var <= node:
            node = tree.get_left(node)
        else:
            node = tree.get_right(node)

    if node is NilVar:
        assert False, "Tree not big enough"

    tree[tree.is_index(node)] = var

    return var

def compare(var1: Var, var2: Var, tree: AnimatedBinaryTreeArray):

    element1 = tree.element_for(var1)
    element2 = tree.element_for(var2)

    if var1 > var2:
        color = 'green'
        text = "✓"
    else:
        color = 'red'
        text = "X"

    less_than = (Text(f"<", font_size=element1.height, anchor=Anchor.RIGHT, fill=color).translate(*(element1.shape.left*1.5))
                    .add_child(question_mark := Text(text, font_size=element1.height/2, fill=color).set_anchor(Anchor.BOTTOM))).set_opacity(0.0)
    question_mark.translate(*(less_than.shape.top*1.25))

    element1.add_child(less_than)

    sequence = AnimationSequence()

    sequence << AnimationBundle(
        TranslationAnimation(element1.transform, element2.transformed_shape.right + (element1.shape.right - element1.shape.left)/1.25),
        ScaleAnimation(element1.transform, 0.5),
    )

    sequence << AnimationBundle(
        fade_in(less_than),
    )

    sequence << NoAnimation()

    sequence << RunFunction(lambda : element1.remove_child(less_than))

    return sequence


def animate_insert(var: Var, tree: AnimatedBinaryTreeArray):
    insert(var, tree)

    node = tree.root

    sequence = AnimationSequence()

    element = tree.element_for(var)
    
    element.set_transform(Transform([0,-150], scale=0))

    while not node is var:
        sequence << compare(var, node, tree)

        if var > node:
            node = tree.get_right(node)
        else:
            node = tree.get_left(node)


    sequence << tree.organize()
    return sequence


def magnifying_glass(radius = 32, length = 32):

    unit = Vec2(np.cos(np.pi*3/8), np.sin(np.pi*3/8))

    start = radius * unit
    end = (radius + length) * unit

    return Circle(radius=radius).add_child(Drawing(path=Path().M(*start).L(*end)))


def animate_find(var: Var, tree: AnimatedBinaryTreeArray):

    sequence = AnimationSequence()

    node = tree.root

    glass = magnifying_glass().set_transform(tree.element_for(node).transform).set_opacity(0.0)

    tree.add_auxiliary_element(glass)
    sequence << fade_in(glass)

    while True:

        if node == var:
            break

        if var > node:
            node = tree.get_right(node)
        else:
            node = tree.get_left(node)

        if not node is NilVar:
            sequence << TransformAnimation(glass.transform, tree.element_for(node).transform)

        if node.is_none:
            break

    sequence << fade_out(glass)
    sequence << RunFunction(lambda : tree.remove_auxiliary_element(glass))
    return sequence


def main():

    # config.canvas_color='off_white'
    # config.drawing_stroke=Color('dark_slate', 1.0)
    # config.drawing_fill=Color('dark_slate', 0.0)
    # config.text_fill=Color('dark_slate', 1)
    radius = 16

    scene = Scene()


    with scene as s:
            

        text = Text("Binary Search Trees", font_size=50).set_opacity(0.0)
        s << text
        s.player << fade_in(text)
        s.player << TransformAnimation(text.transform, Transform(s.xy(0,0) + [text.width/3, text.height/3], scale=2/3))


        tree = AnimatedBinaryTreeArray([Var(None) for _ in range(15)], radius=radius, transform=[0,-75])

        s << tree.structure_element

        s.player << animate_insert(Var(5), tree)
        s.player << animate_insert(Var(3), tree)
        s.player << animate_insert(Var(7), tree)
        s.player << animate_insert(v := Var(6), tree)

        s.player << animate_find(v, tree)



        

        
            





if __name__ == '__main__':
    main()