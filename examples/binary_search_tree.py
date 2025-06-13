from visuscript import *
from visuscript.connector import *
from visuscript.element import Element
import numpy as np
from visuscript.config import *
from visuscript.animated_collection import AnimatedBinaryTreeArray, Var, NilVar
from typing import Tuple, Sequence
import random

RADIUS = 8
NUM_NODES = 31

def main():
    s = Scene()

    text = Text("Binary Search Trees", font_size=50).set_opacity(0.0)
    s << text
    s.player << fade_in(text)
    s.player << AnimationBundle(
        RunFunction(lambda: text.set_anchor(Anchor.TOP_LEFT, keep_position=True)),
        TransformAnimation.lazy(text.transform, Transform(s.shape.top_left + [10,10], scale=0.5))
        )

    tree = AnimatedBinaryTreeArray([Var(None) for _ in range(NUM_NODES)], radius=RADIUS, transform=[0,-75])

    s << tree.collection_element

    operation_text = Text("").set_anchor(Anchor.TOP_RIGHT).translate(*s.shape.top_right + [-10, 10])
    s << operation_text

    flash_text = lambda text, other_animation: AnimationSequence(
        RunFunction(lambda: operation_text.set_text(text)),
        fade_in(operation_text, duration = 0.5),
        other_animation,
        fade_out(operation_text, duration = 0.5)
    )
    s << (edges := Edges())

    random.seed(316)
    vars = list(map(Var, range(1,65)))
    random.shuffle(vars)
    vars = vars[:31]
    vars = insertion_order(vars)
    
    for speed, var in zip([1,1,1,1,2,3,6] + [20]*len(vars), vars):
        s.player << flash_text(f"insert({var.value})", animate_insert(var, tree, edges)).set_speed(speed)
    
    find_vars = map(Var, [23,41])
    for var in find_vars:
        s.player << flash_text(f"find({var.value})", animate_find(var, tree))

    remove_vars = list(map(Var, [12,11,43,46,40]))
    FIND = False
    NO_FIND = True
    for find, var in zip([FIND,FIND,FIND,FIND,FIND] + [NO_FIND]*len(remove_vars), remove_vars):
        s.player << flash_text(f"remove({var.value})", AnimationSequence(
            animate_find(var, tree) if find == FIND else None,
            animate_remove(var, tree, edges)
            )
            )

def to_balanced_tree(sequence: Sequence):
    sequence = sorted(sequence)
    new_sequence = [None]*len(sequence)

    worklist = [(0, len(sequence), 0)]
    while worklist:
        low, high, idx = worklist.pop(0)
        if low >= high:
            continue

        mid = (low + high)//2

        new_sequence[idx] = sequence[mid]

        worklist.extend([
            (low, mid, (idx+1)*2-1),
            (mid+1, high,(idx+1)*2)
        ])

    return new_sequence


def insertion_order(sequence: Sequence):
    sequence = to_balanced_tree(sequence)
    new_sequence = []

    worklist = [0]
        
    pop_random = lambda: worklist.pop(random.randrange(len(worklist)))

    while worklist:
        index = pop_random()
        if index >= len(sequence):
            continue
        new_sequence.append(sequence[index])

        worklist.extend([
            (index+1)*2 -1,
            (index+1)*2
        ])

    return new_sequence



class Edges(Drawable):
    def __init__(self):
        super().__init__()
        self._edges: dict[Tuple[Element, Element], Line] = dict()
        self._fading_away: set[Line] = set()

    @property
    def top_left(self):
        return Vec2(0,0)
    @property
    def width(self):
        return 0.0
    @property
    def height(self):
        return 0.0

    def get_edge(self, element1: Element, element2: Element):
        assert self.connected(element1, element2)
        return self._edges.get((element1, element2), self._edges[(element2, element1)])
    
    def connected(self, element1: Element, element2: Element):
        return (element1, element2) in self._edges or (element2, element1) in self._edges
    
    def connect(self, element1: Element, element2: Element):
        assert not self.connected(element1, element2)
        assert element1 is not element2

        edge = Line(source=element1, destination=element2).set_opacity(0.0)
        self._edges[(element1, element2)] = edge

        return fade_in(edge, duration=0.5)

    def disconnect(self, element1: Element, element2: Element):
        assert self.connected(element1, element2)
        if (element1, element2) in self._edges:
            edge = self._edges.pop((element1, element2))
        else:
            edge = self._edges.pop((element2, element1))
        
        self._fading_away.add(edge)

        return AnimationSequence(
            fade_out(edge),
            RunFunction(lambda:self._fading_away.remove(edge))
        )

    def draw(self):
        drawing = ""
        for edge in self._edges.values():
            drawing += edge.draw()
        for edge in self._fading_away:
            drawing += edge.draw()
        return drawing


def insert(var: Var, tree: AnimatedBinaryTreeArray) -> Var:
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
        TranslationAnimation.lazy(element2.transform, element1.transformed_shape.right + (element2.shape.right - element2.shape.left)/1.25),
        ScaleAnimation.lazy(element2.transform, 0.5),
    )

    sequence << AnimationBundle(
        fade_in(less_than),
    )

    sequence << NoAnimation()

    sequence << RunFunction(lambda : element2.remove_child(less_than))

    return sequence


def animate_insert(var: Var, tree: AnimatedBinaryTreeArray, edges: Edges):
    insert(var, tree)

    sequence = AnimationSequence()

    element = tree.element_for(var)
    
    element.set_transform(Transform([0,-150], scale=0))

    parent = NilVar
    node = tree.root
    while not node is var:
        parent = node
        sequence << compare("<", tree.element_for(node), element, node < var)

        if node < var:
            node = tree.get_right(node)
        else:
            node = tree.get_left(node)

    if not parent.is_none:
        sequence << edges.connect(tree.element_for(parent), tree.element_for(var))

    sequence << tree.organize()
    return sequence


def magnifying_glass(radius = 2*RADIUS, length = 2*RADIUS):

    unit = Vec2(np.cos(np.pi*3/8), np.sin(np.pi*3/8))

    start = radius * unit
    end = (radius + length) * unit

    return Circle(radius=radius).add_child(Drawing(path=Path().M(*start).L(*end))).set_fill(Color('white', opacity=0.0125))


def find(var: Var, tree:AnimatedBinaryTreeArray):
    node = tree.root
    while node != var and not node.is_none:
        if var <= node:
            node = tree.get_left(node)
        else:
            node = tree.get_right(node)
    return node


def animate_find(var: Var, tree: AnimatedBinaryTreeArray, font_size = 16):

    sequence = AnimationSequence()

    parent = NilVar
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
        ),
        center_cross := Text("X", fill='red', font_size=glass.shape.height).set_opacity(0.0)
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

        parent = node
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
            node = tree.get_left(node)
            sequence << AnimationBundle(
                RunFunction(lambda: less_than_check.set_fill('red')),
                RunFunction(lambda: less_than_check.set_text("X")),
                RunFunction(lambda: less_than.set_fill("red")),
                RunFunction(lambda: less_than.set_text(go_left_text)),
                OpacityAnimation(comparison, 1.0),
            )

        if node is NilVar and parent:

            sequence << AnimationBundle(
                TranslationAnimation.lazy(glass.transform, tree.target_for(parent).translation + [0, 3*RADIUS,0]),
                OpacityAnimation(check.fill, 0.0),
                OpacityAnimation(comparison, 0.0),
                )
        elif not node is NilVar:
            sequence << AnimationBundle(
                TransformAnimation.lazy(glass.transform, tree.element_for(node).transform),
                OpacityAnimation(check.fill, 0.0),
                OpacityAnimation(comparison, 0.0)
                )

        if node.is_none:
            break

    if node.is_none:
        sequence << OpacityAnimation(center_cross, 1.0)

    sequence << fade_out(glass)
    sequence << RunFunction(lambda: tree.remove_auxiliary_element(glass))
    return sequence


def animate_remove(var: Var, tree: AnimatedBinaryTreeArray, edges: Edges):
    assert var in tree

    sequence = AnimationSequence()

    removal_node = tree.root
    while removal_node != var:
        if removal_node < var:
            removal_node = tree.get_right(removal_node)
        else:
            removal_node = tree.get_left(removal_node)

    removal_element = tree.element_for(removal_node)
    tree.add_auxiliary_element(removal_element)

    # removal_element.add_child(
    #     removal_text := Text("Removing", font_size=8).translate(*removal_element.shape.top + 6*UP).set_opacity(0.0)
    # )

    sequence << AnimationBundle(
        RgbAnimation(removal_element.stroke, 'red'),
        # fade_in(removal_text)
        )
    
    if tree.number_of_children(removal_node) == 2:
        swap_node = tree.get_left(removal_node)
        sequence << RgbAnimation(tree.element_for(swap_node).stroke, 'blue')
        parent = swap_node
        while not tree.get_right(swap_node).is_none:
            parent = swap_node
            swap_node = tree.get_right(swap_node)
            sequence << AnimationBundle(
                RgbAnimation.lazy(tree.element_for(parent).stroke, 'off_white'),
                RgbAnimation(tree.element_for(swap_node).stroke, 'blue')
                )
            
        removal_parent = tree.get_parent(removal_node)
        sequence << AnimationBundle(
            edges.disconnect(tree.element_for(removal_node),tree.element_for(tree.get_left(removal_node))),
            edges.disconnect(tree.element_for(removal_node),tree.element_for(tree.get_right(removal_node))),
            edges.disconnect(tree.element_for(removal_parent),tree.element_for(removal_node)) if removal_parent else None,
            edges.disconnect(tree.element_for(swap_node), tree.element_for(tree.get_parent(swap_node)))
        )
        sequence << AnimationBundle(
            RgbAnimation(tree.element_for(parent).stroke, 'off_white'),
            edges.connect(tree.element_for(swap_node), tree.element_for(tree.get_left(removal_node))),
            edges.connect(tree.element_for(swap_node), tree.element_for(tree.get_right(removal_node))),
            edges.connect(tree.element_for(removal_parent), tree.element_for(swap_node)) if removal_parent else None,
            tree.quadratic_swap(removal_node, swap_node),
            )
        
        sequence << RgbAnimation.lazy(tree.element_for(swap_node).stroke, 'off_white')

    elif tree.get_parent(removal_node):
        sequence << AnimationBundle(
            edges.disconnect(tree.element_for(tree.get_parent(removal_node)), tree.element_for(removal_node)),
            edges.connect(tree.element_for(tree.get_parent(removal_node)), tree.element_for(tree.get_left(removal_node))) if tree.get_left(removal_node) else None,
            edges.connect(tree.element_for(tree.get_parent(removal_node)), tree.element_for(tree.get_right(removal_node))) if tree.get_right(removal_node) else None,
            )
    
    ## Reorganize tree if needed

    if tree.is_root(removal_node) or tree.get_left(tree.get_parent(removal_node)) is removal_node:
        removal_node_is_right_child = False
    else:
        removal_node_is_right_child = True
    
    removal_node_parent = tree.get_parent(removal_node)

    # Unprocessed node, new index
    move_queue = [(tree.get_left(removal_node), removal_node_parent, removal_node_is_right_child), (tree.get_right(removal_node), removal_node_parent, removal_node_is_right_child)]

    tree[tree.is_index(removal_node)] = Var(None)

    while move_queue:
        node, parent, is_right_child = move_queue.pop(0)

        if not node.is_none:
            move_queue.extend([
            (tree.get_left(node), node, False),
            (tree.get_right(node), node, True)
            ])

        if parent.is_none:
            old_index = tree.is_index(node)
            tree.quadratic_swap(0, node)
            tree[old_index] = Var(None)
            continue

        if node.is_none:
            continue
        
        old_index = tree.is_index(node)
        if is_right_child:
            tree.quadratic_swap(tree.get_right(parent), node)
        else:
            tree.quadratic_swap(tree.get_left(parent), node)

        tree[old_index] = Var(None)
    

    sequence << AnimationBundle(
        tree.organize(),
        fade_out(removal_element)
        )
    sequence << RunFunction(lambda: tree.remove_auxiliary_element(removal_element))
    return sequence




if __name__ == '__main__':
    main()