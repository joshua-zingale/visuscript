from visuscript import *
from visuscript.drawable.connector import *
import numpy as np
from visuscript.config import *
from visuscript.animated_collection import (
    AnimatedList,
    Var,
    NullDrawable,
)
from visuscript.organizer import BinaryTreeOrganizer
from visuscript import connector
from typing import Sequence, Optional, Iterable
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
        TransformAnimation(
            text.transform, Transform(s.shape.top_left + [10, 10], scale=0.5)
        ),
    )

    tree = AnimatedBinaryTreeArray(
        [Var(None) for _ in range(NUM_NODES)],
        radius=RADIUS,
        transform=Transform([0, -75]),
    )

    s << tree.collection_drawable

    operation_text = (
        Text("").set_anchor(Anchor.TOP_RIGHT).translate(*s.shape.top_right + [-10, 10])
    )
    s << operation_text

    flash_text = lambda text, other_animation: AnimationSequence(
        RunFunction(lambda: operation_text.set_text(text)),
        fade_in(operation_text, duration=0.5),
        other_animation,
        fade_out(operation_text, duration=0.5),
    )

    random.seed(316)
    vars = list(map(Var, range(1, 65)))
    random.shuffle(vars)
    vars = vars[:31]
    vars = insertion_order(vars)

    for speed, var in zip([1, 1, 1, 1, 2, 3, 6] + [20] * len(vars), vars):
        s.player << flash_text(
            f"insert({var.value})", animate_insert(var, tree)
        ).set_speed(speed)

    find_vars = map(Var, [23, 41])
    for var in find_vars:
        s.player << flash_text(f"find({var.value})", animate_find(var, tree))

    remove_vars = list(map(Var, [12, 11, 43, 46, 40]))
    FIND = False
    NO_FIND = True
    for find, var in zip(
        [FIND, FIND, FIND, FIND, FIND] + [NO_FIND] * len(remove_vars), remove_vars
    ):
        s.player << flash_text(
            f"remove({var.value})",
            AnimationSequence(
                animate_find(var, tree) if find == FIND else None,
                animate_remove(var, tree),
            ),
        )


def to_balanced_tree(sequence: Sequence):
    sequence = sorted(sequence)
    new_sequence = [None] * len(sequence)

    worklist = [(0, len(sequence), 0)]
    while worklist:
        low, high, idx = worklist.pop(0)
        if low >= high:
            continue

        mid = (low + high) // 2

        new_sequence[idx] = sequence[mid]

        worklist.extend([(low, mid, (idx + 1) * 2 - 1), (mid + 1, high, (idx + 1) * 2)])

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

        worklist.extend([(index + 1) * 2 - 1, (index + 1) * 2])

    return new_sequence


def insert(var: Var, tree: "AnimatedBinaryTreeArray") -> Var:
    node = tree.root
    while node and not node.is_none:
        if var <= node:
            node = tree.get_left(node)
        else:
            node = tree.get_right(node)

    if node is None:
        assert False, "Tree not big enough"

    tree[tree.var_index(node)] = var

    return var


def compare(
    operator: str,
    drawable1: Pivot | Circle,
    drawable2: Pivot | Circle,
    is_true: bool,
):
    if is_true:
        color = "green"
        text = "✓"
    else:
        color = "red"
        text = "X"

    cmp_text = (
        Text(f"{operator}", font_size=drawable2.shape.height)
        .set_anchor(Anchor.RIGHT)
        .set_fill(color)
        .translate(*(drawable2.shape.left * 1.5))
        .add_child(
            question_mark := Text(text, font_size=drawable2.shape.height / 2)
            .set_anchor(Anchor.BOTTOM)
            .set_fill(color)
        )
    ).set_opacity(0.0)
    question_mark.translate(cmp_text.shape.top * 1.25)

    drawable2.add_child(cmp_text)

    # sequence = AnimationSequence()

    # sequence << AnimationBundle(
    #     TranslationAnimation(
    #         drawable2.transform,
    #         drawable1.transformed_shape.right
    #         + (drawable2.shape.right - drawable2.shape.left) / 1.25,
    #     ),
    #     ScaleAnimation(drawable2.transform, 0.5),
    # )

    # sequence << AnimationBundle(
    #     fade_in(cmp_text),
    # )

    # sequence << NoAnimation()

    # sequence << RunFunction(lambda: drawable2.remove_child(cmp_text))

    return AnimationSequence(
        AnimationBundle(
            TranslationAnimation(
                drawable2.transform,
                drawable1.transformed_shape.right
                + (drawable2.shape.right - drawable2.shape.left) / 1.25,
            ),
            ScaleAnimation(drawable2.transform, 0.5),
        ),
        fade_in(cmp_text),
        NoAnimation(),
        RunFunction(lambda: drawable2.remove_child(cmp_text)),
    )


def animate_insert(var: Var, tree: "AnimatedBinaryTreeArray"):
    insert(var, tree)

    sequence = AnimationSequence()

    drawable = tree.drawable_for(var)

    drawable.set_transform(Transform([0, -150], scale=0))

    parent = None
    node = tree.root
    while node is not var:
        parent = node
        sequence << compare("<", tree.drawable_for(node), drawable, node < var)

        if node < var:
            node = tree.get_right(node)
        else:
            node = tree.get_left(node)
        assert node is not None

    if parent is not None:
        sequence << tree.edges.connect(
            tree.drawable_for(parent), tree.drawable_for(var)
        )

    sequence << tree.organize()
    return sequence


def magnifying_glass(radius=2 * RADIUS, length=2 * RADIUS):
    unit = Vec2(np.cos(np.pi * 3 / 8), np.sin(np.pi * 3 / 8))

    start = radius * unit
    end = (radius + length) * unit

    return (
        Circle(radius=radius)
        .add_child(Drawing(path=Path().M(*start).L(*end)))
        .set_fill(Color("white", opacity=0.0125))
    )


def find(var: Var, tree: "AnimatedBinaryTreeArray"):
    node = tree.root
    while node != var and node is not None and not node.is_none:
        if var <= node:
            node = tree.get_left(node)
        else:
            node = tree.get_right(node)
    return node


def animate_find(var: Var, tree: "AnimatedBinaryTreeArray", font_size=16):
    sequence = AnimationSequence()

    parent = None
    node = tree.root

    glass = (
        magnifying_glass()
        .set_transform(tree.drawable_for(node).transform)
        .set_opacity(0.0)
    )

    found_text = f"{var.value} ="
    not_found_text = f"{var.value} ≠"
    go_right_text = f"< {var.value} →"
    go_left_text = f"< {var.value} ←"
    glass.add_children(
        check := Text(not_found_text)
        .set_fill(Color("red", 0.0))
        .set_anchor(Anchor.RIGHT)
        .translate(*glass.shape.left + font_size * LEFT / 2),
        comparison := Pivot()
        .set_opacity(0.0)
        .add_children(
            less_than := Text("", font_size=font_size)
            .set_anchor(Anchor.LEFT)
            .translate(*glass.shape.right + font_size * RIGHT / 2),
            less_than_check := Text("", font_size=font_size / 2)
            .set_anchor(Anchor.LEFT)
            .translate(*glass.shape.right + UP * font_size / 2 + font_size * RIGHT / 2),
        ),
        center_cross := Text("X", font_size=glass.shape.height)
        .set_opacity(0.0)
        .set_fill("red"),
    )

    tree.add_auxiliary_drawable(glass)
    sequence << fade_in(glass)

    while True:
        if node == var:
            sequence << RunFunction(lambda: check.set_text(found_text))
            sequence << RunFunction(lambda: check.set_fill(Color("green", 0.0)))
            sequence << OpacityAnimation(check.fill, 1.0)
            break
        else:
            sequence << OpacityAnimation(check.fill, 1.0)

        parent = node
        if node < var:
            node = tree.get_right(node)
            sequence << AnimationBundle(
                RunFunction(lambda: less_than_check.set_fill("green")),
                RunFunction(lambda: less_than_check.set_text("✓")),
                RunFunction(lambda: less_than.set_fill("green")),
                RunFunction(lambda: less_than.set_text(go_right_text)),
                OpacityAnimation(comparison, 1.0),
            )
        else:
            node = tree.get_left(node)
            sequence << AnimationBundle(
                RunFunction(lambda: less_than_check.set_fill("red")),
                RunFunction(lambda: less_than_check.set_text("X")),
                RunFunction(lambda: less_than.set_fill("red")),
                RunFunction(lambda: less_than.set_text(go_left_text)),
                OpacityAnimation(comparison, 1.0),
            )

        if node is None and parent:
            sequence << AnimationBundle(
                TranslationAnimation(
                    glass.transform,
                    tree.target_for(parent).translation + DOWN * 3 * RADIUS,
                ),
                OpacityAnimation(check.fill, 0.0),
                OpacityAnimation(comparison, 0.0),
            )
        elif node is not None:
            sequence << AnimationBundle(
                TransformAnimation(glass.transform, tree.drawable_for(node).transform),
                OpacityAnimation(check.fill, 0.0),
                OpacityAnimation(comparison, 0.0),
            )

        if node is None or node.is_none:
            break

    if node is None or node.is_none:
        sequence << OpacityAnimation(center_cross, 1.0)

    sequence << fade_out(glass)
    sequence << RunFunction(lambda: tree.remove_auxiliary_drawable(glass))
    return sequence


def animate_remove(
    var: Var, tree: "AnimatedBinaryTreeArray", sequence: AnimationSequence | None = None
):
    assert var in tree

    sequence = sequence or AnimationSequence()

    removal_node = tree.root
    while removal_node != var:
        if removal_node < var:
            removal_node = tree.get_right(removal_node)
        else:
            removal_node = tree.get_left(removal_node)
        assert removal_node is not None

    removal_drawable = tree.drawable_for(removal_node)
    tree.add_auxiliary_drawable(removal_drawable)

    assert not isinstance(removal_drawable, NullDrawable)

    sequence << AnimationBundle(
        RgbAnimation(removal_drawable.stroke, "red"),
    )

    if len(tree.get_children(removal_node)) == 2:
        swap_node = tree.get_left(removal_node)
        assert swap_node is not None
        sequence << RgbAnimation(tree.drawable_for(swap_node).stroke, "blue")
        parent = swap_node

        while swap_node is not None and tree.has_right(swap_node):
            parent = swap_node
            swap_node = tree.get_right(swap_node)
            assert swap_node is not None
            sequence << AnimationBundle(
                RgbAnimation(tree.drawable_for(parent).stroke, "off_white"),
                RgbAnimation(tree.drawable_for(swap_node).stroke, "blue"),
            )

        removal_parent = tree.get_parent(removal_node)
        sequence << AnimationBundle(
            tree.edges.disconnect(
                tree.drawable_for(removal_node),
                tree.drawable_for(tree.get_left(removal_node)),
            ),
            tree.edges.disconnect(
                tree.drawable_for(removal_node),
                tree.drawable_for(tree.get_right(removal_node)),
            ),
            tree.edges.disconnect(
                tree.drawable_for(removal_parent), tree.drawable_for(removal_node)
            )
            if removal_parent
            else None,
            tree.edges.disconnect(
                tree.drawable_for(swap_node),
                tree.drawable_for(tree.get_parent(swap_node)),
            ),
        )
        sequence << AnimationBundle(
            RgbAnimation(tree.drawable_for(parent).stroke, "off_white"),
            tree.edges.connect(
                tree.drawable_for(swap_node),
                tree.drawable_for(tree.get_left(removal_node)),
            ),
            tree.edges.connect(
                tree.drawable_for(swap_node),
                tree.drawable_for(tree.get_right(removal_node)),
            ),
            tree.edges.connect(
                tree.drawable_for(removal_parent), tree.drawable_for(swap_node)
            )
            if removal_parent
            else None,
            tree.qswap(removal_node, swap_node),
        )

        sequence << RgbAnimation(tree.drawable_for(swap_node).stroke, "off_white")

    elif tree.get_parent(removal_node):
        sequence << AnimationBundle(
            tree.edges.disconnect(
                tree.drawable_for(tree.get_parent(removal_node)),
                tree.drawable_for(removal_node),
            ),
            tree.edges.connect(
                tree.drawable_for(tree.get_parent(removal_node)),
                tree.drawable_for(tree.get_left(removal_node)),
            )
            if tree.get_left(removal_node)
            else None,
            tree.edges.connect(
                tree.drawable_for(tree.get_parent(removal_node)),
                tree.drawable_for(tree.get_right(removal_node)),
            )
            if tree.get_right(removal_node)
            else None,
        )

    ## Reorganize tree if needed

    if (
        tree.is_root(removal_node)
        or tree.get_left(tree.get_parent(removal_node)) is removal_node
    ):
        removal_node_is_right_child = False
    else:
        removal_node_is_right_child = True

    removal_node_parent = tree.get_parent(removal_node)

    # Unprocessed node, new index
    move_queue = [
        (tree.get_left(removal_node), removal_node_parent, removal_node_is_right_child),
        (
            tree.get_right(removal_node),
            removal_node_parent,
            removal_node_is_right_child,
        ),
    ]

    tree[tree.var_index(removal_node)] = Var(None)

    while move_queue:
        node, parent, is_right_child = move_queue.pop(0)

        if node is not None and not node.is_none:
            move_queue.extend(
                [(tree.get_left(node), node, False), (tree.get_right(node), node, True)]
            )

        if parent is None or parent.is_none:
            old_index = tree.var_index(node)
            tree.qswap(0, node)
            tree[old_index] = Var(None)
            continue

        if node is None or node.is_none:
            continue

        old_index = tree.var_index(node)
        if is_right_child:
            tree.qswap(tree.get_right(parent), node)
        else:
            tree.qswap(tree.get_left(parent), node)

        tree[old_index] = Var(None)

    sequence << AnimationBundle(tree.organize(), fade_out(removal_drawable))
    sequence << RunFunction(lambda: tree.remove_auxiliary_drawable(removal_drawable))
    return sequence


class AnimatedBinaryTreeArray(AnimatedList[Var, NullDrawable | Circle]):
    def __init__(
        self,
        variables: Iterable[Var],
        *,
        radius: float,
        level_heights: float | None = None,
        node_width: float | None = None,
        transform: Transform.TransformLike | None = None,
    ):
        self._radius = radius
        self.level_heights = level_heights or 3 * radius
        self.node_width = node_width or 3 * radius

        self._edges = connector.Edges()
        self.add_auxiliary_drawable(self._edges)
        super().__init__(variables, transform=transform)

    @property
    def edges(self) -> connector.Edges:
        return self._edges

    def get_organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(
            num_levels=num_levels,
            level_heights=self.level_heights,
            node_width=self.node_width,
        )

    def new_drawable_for(self, var: Var) -> Circle | NullDrawable:
        if var.is_none:
            return NullDrawable()
        n = Circle(radius=self._radius).add_child(
            Text(str(var.value), font_size=self._radius)
        )
        return n

    def get_parent_index(self, var: int | Var):
        if isinstance(var, int):
            var = self[var]
        return int((self.var_index(var) + 1) // 2) - 1

    def get_left_index(self, var: int | Var):
        if isinstance(var, int):
            var = self[var]
        return int((self.var_index(var) + 1) * 2) - 1

    def get_right_index(self, var: int | Var):
        return self.get_left_index(var) + 1

    @property
    def root(self) -> Var:
        return self[0]

    def get_parent(self, var: Var) -> Optional[Var]:
        idx = self.get_parent_index(var)

        if idx < 0:
            return None

        return self[idx]

    def get_left(self, var: Var) -> Optional[Var]:
        idx = self.get_left_index(var)

        if idx >= len(self):
            return None

        return self[idx]

    def get_right(self, var: Var) -> Optional[Var]:
        idx = self.get_right_index(var)

        if idx >= len(self):
            return None

        return self[idx]

    def has_left(self, var: Var) -> bool:
        maybe_left = self.get_left(var)
        return maybe_left is not None and not maybe_left.is_none

    def has_right(self, var: Var) -> bool:
        maybe_right = self.get_right(var)
        return maybe_right is not None and not maybe_right.is_none

    def is_root(self, var: Var) -> bool:
        return self.root is var

    def is_child(self, var: Var) -> bool:
        return self.get_parent(var) is not None

    def is_leaf(self, var: Var) -> bool:
        return self.get_left(var) is None and self.get_right(var) is None

    def get_children(self, var: Var) -> list[Var]:
        children: list[Var] = []
        for maybe_child in (self.get_left(var), self.get_right(var)):
            if maybe_child is not None and not maybe_child.is_none:
                children.append(maybe_child)
        return children


if __name__ == "__main__":
    main()
