from visuscript import *
from visuscript.element import Element
import numpy as np
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray, TextContainer

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

def compare(operator: str, element1: Element, element2: Element, is_true: bool):


    if is_true:
        color = 'green'
        text = "✓"
    else:
        color = 'red'
        text = "X"

    less_than = (Text(f"{operator}", font_size=element2.height, anchor=Anchor.RIGHT, fill=color).translate(*(element2.shape.left*1.5))
                    .add_child(question_mark := Text(text, font_size=element2.height/2, fill=color).set_anchor(Anchor.BOTTOM))).set_opacity(0.0)
    question_mark.translate(*(less_than.shape.top*1.25))

    element2.add_child(less_than)

    sequence = AnimationSequence()

    sequence << AnimationBundle(
        TranslationAnimation(element2.transform, element1.transformed_shape.right + (element2.shape.right - element2.shape.left)/1.25),
        ScaleAnimation(element2.transform, 0.5),
    )

    sequence << AnimationBundle(
        fade_in(less_than),
    )

    sequence << NoAnimation()

    sequence << RunFunction(lambda : element2.remove_child(less_than))

    return sequence


def animate_insert(var: Var, tree: AnimatedBinaryTreeArray):
    insert(var, tree)

    node = tree.root

    sequence = AnimationSequence()

    element = tree.element_for(var)
    
    element.set_transform(Transform([0,-150], scale=0))

    while not node is var:
        sequence << compare("<", tree.element_for(node), element, node < var)

        if node < var:
            node = tree.get_right(node)
        else:
            node = tree.get_left(node)


    sequence << tree.organize()
    return sequence


def magnifying_glass(radius = 32, length = 32):

    unit = Vec2(np.cos(np.pi*3/8), np.sin(np.pi*3/8))

    start = radius * unit
    end = (radius + length) * unit

    return Circle(radius=radius).add_child(Drawing(path=Path().M(*start).L(*end))).set_fill(Color('white', opacity=0.0125))


def animate_find(var: Var, tree: AnimatedBinaryTreeArray, font_size = 16):

    sequence = AnimationSequence()

    node = tree.root

    glass = magnifying_glass().set_transform(tree.element_for(node).transform).set_opacity(0.0)

    found_text = f"{var.value} ="
    not_found_text = f"{var.value} ≠"
    go_right_text = f"< {var.value} →"
    go_left_text = f"< {var.value} ←"
    glass.add_children(
        check := Text(not_found_text, fill=Color('red', 0.0)).set_anchor(Anchor.RIGHT).translate(*glass.shape.left + font_size*LEFT/2),
        comparison := Pivot().set_opacity(0.0).add_children(
            less_than := Text("", font_size=font_size).set_anchor(Anchor.LEFT).translate(*glass.shape.right + font_size*RIGHT/2),
            less_than_check := Text("", font_size=font_size/2).set_anchor(Anchor.LEFT).translate(*glass.shape.right + UP*font_size/2 + font_size*RIGHT/2),
        )
        )

    tree.add_auxiliary_element(glass)
    sequence << fade_in(glass)

    while True:

        if node == var:
            sequence << RunFunction(lambda: check.set_text(found_text))
            sequence << RunFunction(lambda: check.set_fill(Color('green', 0.0)))
            sequence << OpacityAnimation(check.fill, 1.0)
            break
        else:
            sequence << OpacityAnimation(check.fill, 1.0)

        if node < var:
            node = tree.get_right(node)
            sequence << AnimationBundle(
                RunFunction(lambda: less_than_check.set_fill('green')),
                RunFunction(lambda: less_than_check.set_text("✓")),
                RunFunction(lambda: less_than.set_fill("green")),
                RunFunction(lambda: less_than.set_text(go_right_text)),
                OpacityAnimation(comparison, 1.0),
            )
        else:
            sequence << AnimationBundle(
                RunFunction(lambda: less_than_check.set_fill('red')),
                RunFunction(lambda: less_than_check.set_text("X")),
                RunFunction(lambda: less_than.set_fill("red")),
                RunFunction(lambda: less_than.set_text(go_left_text)),
                OpacityAnimation(comparison, 1.0),
            )
            node = tree.get_left(node)

        if not node is NilVar:
            sequence << AnimationBundle(
                TransformAnimation(glass.transform, tree.element_for(node).transform),
                OpacityAnimation(check.fill, 0.0),
                OpacityAnimation(comparison, 0.0)
                )

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
            

        text = Text("Binary Search Trees", font_size=25).set_opacity(0.0)
        s << text
        s.player << fade_in(text)
        s.player << AnimationBundle(
            RunFunction(lambda: text.set_anchor(Anchor.TOP_LEFT, keep_position=True)),
            TransformAnimation(text.transform, Transform(s.xy(0.01,0.01)))
            )


        tree = AnimatedBinaryTreeArray([Var(None) for _ in range(15)], radius=radius, transform=[0,-75])

        s << tree.structure_element

        s.player << animate_insert(Var(5), tree)
        s.player << animate_insert(Var(3), tree)
        s.player << animate_insert(Var(7), tree)
        s.player << animate_insert(v := Var(6), tree)

        s.player << animate_find(v, tree)



        

        
            





if __name__ == '__main__':
    main()