import unittest
from visuscript.primatives import Vec
from visuscript.math_utility import magnitude
class VisuscriptTestCase(unittest.TestCase):

    def assertVecAlmostEqual(self, vec1: Vec, vec2: Vec, msg: str ="", delta=1e-7):
        self.assertLessEqual(magnitude(vec1 - vec2), delta, f"The magnitude difference between {vec1} and {vec2} is {magnitude(vec1 - vec2)} : " + msg)

    def assertVecNotAlmostEqual(self, vec1: Vec, vec2: Vec, msg: str = "", delta=1e-7):
        self.assertGreaterEqual(magnitude(vec1 - vec2), delta,  f"The magnitude difference between {vec1} and {vec2} is {magnitude(vec1 - vec2)} : " + msg)
