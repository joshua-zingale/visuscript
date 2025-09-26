from .base_class import VisuscriptTestCase
from visuscript.animation import (
    Animation,
    run,
    sequence,
    AnimationBundle,
    animate_transform,
    animate_translation,
    animate_scale,
    animate_rotation,
)
from visuscript.property_locker import PropertyLocker, LockedPropertyError
from visuscript import Transform, Circle
from visuscript.lazy_object import Lazible
from visuscript.config import config
from visuscript.primatives import Vec2


class TestRun(VisuscriptTestCase):
    class Incrementer:
        val = 0

        def increment(self):
            self.val += 1

    def test_function_called_once_and_on_advance(self):
        x = self.Incrementer()
        animation = run(x.increment)
        self.assertEqual(x.val, 0)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)


class TestAnimationSequence(VisuscriptTestCase):
    def test_sequence_duration(self):
        seq = sequence(
            MockAnimation(13),
            MockAnimation(15),
            MockAnimation(20),
            MockAnimation(0),
        )
        self.assertEqual(number_of_frames(seq), 13 + 15 + 20)

    def test_locker_conflicts(self):
        sequence(
            MockAnimation(13, locked={None: ["strawberry"]}),
            MockAnimation(15, locked={None: ["strawberry"]}),
            MockAnimation(20, locked={None: ["shortcake"]}),
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
        self.assertRaises(
            LockedPropertyError,
            lambda: AnimationBundle(
                MockAnimation(13, locked={obj: ["strawberry"]}),
                MockAnimation(15, locked={obj: ["strawberry"]}),
                MockAnimation(20, locked={obj: ["shortcake"]}),
            ),
        )

        self.assertRaises(
            LockedPropertyError,
            lambda: AnimationBundle(
                MockAnimation(13, locked={obj: ["strawberry"]}),
                sequence(
                    MockAnimation(20, locked={obj: ["shortcake"]}),
                    MockAnimation(15, locked={obj: ["strawberry"]}),
                ),
            ),
        )

        AnimationBundle(
            MockAnimation(13, locked={obj: ["straw"]}),
            MockAnimation(15, locked={obj: ["berry"]}),
            MockAnimation(20, locked={obj: ["shortcake"]}),
        )

        AnimationBundle(
            MockAnimation(13, locked={obj: ["strawberry"]}),
            sequence(
                MockAnimation(20, locked={obj: ["shortcake"]}),
                MockAnimation(15, locked={obj: ["shortcake"]}),
            ),
        )


class Testanimate_translation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = animate_translation(obj, Vec2(1, 1), duration=2)
        self.assertEqual(obj.translation, Vec2(0, 0))
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.translation, Vec2(0.5, 0.5))
        run_for(animation, 1)
        self.assertEqual(obj.translation, Vec2(1, 1))

    def test_conflict(self):
        obj = Transform()

        animation1 = animate_translation(obj, Vec2(1, 1), duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = animate_translation(obj, Vec2(2, 2), duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class Testanimate_scale(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = animate_scale(obj, Vec2(3, 2), duration=2)
        self.assertEqual(obj.scale, Vec2(1, 1))
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.scale, Vec2(2, 1.5))
        run_for(animation, 1)
        self.assertEqual(obj.scale, Vec2(3, 2))

    def test_conflict(self):
        obj = Transform()

        animation1 = animate_scale(obj, Vec2(3, 2), duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = animate_scale(obj, Vec2(3, 2), duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class Testanimate_rotation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = animate_rotation(obj, 180, duration=2)
        self.assertEqual(obj.rotation, 0)
        run_for(animation, 1)
        self.assertAlmostEqual(obj.rotation, 90)
        run_for(animation, 1)
        self.assertEqual(obj.rotation, 180)

    def test_conflict(self):
        obj = Transform()

        animation1 = animate_rotation(obj, 180, duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = animate_rotation(obj, 180, duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class Testanimate_transform(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = animate_transform(
            obj,
            Transform(translation=Vec2(1, 1), scale=Vec2(3, 2), rotation=180),
            duration=2,
        )
        self.assertEqual(obj.translation, Vec2(0, 0))
        self.assertEqual(obj.scale, Vec2(1, 1))
        self.assertEqual(obj.rotation, 0)
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.translation, Vec2(0.5, 0.5))
        self.assertVecAlmostEqual(obj.scale, Vec2(2, 1.5))
        self.assertAlmostEqual(obj.rotation, 90)
        run_for(animation, 1)
        self.assertEqual(obj.translation, Vec2(1, 1))
        self.assertEqual(obj.scale, Vec2(3, 2))
        self.assertEqual(obj.rotation, 180)

    def test_conflict(self):
        obj = Transform()

        animation1 = animate_transform(
            obj,
            Transform(translation=Vec2(1, 1), scale=Vec2(3, 2), rotation=180),
            duration=2,
        )
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = animate_translation(obj, Vec2(2, 2), duration=2)

        animation3 = animate_scale(obj, Vec2(2, 2), duration=2)

        animation4 = animate_rotation(obj, 180, duration=2)

        animation5 = animate_transform(
            obj,
            Transform(translation=Vec2(1, 1), scale=Vec2(3, 2), rotation=180),
            duration=2,
        )

        def conflict1():
            locker.update(animation2.locker)

        def conflict2():
            locker.update(animation3.locker)

        def conflict3():
            locker.update(animation4.locker)

        def conflict4():
            locker.update(animation5.locker)

        self.assertRaises(LockedPropertyError, conflict1)
        self.assertRaises(LockedPropertyError, conflict2)
        self.assertRaises(LockedPropertyError, conflict3)
        self.assertRaises(LockedPropertyError, conflict4)


class TestFades(VisuscriptTestCase):
    def test_fade_in(self):
        from visuscript.animation import fade_in

        circle = Circle(5).set_opacity(0.0)

        animation = fade_in(circle, duration=2)
        self.assertEqual(circle.opacity, 0)
        run_for(animation, 1)

        self.assertAlmostEqual(circle.opacity, 0.5)

        run_for(animation, 1)
        self.assertEqual(circle.opacity, 1)

    def test_fade_out(self):
        from visuscript.animation import fade_out

        circle = Circle(5)

        animation = fade_out(circle, duration=2)
        self.assertEqual(circle.opacity, 1)
        run_for(animation, 1)

        self.assertAlmostEqual(circle.opacity, 0.5)

        run_for(animation, 1)
        self.assertEqual(circle.opacity, 0)


    


def run_for(animation: Animation, duration: int):
    total_frames = config.fps * duration
    for _ in range(total_frames):
        animation.advance()


def number_of_frames(animation: Animation):
    num_frames = 0
    while animation.next_frame():
        num_frames += 1
    return num_frames


class MockObject(Lazible):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockAnimation(Animation):
    actual_advaces = 0
    total_advances = 0

    def __init__(
        self,
        total_advances,
        obj: list[int] = [0],
        adder: int = 1,
        locked: dict[object, list[str]] = dict(),
    ):
        super().__init__()
        self.actual_advances = 0
        self.total_advances = total_advances
        self.obj = obj
        self.obj_value = obj[0]
        self.adder = adder
        self.__locker__ = PropertyLocker(locked) # type: ignore

    def advance(self):
        self.actual_advances += 1
        if self.actual_advances > self.total_advances:
            return False
        self.obj[0] = self.obj_value + self.adder
        return True