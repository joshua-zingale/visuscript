from visuscript import *
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

    less_than = (Text(f"<", font_size=element1.height, anchor=Anchor.RIGHT).translate(*(element1.shape.left*1.5)).set_opacity(0.0)
                    .add_child(question_mark := Text("", font_size=element1.height/2).set_anchor(Anchor.BOTTOM)))
    question_mark.translate(*(less_than.shape.top*1.25)).fill.set_opacity(0.0)

    element1.add_child(less_than)

    sequence = AnimationSequence()

    sequence << AnimationBundle(
        TranslationAnimation(element1.transform, element2.transformed_shape.right + (element1.shape.right - element1.shape.left)/1.25),
        ScaleAnimation(element1.transform, 0.5),
        fade_in(less_than),
        fade_in(question_mark),
    )

    if var1 > var2:
        target_color = 'green'
        new_text = "✓"
    else:
        target_color = 'red'
        new_text = "X"

    sequence << AnimationBundle(
        RgbAnimation(less_than.fill, target_color),
        RgbAnimation(question_mark.fill, target_color),
        OpacityAnimation(question_mark.fill, 1.0),
        RunFunction(lambda : question_mark.set_text(new_text))
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

def main():

    # config.canvas_color='off_white'
    # config.drawing_stroke='dark_slate'
    # config.drawing_fill=Color('dark_slate', 0)
    # config.text_fill=Color('dark_slate', 1)
    radius = 16

    scene = Scene()


    with scene as s:
            

        text = Text("Binary Trees", font_size=50).set_opacity(0.0)
        s << text
        s.player << fade_in(text)
        s.player << TransformAnimation(text.transform, Transform(s.xy(0,0) + [text.width/3, text.height/3], scale=2/3))


        tree = AnimatedBinaryTreeArray([Var(None) for _ in range(15)], radius=radius, transform=[0,-75])

        s << tree.structure_element

        s.player << animate_insert(Var(5), tree)
        s.player << animate_insert(Var(3), tree)
        s.player << animate_insert(Var(7), tree)
        s.player << animate_insert(v := Var(8), tree)



        

        
            





if __name__ == '__main__':
    main()