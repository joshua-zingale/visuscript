from .base_class import VisuscriptTestCase
from visuscript.text import Text
from visuscript.animated_collection import AnimatedArray, Var
from visuscript.animation import AnimationSequence
from visuscript.element import Rect

from .test_animation import run_for

import math

class TestAnimatedList(VisuscriptTestCase):
    def test_quadratic_swap_start_and_end(self):
        data = list(map(Var, [1,2,3,4,5]))
        array = AnimatedArray(data, 20)

        loc1 = array.elements[0].transform.translation
        loc2 = array.elements[-1].transform.translation

        array.quadratic_swap(0,-1).finish()

        self.assertEqual(array[0], data[-1])
        self.assertEqual(array[-1], data[0])

        self.assertVecAlmostEqual(array.elements[0].transform.translation, loc1)
        self.assertVecAlmostEqual(array.elements[-1].transform.translation, loc2)


    def test_quadratic_swap_animation(self):


        data = list(map(Var, [1,2,3,4,5]))
        array = AnimatedArray(data, 20)

        loc1 = array.elements[0].transform.translation
        loc2 = array.elements[-1].transform.translation

        animation = array.quadratic_swap(0,-1, duration=2)

        self.assertVecAlmostEqual(array.elements[0].transform.translation, loc2)
        self.assertVecAlmostEqual(array.elements[-1].transform.translation, loc1)

        run_for(animation, 1)

        self.assertAlmostEqual(array.elements[0].transform.translation.x, (loc1.x + loc2.x)/2)
        self.assertAlmostEqual(array.elements[-1].transform.translation.x, (loc1.x + loc2.x)/2)
        self.assertGreaterEqual(array.elements[1].global_shape.bottom.y, array.elements[0].global_shape.top.y)


        run_for(animation, 1)

        self.assertEqual(array[0], data[-1])
        self.assertEqual(array[-1], data[0])

        self.assertVecAlmostEqual(array.elements[0].transform.translation, loc1)
        self.assertVecAlmostEqual(array.elements[-1].transform.translation, loc2)
        




class TestAnimatedArray(VisuscriptTestCase):

    def test_array_creation(self):
        data = list(map(Var, [0,1,2,3,4,5]))
        array = AnimatedArray(data, len(data))
        
        self.assertEqual(len(array), len(data))
        self.assertEqual(len(array.elements), len(data))
        self.assertGreaterEqual(len(get_elements_of_type(array.auxiliary_elements, Rect)), len(data))

        for val, array_val in zip(data, array):
            self.assertEqual(val, array_val)

        last_x = -math.inf
        y = array.elements[0].transform.translation.y
        for element in array.elements:
            self.assertIsInstance(element, Text)
            self.assertGreater(element.transform.translation.x, last_x)
            self.assertEqual(element.transform.translation.y, y)
            last_x = element.transform.translation.x



    def test_reverse(self):
        data = list(map(Var, [0,1,2,3,4,5]))
        array = AnimatedArray(data, len(data))

        sequence = AnimationSequence()
        for i, j in zip(range(0,len(array)//2), range(len(array)-1, len(array)//2-1, -1)):
            sequence << array.quadratic_swap(i,j)
        
        sequence.finish()

        for val, array_val in zip(reversed(data), array):
            self.assertEqual(val, array_val)


def get_elements_of_type(elements, type_):
    return list(filter(lambda x: isinstance(x, type_), elements))
