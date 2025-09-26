from .base_class import VisuscriptTestCase
from visuscript.animated_collection import AnimatedArray, Var
from visuscript import (
    Rect,
    sequence,
    Text,
)

from .test_animation import run_for

import math


class TestAnimatedList(VisuscriptTestCase):
    def test_qswap_start_and_end(self):
        data = list(map(Var, [1, 2, 3, 4, 5]))
        array = AnimatedArray(data, 20)

        loc1 = array.drawables[0].transform.translation
        loc2 = array.drawables[-1].transform.translation

        array.qswap(0, -1).finish()

        self.assertEqual(array[0], data[-1])
        self.assertEqual(array[-1], data[0])

        self.assertVecAlmostEqual(array.drawables[0].transform.translation, loc1)
        self.assertVecAlmostEqual(array.drawables[-1].transform.translation, loc2)

    def test_qswap_animation(self):
        data = list(map(Var, [1, 2, 3, 4, 5]))
        array = AnimatedArray(data, 20)

        loc1 = array.drawables[0].transform.translation
        loc2 = array.drawables[-1].transform.translation

        animation = array.qswap(0, -1, duration=2)

        self.assertVecAlmostEqual(array.drawables[0].transform.translation, loc2)
        self.assertVecAlmostEqual(array.drawables[-1].transform.translation, loc1)

        run_for(animation, 1)

        self.assertAlmostEqual(
            array.drawables[0].transform.translation.x, (loc1.x + loc2.x) / 2
        )
        self.assertAlmostEqual(
            array.drawables[-1].transform.translation.x, (loc1.x + loc2.x) / 2
        )
        self.assertLessEqual(
            array.drawables[-1].gshape.bottom.y,
            array.drawables[0].gshape.top.y,
        )

        run_for(animation, 1)

        self.assertEqual(array[0], data[-1])
        self.assertEqual(array[-1], data[0])

        self.assertVecAlmostEqual(array.drawables[0].transform.translation, loc1)
        self.assertVecAlmostEqual(array.drawables[-1].transform.translation, loc2)

    def test_qswap_sequence(self):
        data = list(map(Var, [1, 2, 3, 4, 5]))
        array = AnimatedArray(data, 20)

        loc1 = array.drawables[0].transform.translation
        loc2 = array.drawables[1].transform.translation
        loc3 = array.drawables[-1].transform.translation

        animation = sequence(
            array.qswap(0, -1, duration=1),
            array.qswap(0, 1, duration=2),
        )

        run_for(animation, 1)

        self.assertVecAlmostEqual(array.drawables[1].transform.translation, loc1)
        self.assertVecAlmostEqual(array.drawables[0].transform.translation, loc2)
        self.assertVecAlmostEqual(array.drawables[-1].transform.translation, loc3)

        run_for(animation, 1)

        self.assertAlmostEqual(
            array.drawables[0].transform.translation.x, (loc1.x + loc2.x) / 2
        )
        self.assertAlmostEqual(
            array.drawables[1].transform.translation.x, (loc1.x + loc2.x) / 2
        )
        self.assertLessEqual(
            array.drawables[1].gshape.bottom.y,
            array.drawables[0].gshape.top.y,
        )

        run_for(animation, 1)

        self.assertEqual(array[0], data[1])
        self.assertEqual(array[1], data[-1])
        self.assertEqual(array[-1], data[0])

        self.assertVecAlmostEqual(array.drawables[0].transform.translation, loc1)
        self.assertVecAlmostEqual(array.drawables[1].transform.translation, loc2)


class TestAnimatedArray(VisuscriptTestCase):
    def test_array_creation(self):
        data = list(map(Var, [0, 1, 2, 3, 4, 5]))
        array = AnimatedArray(data, len(data))

        self.assertEqual(len(array), len(data))
        self.assertEqual(len(array.drawables), len(data))
        self.assertGreaterEqual(
            len(get_drawables_of_type(array.auxiliary_drawables, Rect)), len(data)
        )

        for val, array_val in zip(data, array):
            self.assertEqual(val, array_val)

        last_x = -math.inf
        y = array.drawables[0].transform.translation.y
        for drawable in array.drawables:
            self.assertIsInstance(drawable, Text)
            self.assertGreater(drawable.transform.translation.x, last_x)
            self.assertEqual(drawable.transform.translation.y, y)
            last_x = drawable.transform.translation.x

    def test_reverse(self):
        data = list(map(Var, [0, 1, 2, 3, 4, 5]))
        array = AnimatedArray(data, len(data))

        seq = sequence()
        for i, j in zip(
            range(0, len(array) // 2), range(len(array) - 1, len(array) // 2 - 1, -1)
        ):
            seq << array.qswap(i, j)

        seq.finish()

        for val, array_val in zip(reversed(data), array):
            self.assertEqual(val, array_val)


# class TestAnimatedBinaryTreeArray(VisuscriptTestCase):
#     def test_initialization(self):
#         data = list(map(Var, [0, 1, 2, 3, 4, 5]))
#         array = AnimatedBinaryTreeArray(data, radius=10)
#         array.organize().finish()

#         for var1, var2 in zip(data, array):
#             self.assertEqual(var1, var2)

#         y = lambda i: array.drawables[i].gshape.center.y
#         x = lambda i: array.drawables[i].gshape.center.x

#         self.assertGreater(y(1), y(0))

#         self.assertEqual(y(1), y(2))
#         self.assertEqual(y(3), y(4))
#         self.assertEqual(y(3), y(5))

#         self.assertGreater(x(0), x(1))
#         self.assertLess(x(0), x(2))

#         self.assertGreater(x(1), x(3))
#         self.assertLess(x(1), x(4))

#         self.assertLess(x(4), x(5))

#         self.assertGreater(x(2), x(5))


def get_drawables_of_type(drawables, type_):
    return list(filter(lambda x: isinstance(x, type_), drawables))
