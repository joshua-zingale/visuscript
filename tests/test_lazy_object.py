import unittest
from visuscript.lazy_object import *


class TestLazyObject(unittest.TestCase):
    def test_attribute_evaluation_correctness(self):
        obj = A(B(A(1, 2, 3), 4), B(A(5)), 6)
        self.assertEqual(LazyObject(obj).a.b.evaluate_lazy_object(), obj.a.b)
        self.assertEqual(LazyObject(obj).a.a.a.evaluate_lazy_object(), obj.a.a.a)
        self.assertEqual(LazyObject(obj).c.evaluate_lazy_object(), obj.c)

        a = A(1, 2, 3)
        lazy_a = LazyObject(a).a
        a.a = 9
        self.assertEqual(lazy_a.evaluate_lazy_object(), 9)

    def test_attribute_error(self):
        obj = A(B(A(1, 2, 3), 4), B(A(5)), 6)
        self.assertRaises(
            AttributeError, lambda: LazyObject(obj).c.a.evaluate_lazy_object()
        )
        LazyObject(obj).c

    def test_multiple_chains(self):
        obj = A(B(A(1, 2, 3), 4), B(A(5)), 6)
        lazy_obj = LazyObject(obj)
        self.assertEqual(lazy_obj.a.b.evaluate_lazy_object(), 4)
        self.assertEqual(lazy_obj.c.evaluate_lazy_object(), 6)

    def test_calls(self):
        a = A(1)
        lazy_called_a = LazyObject(a).double_a().add_to_a(3).double_a()
        self.assertEqual(lazy_called_a.evaluate_lazy_object().a, 10)
        self.assertEqual(a.a, 10)
        a.a = 2
        self.assertEqual(lazy_called_a.evaluate_lazy_object().a, 14)
        self.assertEqual(a.a, 14)

    def test_embedded_calls(self):
        a = A(A(1, A(1, 2)))
        lazy_a_a = LazyObject(a).a.double_a().add_to_a(3).double_a()
        lazy_a_a_b = LazyObject(a).a.b.add_to_a(4)

        self.assertEqual(lazy_a_a.evaluate_lazy_object().a, 10)
        self.assertEqual(a.a.a, 10)

        self.assertEqual(lazy_a_a_b.evaluate_lazy_object().a, 5)
        self.assertEqual(a.a.b.a, 5)

        a.a.a = 2
        self.assertEqual(lazy_a_a.evaluate_lazy_object().a, 14)
        self.assertEqual(a.a.a, 14)


class A:
    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c

    def double_a(self):
        self.a *= 2
        return self

    def add_to_a(self, val):
        self.a += val
        return self


class B:
    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c
