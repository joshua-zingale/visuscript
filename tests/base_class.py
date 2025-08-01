import unittest
from visuscript.primatives import Vec2
from visuscript.math_utility import magnitude


class VisuscriptTestCase(unittest.TestCase):
    def assertVecAlmostEqual(self, vec1: Vec2, vec2: Vec2, msg: str = "", delta=1e-7):
        self.assertLessEqual(
            magnitude(vec1 - vec2),
            delta,
            f"The magnitude difference between {vec1} and {vec2} is {magnitude(vec1 - vec2)} : "
            + msg,
        )

    def assertVecNotAlmostEqual(
        self, vec1: Vec2, vec2: Vec2, msg: str = "", delta=1e-7
    ):
        self.assertGreaterEqual(
            magnitude(vec1 - vec2),
            delta,
            f"The magnitude difference between {vec1} and {vec2} is {magnitude(vec1 - vec2)} : "
            + msg,
        )
