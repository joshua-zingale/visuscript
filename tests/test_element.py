from .base_class import VisuscriptTestCase
from visuscript.mixins import Element
from visuscript.primatives import Vec2


class TestElement(VisuscriptTestCase):
    class MockElement(Element):
        def __init__(self, width, height, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._width = width
            self._height = height

        def calculate_top_left(self):
            return Vec2(0, 0)

        def calculate_width(self):
            return self._width

        def calculate_height(self):
            return self._height

        def draw_self(self):
            return ""

    def test_initialization(self):
        element = self.MockElement(10, 10)

    def test_iteration(self):
        parent = self.MockElement(10, 10)
        children = [self.MockElement(10, 10) for _ in range(3)]
        parent.add_child(children[0])
        parent.add_children(*children[1:])

        self.assertIn(parent, parent)
        for child in children:
            self.assertIn(child, parent)

    def test_functional_add_children(self):
        parent = self.MockElement(10, 10)
        child = self.MockElement(10, 10)
        parent.add_child(lambda p: child.translate(*p.ushape.bottom_right))
        self.assertVecAlmostEqual(
            child.transform.translation, parent.ushape.bottom_right
        )
        self.assertTrue(child in parent)

        children = [self.MockElement(10, 10) for _ in range(5)]
        parent.add_child(
            lambda p: (
                child.translate(*p.ushape.right + Vec2(10 * i, 0))
                for i, child in enumerate(children)
            )
        )
        self.assertSetEqual(set(children).union(child), set(parent.iter_children()))
        for i, child in enumerate(children):
            self.assertVecAlmostEqual(
                child.transform.translation,
                parent.ushape.right + Vec2(10 * i, 0),
            )

    def test_children_have_parent(self):
        parent1 = self.MockElement(10, 10)
        parent2 = self.MockElement(10, 10)
        children = [self.MockElement(10, 10) for _ in range(3)]
        parent1.add_child(children[0])
        parent1.add_children(*children[1:])

        self.assertSetEqual(set(parent1.iter_children()), set(children))

        for child in children:
            self.assertIs(child.parent, parent1)

        children[0].set_parent(parent2)
        self.assertIs(children[0].parent, parent2)

        self.assertSetEqual(set(parent1.iter_children()), set(children[1:]))
        for child in children[1:]:
            self.assertIs(child.parent, parent1)

        children[0].set_parent(None)
        self.assertIs(children[0].parent, None)

        self.assertEqual(len(list(parent2.iter_children())), 0)

    def test_relative_position(self):
        parent = self.MockElement(10, 10)
        child1 = self.MockElement(10, 10)
        child2 = self.MockElement(10, 10)
        parent.add_child(child1)
        parent.add_child(child2.translate(-100))

        parent.translate(100)
        child1.translate(0, 100)
        self.assertVecAlmostEqual(child1.transform.translation, Vec2(0, 100))
        self.assertVecAlmostEqual(child2.transform.translation, Vec2(-100, 0))
        self.assertVecAlmostEqual(parent.transform.translation, Vec2(100, 0))

        self.assertVecAlmostEqual(child1.global_transform.translation, Vec2(100, 100))
        self.assertVecAlmostEqual(child2.global_transform.translation, Vec2(0, 0))
        self.assertVecAlmostEqual(parent.transform.translation, Vec2(100, 0))

    def test_global_position(self):
        parent = self.MockElement(10, 10)
        child = self.MockElement(10, 10)
        parent.add_child(child)

        parent.translate(100)
        self.assertVecAlmostEqual(child.global_transform.translation, Vec2(100, 0))

        child.translate(0, 100)
        self.assertVecAlmostEqual(child.global_transform.translation, Vec2(100, 100))
        self.assertVecAlmostEqual(parent.global_transform.translation, Vec2(100, 0))
