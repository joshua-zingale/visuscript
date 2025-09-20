from visuscript import *
from visuscript.animation import Animation, quadratic_swap, LazyAnimation
from visuscript.drawable.connector import *
import math
from visuscript.config import *
from visuscript.animated_collection import (
    AnimatedCollection,
)
from visuscript.primatives import TransformMixin
from visuscript.organizer import BinaryTreeOrganizer
from visuscript import connector
from typing import Sequence, Optional, Generic, TypeVar, Self, Literal
import random
import operator as op


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
            text.transform, Transform(s.ushape.top_left + [10, 10], scale=0.5)
        ),
    )

    tree = AnimatedBinarySearchTree(
        num_levels=int(math.log2(NUM_NODES + 1)),
        radius=RADIUS,
    ).set_transform(UP * 75)

    s << tree.collection_drawable

    operation_text = (
        Text("").set_anchor(Anchor.TOP_RIGHT).translate(s.ushape.top_right + [-10, 10])
    )

    s << operation_text

    flash_text = lambda text, other_animation: AnimationSequence(
        RunFunction(lambda: operation_text.set_text(text)),
        fade_in(operation_text, duration=0.5),
        other_animation,
        fade_out(operation_text, duration=0.5),
    )

    random.seed(316)
    nums = list(range(1, 65))
    random.shuffle(nums)
    nums = nums[:NUM_NODES]
    nums = insertion_order(nums)

    for speed, num in zip([1, 1, 1, 1, 2, 3, 6] + [20] * len(nums), nums):
        s.player << flash_text(f"insert({num})", tree.insert(num)).set_speed(speed)

    for num in [23, 41]:
        s.player << flash_text(f"find({num})", tree.find(num))

    FIND = False
    NO_FIND = True
    for find, num in zip(
        [FIND, FIND] + [NO_FIND] * NUM_NODES, [12, 11, 43, 46, 40, 39]
    ):
        s.player << flash_text(
            f"remove({num})",
            AnimationSequence(
                tree.find(num).set_speed(2) if find == FIND else None,
                tree.remove(num),
            ),
        )


def to_balanced_tree(sequence: Sequence[int]) -> Sequence[int]:
    sequence = sorted(sequence)
    new_sequence: list[None | int] = [None] * len(sequence)

    worklist = [(0, len(sequence), 0)]
    while worklist:
        low, high, idx = worklist.pop(0)
        if low >= high:
            continue

        mid = (low + high) // 2

        new_sequence[idx] = sequence[mid]

        worklist.extend([(low, mid, (idx + 1) * 2 - 1), (mid + 1, high, (idx + 1) * 2)])

    for s in new_sequence:
        if s is None:
            raise RuntimeError("Should not happen")
    return new_sequence  # type: ignore


def insertion_order(sequence: Sequence[int]) -> Sequence[int]:
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


_T = TypeVar("_T")


class BTNode(Generic[_T]):
    def __init__(self, tree: "AnimatedBinaryTree", value: _T):
        self.value = value
        self._children: list[Optional["BTNode[_T]"]] = [None, None]
        self._parent: Optional["BTNode[_T]"] = None
        self._tree = tree

    def __getitem__(self, index: int) -> Optional["BTNode[_T]"]:
        return self._children[index] if index in range(len(self._children)) else None

    def __setitem__(self, index: int, value: Optional["BTNode[_T]"]):
        if index not in range(len(self._children)):
            raise IndexError("Index out of range")
        if value is not None and self._tree is not value._tree:
            raise ValueError("Cannot set a node from a different tree as a child")
        if value and self.has_ancestor(value):
            raise ValueError("Cannot set a node as a child of one of its descendants")

        old_child = self._children[index]
        if old_child is not None:
            old_child._parent = None

        self._children[index] = value
        if value is not None:
            if value._parent is not None:
                value[value.index(self)] = None
            value._parent = self

    def swap(self, other: "BTNode[_T]"):
        if self._tree != other._tree:
            raise ValueError("Cannot swap nodes from different trees")
        if not self.connected_to_root or not other.connected_to_root:
            raise ValueError("Both nodes must be connected to the root")
        if self is other:
            raise ValueError("Cannot swap a node with itself")

        if self._tree.root is self:
            self._tree.root = other
        elif self._tree.root is other:
            self._tree.root = self

        self._parent, other._parent
        if self._parent:
            self._parent._children[self._parent.index(self)] = other
        if other._parent:
            other._parent._children[other._parent.index(other)] = self
        self._parent, other._parent = other._parent, self._parent

        for child in filter(None, self._children):
            child._parent = other
        for child in filter(None, other._children):
            child._parent = self

        self._children, other._children = other._children, self._children

    def index(self, child: "BTNode[_T]") -> int:
        """The index of a child node"""
        if self.left is child:
            return 0
        elif self.right is child:
            return 1
        else:
            raise ValueError(f"{child} is not a child of {self}")

    @property
    def connected_to_root(self) -> bool:
        node = self
        while node._parent is not None:
            node = node._parent
        return node is self._tree.root

    def has_ancestor(self, other: "BTNode[_T]") -> bool:
        node = self
        while node is not None:
            if node is other:
                return True
            node = node._parent
        return False

    @property
    def children(self):
        return list(self._children)

    @property
    def left(self) -> Optional["BTNode[_T]"]:
        return self[0]

    @left.setter
    def left(self, other: Optional["BTNode[_T]"]):
        self[0] = other

    @property
    def right(self) -> Optional["BTNode[_T]"]:
        return self[1]

    @right.setter
    def right(self, other: Optional["BTNode[_T]"]):
        self[1] = other

    @property
    def parent(self) -> Optional["BTNode[_T]"]:
        return self._parent

    def detach_from_parent(self) -> Self:
        if self._parent is not None:
            self._parent[self._parent.index(self)] = None
        return self

    def set_left(self, other: Optional["BTNode[_T]"]) -> Self:
        self.left = other
        return self

    def set_right(self, other: Optional["BTNode[_T]"]) -> Self:
        self.right = other
        return self

    def __str__(self) -> str:
        return f"BTNode({self.value})"

    def __repr__(self) -> str:
        return str(self)


class BTDrawable(Circle, Generic[_T]):
    def __init__(self, node: BTNode[_T], radius: float = RADIUS):
        super().__init__(radius=radius)
        self._node = node
        self.add_child(Text(str(node.value), font_size=radius))

    def __str__(self) -> str:
        return f"BTDrawable({self._node.value})"

    def __repr__(self) -> str:
        return str(self)


class AnimatedBinaryTree(AnimatedCollection[BTNode[_T], BTDrawable], TransformMixin):
    def __init__(
        self,
        *,
        num_levels: int,
        radius: int,
        level_heights: float | None = None,
        node_width: float | None = None,
    ):
        self._radius = radius
        self._level_heights = level_heights or 3 * radius
        self._node_width = node_width or 3 * radius

        self._root = None

        self._drawable_map: dict[BTNode[_T], BTDrawable[_T]] = {}

        self._organizer = BinaryTreeOrganizer(
            num_levels=num_levels,
            level_heights=self._level_heights,
            node_width=self._node_width,
        )
        self._edges = connector.Edges()

        super().__init__()

        self.add_auxiliary_drawable(self._edges)

    def connect(
        self,
        a: BTNode[_T],
        b: BTNode[_T],
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        return self._edges.connect(
            self.drawable_for(a), self.drawable_for(b), duration=duration
        )

    def disconnect(
        self,
        a: BTNode[_T],
        b: BTNode[_T],
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        return self._edges.disconnect(
            self.drawable_for(a), self.drawable_for(b), duration=duration
        )

    def connected(
        self,
        a: BTNode[_T],
        b: BTNode[_T],
    ) -> bool:
        return self._edges.connected(self.drawable_for(a), self.drawable_for(b))

    def connect_all(self) -> Animation:
        connections: set[tuple[BTDrawable, BTDrawable]] = set()
        worklist = [self.root] if self.root else []
        while worklist:
            node = worklist.pop(0)
            if node.left:
                connections.add((self.drawable_for(node), self.drawable_for(node.left)))
                worklist.append(node.left)
            if node.right:
                connections.add(
                    (self.drawable_for(node), self.drawable_for(node.right))
                )
                worklist.append(node.right)
        return self._edges.connect_by_rule(
            lambda a, b: (a, b) in connections or (b, a) in connections,
            self.node_drawables,
        )

    def disconnect_all(self):
        return self._edges.connect_by_rule(lambda a, b: False, self.node_drawables)

    @property
    def root(self) -> Optional[BTNode[_T]]:
        return self._root

    @root.setter
    def root(self, value: Optional[BTNode[_T]]):
        self._root = value

    def Node(self, value: _T) -> BTNode[_T]:
        """Create a new node in the tree with the given value.
        Its drawable can be accessed with `drawable_for`."""
        node = BTNode(self, value)
        self.set_drawable_for(
            node,
            BTDrawable(node, radius=self._radius).translate(self.transform.translation),
        )
        return node

    def delete_node(self, node: BTNode[_T]) -> BTDrawable[_T]:
        """Removes a node from this Tree,
        setting its children's parents to None and its parent's child pointer to None.
        The drawable for this node is removed from this :class:`AnimatedCollection`'s
        display and is returned"""

        for i in range(len(node.children)):
            if node[i]:
                node[i] = None

        if node.parent:
            node.parent[node.parent.index(node)] = None

        drawable = self._drawable_map[node]
        del self._drawable_map[node]
        return drawable

    def set_transform(self, transform: Transform.TransformLike) -> Self:
        super().set_transform(transform)
        self._organizer.set_transform(transform)
        return self

    def drawable_for(self, node: BTNode[_T]) -> BTDrawable[_T]:
        if node not in self._drawable_map:
            raise ValueError(f"{node} not in tree")
        return self._drawable_map[node]

    def set_drawable_for(self, node: BTNode[_T], drawable: BTDrawable[_T]):
        self._drawable_map[node] = drawable

    def target_for(self, node: BTNode[_T]) -> Transform:
        index = self._index_of(node)
        return self._organizer[index]

    def __iter__(self):
        """Level-order traversal of the binary tree."""
        worklist = [self.root] if self.root else []
        while worklist:
            node = worklist.pop(0)
            yield node
            if node.left:
                worklist.append(node.left)
            if node.right:
                worklist.append(node.right)

    def _index_of(self, node: BTNode[_T]) -> int:
        """The organizer index for a node in the tree"""
        worklist = [(self.root, 0)] if self.root else []
        while worklist:
            node_, index = worklist.pop(0)
            if node_ is node:
                return index
            if node_.left:
                worklist.append((node_.left, (index + 1) * 2 - 1))
            if node_.right:
                worklist.append((node_.right, (index + 1) * 2))
        raise ValueError(f"{node} not in tree")

    @property
    def node_drawables(self):
        return list(self._drawable_map.values())

    @property
    def all_drawables(self):
        yield from self.auxiliary_drawables
        yield from self.node_drawables


class AnimatedBinarySearchTree(AnimatedBinaryTree[int]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert(self, value: int) -> Animation:
        new_node = self.Node(value)
        new_node_drawable = self.drawable_for(new_node).set_opacity(0.0)
        if self.root is None:
            self.root = new_node
            return AnimationBundle(
                OpacityAnimation(new_node_drawable, 1.0),
                TransformAnimation(
                    new_node_drawable.transform, self.target_for(new_node)
                ),
            )
        current = self.root
        path = [current]
        while True:
            if value < current.value:
                if current.left is None:
                    current.left = new_node
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right
            path.append(current)

        return AnimationSequence(
            OpacityAnimation(
                new_node_drawable.translate(
                    self.transform.translation + UP * self._radius * 3
                ),
                1.0,
            ),
            *map(lambda n: self._compare("<", new_node, n), path),
            AnimationBundle(
                self.connect(current, new_node),
                TransformAnimation(
                    new_node_drawable.transform, self.target_for(new_node)
                ),
            ),
        )

    def find(self, value: int) -> Animation:
        SMALL = 0
        EQUAL = 1
        LARGE = 2
        current = self.root
        path: list[tuple[BTNode[int], int]] = []
        while current:
            if value == current.value:
                path.append((current, EQUAL))
                break
            elif value < current.value:
                path.append((current, SMALL))
                current = current.left
            else:
                path.append((current, LARGE))
                current = current.right

        FOUND = current is not None

        magnifying_glass = (
            self._magnifying_glass()
            .set_opacity(0.0)
            .translate(
                self.transform.translation
                + UP * self._radius * 2
                + RIGHT * self._radius
            )
        )

        self.add_auxiliary_drawable(magnifying_glass)

        def small():
            arrow = Text("← too big", font_size=self._radius).set_opacity(0.0)
            return AnimationSequence(
                RunFunction(
                    magnifying_glass.add_child,
                    lambda p: arrow.set_anchor(Anchor.TOP).translate(
                        p.ushape.bottom * 1.25 + RIGHT * self._radius
                    ),
                ),
                AnimationBundle(
                    AnimationSequence(
                        OpacityAnimation(arrow, 1.0, duration=0.5),
                        OpacityAnimation(arrow, 0.0, duration=0.5),
                    ),
                    TranslationAnimation(
                        arrow.transform,
                        arrow.lazy.transform.translation + LEFT * self._radius * 2,
                    ),
                ),
                RunFunction(magnifying_glass.remove_child, arrow),
            )

        def large():
            arrow = Text("too small →", font_size=self._radius).set_opacity(0.0)
            return AnimationSequence(
                RunFunction(
                    magnifying_glass.add_child,
                    lambda p: arrow.set_anchor(Anchor.TOP).translate(
                        p.ushape.bottom * 1.25 + LEFT * self._radius
                    ),
                ),
                AnimationBundle(
                    AnimationSequence(
                        OpacityAnimation(arrow, 1.0, duration=0.5),
                        OpacityAnimation(arrow, 0.0, duration=0.5),
                    ),
                    TranslationAnimation(
                        arrow.transform,
                        arrow.lazy.transform.translation + RIGHT * self._radius * 2,
                    ),
                ),
                RunFunction(magnifying_glass.remove_child, arrow),
            )

        def equal(n: BTNode[int]):
            check = Text("✓", font_size=self._radius).set_opacity(0.0)
            return AnimationSequence(
                RunFunction(
                    magnifying_glass.add_child,
                    lambda p: check.set_anchor(Anchor.TOP).translate(
                        p.ushape.bottom * 1.25
                    ),
                ),
                AnimationBundle(
                    flash(self.drawable_for(n).stroke, "green"),
                    AnimationSequence(
                        OpacityAnimation(check, 1.0, duration=0.5),
                        OpacityAnimation(check, 0.0, duration=0.5),
                    ),
                ),
                RunFunction(magnifying_glass.remove_child, check),
            )

        return AnimationSequence(
            AnimationBundle(OpacityAnimation(magnifying_glass, 1.0)),
            *map(
                lambda n: AnimationSequence(
                    TransformAnimation(
                        magnifying_glass.transform, self.drawable_for(n[0]).transform
                    ),
                    small() if n[1] == SMALL else None,
                    equal(n[0]) if n[1] == EQUAL else None,
                    large() if n[1] == LARGE else None,
                ),
                path,
            ),
            AnimationSequence(
                TranslationAnimation(
                    magnifying_glass.transform,
                    magnifying_glass.lazy.transform.translation
                    + DOWN * self._radius * 3,
                ),
                RgbAnimation(magnifying_glass.stroke, "red", duration=0.5),
            )
            if not FOUND
            else None,
            OpacityAnimation(magnifying_glass, 0.0),
            RunFunction(self.remove_auxiliary_drawable, magnifying_glass),
        )

    def remove(self, value: int) -> Animation:
        sequence = AnimationSequence()

        node = self.root
        find_path = []
        while node:
            if value == node.value:
                break
            elif value < node.value:
                find_path.append(node)
                node = node.left
            else:
                find_path.append(node)
                node = node.right
        if node is None:
            raise ValueError(f"Value {value} not found in tree")

        sequence.push(RgbAnimation(self.drawable_for(node).stroke, "red"))

        swap_path: list[BTNode[int]] = []
        if node.left and node.right:
            successor = node.left
            swap_path.append(successor)
            while successor.right:
                successor = successor.right
                swap_path.append(successor)

            sequence.push(
                [
                    RgbAnimation(self.drawable_for(swap_path[0]).stroke, "blue"),
                    *map(
                        lambda n: AnimationBundle(
                            RgbAnimation(self.drawable_for(n[0]).stroke, "off_white"),
                            RgbAnimation(self.drawable_for(n[1]).stroke, "blue"),
                        ),
                        zip(swap_path, swap_path[1:]),
                    ),
                    self.swap(node, swap_path[-1]),
                    RgbAnimation(self.drawable_for(swap_path[-1]).stroke, "off_white"),
                ]
            )

        child = node.left or node.right

        if child:
            sequence.push(
                [
                    AnimationSequence(
                        RgbAnimation(self.drawable_for(child).stroke, "blue"),
                        self.swap(node, child),
                        RgbAnimation(self.drawable_for(child).stroke, "off_white"),
                    )
                ]
            )

        disconnect_animation = (
            self.disconnect(node.parent, node)
            if node.parent and self.connected(node.parent, node)
            else None
        )
        node_d = self.delete_node(node)
        self.add_auxiliary_drawable(node_d)

        return sequence.push(
            [
                AnimationBundle(
                    OpacityAnimation(node_d, 0.0),
                    disconnect_animation,
                ),
                RunFunction(self.remove_auxiliary_drawable, node_d),
            ]
        )

    def swap(self, node1: BTNode[int], node2: BTNode[int]):
        if node1 is node2:
            raise ValueError("Cannot swap a node with itself")
        if not node1.connected_to_root or not node2.connected_to_root:
            raise ValueError("Both nodes must be connected to the root")

        node1.swap(node2)

        return AnimationBundle(
            LazyAnimation(
                lambda node1=self.drawable_for(node1),
                node2=self.drawable_for(node2): quadratic_swap(
                    node1, node2, height_multiplier=1.5
                )
            ),
            self.connect_all(),
        )

    def _compare(
        self,
        operator: Literal["<", ">", "="],
        node1: BTNode[int],
        node2: BTNode[int],
    ):
        match operator:
            case "<":
                operator = "<"
                op_func = op.lt
            case ">":
                operator = ">"
                op_func = op.gt
            case "=":
                operator = "="
                op_func = op.eq
            case _:
                raise ValueError(f"Invalid operator: {operator}")

        if op_func(node1.value, node2.value):
            color = "green"
            text = "✓"
        else:
            color = "red"
            text = "X"

        drawable1, drawable2 = self.drawable_for(node1), self.drawable_for(node2)

        cmp_text = (
            Text(f"{operator}", font_size=drawable2.shape.height)
            .set_anchor(Anchor.RIGHT)
            .set_fill(color)
            .translate(drawable2.shape.left + LEFT * 0.35 * drawable2.shape.width)
            .add_child(
                lambda p: Text(text, font_size=drawable2.ushape.height / 2)
                .set_anchor(Anchor.BOTTOM)
                .set_fill(color)
                .translate(p.ushape.top * 1.25)
            )
        ).set_opacity(0.0)

        self.add_auxiliary_drawable(cmp_text)

        return AnimationSequence(
            AnimationBundle(
                TranslationAnimation(
                    drawable1.transform,
                    drawable2.shape.left + LEFT * (drawable1.shape.width) * 1.5,
                ),
                ScaleAnimation(drawable1.transform, 0.75),
            ),
            fade_in(cmp_text),
            NoAnimation(),
            RunFunction(lambda: self.remove_auxiliary_drawable(cmp_text)),
        )

    @staticmethod
    def _magnifying_glass(radius=2 * RADIUS, length=2 * RADIUS):
        unit = Vec2(math.cos(math.pi * 3 / 8), math.sin(math.pi * 3 / 8))

        start = radius * unit
        end = (radius + length) * unit

        return (
            Circle(radius=radius)
            .add_child(Drawing(path=Path().M(*start).L(*end)))
            .set_fill(Color("white", opacity=0.0125))
        )


if __name__ == "__main__":
    main()
