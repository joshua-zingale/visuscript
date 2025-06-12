from .base_class import VisuscriptTestCase
from visuscript.animation import (
    Animation,
    RunFunction,
    AnimationSequence,
    AnimationBundle
    )
from visuscript._property_locker import PropertyLocker, LockedPropertyError
class TestAnimation(VisuscriptTestCase):
    def test_set_speed_number_of_advances(self):
        for speed in [1,2,10,11]:
            animation = MockAnimation(17).set_speed(speed)
            self.assertAlmostEqual(int(animation.total_advances/speed), number_of_frames(animation), msg=f"speed={speed}")

    def test_finish(self):
        animation = MockAnimation(13)
        animation.finish()
        self.assertFalse(animation.advance())

    def test_compress(self):
        animation = MockAnimation(13).compress()
        self.assertTrue(animation.advance())
        self.assertFalse(animation.advance())

    def test_lazy(self):
        arr = [3]
        x = 1
        adder = lambda: x
        animation = MockAnimation.lazy(13, obj=arr, adder=adder())
        arr[0] = 1
        x = 90
        animation.finish()
        self.assertEqual(arr[0], 2)


class TestRunFunction(VisuscriptTestCase):
    class Incrementer:
            val = 0
            def increment(self):
                self.val += 1

    def test_function_called_once_and_on_advance(self):
        x = self.Incrementer()
        animation = RunFunction(x.increment)
        self.assertEqual(x.val,0)


        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)


    def test_consume_frame(self):
        x = self.Incrementer()
        animation = RunFunction(x.increment, consume_frame=True)
        self.assertEqual(x.val,0)

        self.assertTrue(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

class TestAnimationSequence(VisuscriptTestCase):
    def test_sequence_duration(self):
        sequence = AnimationSequence(
            MockAnimation(13),
            MockAnimation(15),
            MockAnimation(20),
            MockAnimation(0),
        )
        self.assertEqual(number_of_frames(sequence), 13+15+20)

    def test_locker_conflicts(self):
        AnimationSequence(
            MockAnimation(13, locked={None:['strawberry']}),
            MockAnimation(15,locked={None:['strawberry']}),
            MockAnimation(20,locked={None:['shortcake']}),
        )

class TestAnimationBundle(VisuscriptTestCase):
    def test_bundle_duration(self):
        bundle = AnimationBundle(
            MockAnimation(13),
            MockAnimation(15),
            MockAnimation(20),
            MockAnimation(0),
        )
        self.assertEqual(number_of_frames(bundle), 20)

    def test_locker_conflicts(self):
        obj = object()
        self.assertRaises(LockedPropertyError,
            lambda:AnimationBundle(
                MockAnimation(13, locked={obj:['strawberry']}),
                MockAnimation(15,locked={obj:['strawberry']}),
                MockAnimation(20,locked={obj:['shortcake']}),
            ))
        
        self.assertRaises(LockedPropertyError,
            lambda:AnimationBundle(
                MockAnimation(13, locked={obj:['strawberry']}),
                AnimationSequence(
                    MockAnimation(20,locked={obj:['shortcake']}),
                    MockAnimation(15,locked={obj:['strawberry']}),
                )
            ))
        
        AnimationBundle(
            MockAnimation(13, locked={obj:['straw']}),
            MockAnimation(15,locked={obj:['berry']}),
            MockAnimation(20,locked={obj:['shortcake']}),
        )

        AnimationBundle(
            MockAnimation(13, locked={obj:['strawberry']}),
            AnimationSequence(
                MockAnimation(20,locked={obj:['shortcake']}),
                MockAnimation(15,locked={obj:['shortcake']}),
            )
        )

def number_of_frames(animation: Animation):
    num_frames = 0
    while animation.next_frame():
        num_frames += 1
    return num_frames

class MockAnimation(Animation):
    def __init__(self, total_advances, obj: list[int] = [0], adder: int = 1, locked: dict[object, list[str]] = dict()):
        super().__init__()
        self.actual_advances = 0
        self.total_advances = total_advances
        self.obj = obj
        self.obj_value = obj[0]
        self.adder = adder
    def advance(self):
        self.actual_advances += 1
        if self.actual_advances > self.total_advances:
            return False
        self.obj[0] = self.obj_value + self.adder
        return True
    def init_locker(self, total_advances, obj: list[int] = [0], adder: int = 1, locked: dict[object, list[str]] = dict()):
        return PropertyLocker(locked)

