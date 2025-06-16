from .base_class import VisuscriptTestCase
from visuscript.text import Text
from visuscript.animated_collection import AnimatedArray, Var
from visuscript.animation import AnimationSequence
from visuscript.canvas import Scene
from visuscript.element import Rect
import math
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
