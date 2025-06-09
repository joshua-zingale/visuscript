import unittest
from visuscript._lazy_object import *
from typing import cast
class TestLazyObject(unittest.TestCase):

    def test_attribute_evaluation_correctness(self):
        obj = A(B(A(1,2,3), 4), B(A(5)), 6)
        self.assertEqual(LazyObject(obj).a.b.evaluate_lazy_object(), obj.a.b)
        self.assertEqual(LazyObject(obj).a.a.a.evaluate_lazy_object(), obj.a.a.a)
        self.assertEqual(LazyObject(obj).c.evaluate_lazy_object(), obj.c)

        a = A(1,2,3)
        lazy_a = LazyObject(a).a
        a.a = 9
        self.assertEqual(lazy_a.evaluate_lazy_object(), 9)


        

    def test_attribute_error(self):
        obj = A(B(A(1,2,3), 4), B(A(5)), 6)
        self.assertRaises(AttributeError, lambda: LazyObject(obj).c.a)
        LazyObject(obj).c

    def test_multiple_chains(self):
        obj = A(B(A(1,2,3), 4), B(A(5)), 6)
        lazy_obj = LazyObject(obj)
        self.assertEqual(lazy_obj.a.b.evaluate_lazy_object(), 4)
        self.assertEqual(lazy_obj.c.evaluate_lazy_object(), 6)


class TestLazyInitMetaClass(unittest.TestCase):

    def test_delayed_init(self):
        a = A(1,2,3)
        b = B(4,5,6)
        d = B(a, 7, 8)
        lazy_class = LazyClass(LazyObject(d).a, b)
        self.assertEqual(lazy_class.c, a)
        self.assertEqual(lazy_class.d, b)
        self.assertRaises(AttributeError, lambda: lazy_class.a)
        self.assertRaises(AttributeError, lambda: lazy_class.b)

        lazy_class.no_activation()
        self.assertRaises(AttributeError, lambda: lazy_class.a)
        self.assertRaises(AttributeError, lambda: lazy_class.b)

        self.assertEqual(lazy_class.activate_a(1), (1, a))

        self.assertEqual(lazy_class.a, a)
        self.assertEqual(lazy_class.b, b)
        self.assertEqual(lazy_class.c, a)
        self.assertEqual(lazy_class.d, b)

    def test_delayed_init2(self):
        a = A(1,2,3)
        b = B(4,5,6)
        d = B(a, 7, 8)
        lazy_class = LazyClass(LazyObject(d).a, b)
        self.assertEqual(lazy_class.c, a)
        self.assertEqual(lazy_class.d, b)
        self.assertRaises(AttributeError, lambda: lazy_class.a)
        self.assertRaises(AttributeError, lambda: lazy_class.b)

        lazy_class.no_activation()
        self.assertRaises(AttributeError, lambda: lazy_class.a)
        self.assertRaises(AttributeError, lambda: lazy_class.b)

        self.assertEqual(lazy_class.activate_b(), b)

        self.assertEqual(lazy_class.a, a)
        self.assertEqual(lazy_class.b, b)
        self.assertEqual(lazy_class.c, a)
        self.assertEqual(lazy_class.d, b)



class A:
    def __init__(self, a=None,b=None,c=None):
        self.a = a
        self.b = b
        self.c = c
class B:
    def __init__(self, a=None,b=None,c=None):
        self.a = a
        self.b = b
        self.c = c


class LazyClass(metaclass=LazyInitMetaClass, activators=['activate_a', 'activate_b'], para_inits=['para_init1', 'para_init2']):

    def __init__(self, a: A, b: B):
        self.a = a
        self.b = b
    def para_init1(self, a: A, b : B):
        self.c = a
    def para_init2(self, a: A, b : B):
        self.d = b
    def activate_a(self, value):
        return value, self.a
    def activate_b(self):
        return self.b
    def no_activation(self):
        pass


