from .base_class import VisuscriptTestCase
from visuscript.animation import (
    Animation,
    RunFunction,
    AnimationSequence,
    AnimationBundle,
    PropertyAnimation,
    TransformAnimation,
    TranslationAnimation,
    ScaleAnimation,
    RotationAnimation,
)
from visuscript.property_locker import PropertyLocker, LockedPropertyError
from visuscript import (
    Transform,
    Vec3,
    Color,
    Rgb,
    Circle
    )
from visuscript.lazy_object import Lazible
from visuscript.config import config
from visuscript.primatives import Vec

class TestAnimation(VisuscriptTestCase):
    def test_set_speed_number_of_advances(self):
        for speed in [1, 2, 10, 11]:
            animation = MockAnimation(17).set_speed(speed)
            self.assertAlmostEqual(
                int(animation.total_advances / speed),
                number_of_frames(animation),
                msg=f"speed={speed}",
            )

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
        self.assertEqual(x.val, 0)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

        self.assertFalse(animation.advance())
        self.assertEqual(x.val, 1)

    def test_consume_frame(self):
        x = self.Incrementer()
        animation = RunFunction(x.increment, consume_frame=True)
        self.assertEqual(x.val, 0)

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
        self.assertEqual(number_of_frames(sequence), 13 + 15 + 20)

    def test_locker_conflicts(self):
        AnimationSequence(
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
                AnimationSequence(
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
            AnimationSequence(
                MockAnimation(20, locked={obj: ["shortcake"]}),
                MockAnimation(15, locked={obj: ["shortcake"]}),
            ),
        )


class TestPropertyAnimation(VisuscriptTestCase):
    def test_approach(self):
        obj = MockObject(a=Vec(0, 0), b=Vec(1, 1))

        animation = PropertyAnimation(
            obj=obj,
            destinations=[Vec(1, 1), Vec(0, 1)],
            properties=["a", "b"],
            duration=2,
            initials=[None, None],
        )
        self.assertEqual(obj.a, Vec(0, 0))
        self.assertEqual(obj.b, Vec(1, 1))
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.a, Vec(0.5, 0.5))
        self.assertVecAlmostEqual(obj.b, Vec(0.5, 1))
        run_for(animation, 1)
        self.assertEqual(obj.a, Vec(1, 1))
        self.assertEqual(obj.b, Vec(0, 1))


class TestTranslationAnimation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = TranslationAnimation(obj, Vec3(1, 1, 1), duration=2)
        self.assertEqual(obj.translation, Vec3(0, 0, 0))
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.translation, Vec(0.5, 0.5, 0.5))
        run_for(animation, 1)
        self.assertEqual(obj.translation, Vec(1, 1, 1))

    def test_conflict(self):
        obj = Transform()

        animation1 = TranslationAnimation(obj, Vec3(1, 1, 1), duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = TranslationAnimation(obj, Vec3(2, 2, 2), duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class TestScaleAnimation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = ScaleAnimation(obj, Vec3(3, 2, 1), duration=2)
        self.assertEqual(obj.scale, Vec3(1, 1, 1))
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.scale, Vec(2, 1.5, 1))
        run_for(animation, 1)
        self.assertEqual(obj.scale, Vec(3, 2, 1))

    def test_conflict(self):
        obj = Transform()

        animation1 = ScaleAnimation(obj, Vec3(3, 2, 1), duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = ScaleAnimation(obj, Vec3(3, 2, 1), duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class TestRotationAnimation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = RotationAnimation(obj, 180, duration=2)
        self.assertEqual(obj.rotation, 0)
        run_for(animation, 1)
        self.assertAlmostEqual(obj.rotation, 90)
        run_for(animation, 1)
        self.assertEqual(obj.rotation, 180)

    def test_conflict(self):
        obj = Transform()

        animation1 = RotationAnimation(obj, 180, duration=2)
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = RotationAnimation(obj, 180, duration=2)

        def conflict():
            locker.update(animation2.locker)

        self.assertRaises(LockedPropertyError, conflict)


class TestTransformAnimation(VisuscriptTestCase):
    def test_approach(self):
        obj = Transform()

        animation = TransformAnimation(
            obj,
            Transform(translation=Vec3(1, 1, 1), scale=Vec3(3, 2, 1), rotation=180),
            duration=2,
        )
        self.assertEqual(obj.translation, Vec3(0, 0, 0))
        self.assertEqual(obj.scale, Vec3(1, 1, 1))
        self.assertEqual(obj.rotation, 0)
        run_for(animation, 1)
        self.assertVecAlmostEqual(obj.translation, Vec(0.5, 0.5, 0.5))
        self.assertVecAlmostEqual(obj.scale, Vec(2, 1.5, 1))
        self.assertAlmostEqual(obj.rotation, 90)
        run_for(animation, 1)
        self.assertEqual(obj.translation, Vec(1, 1, 1))
        self.assertEqual(obj.scale, Vec3(3, 2, 1))
        self.assertEqual(obj.rotation, 180)

    def test_conflict(self):
        obj = Transform()

        animation1 = TransformAnimation(
            obj,
            Transform(translation=Vec3(1, 1, 1), scale=Vec3(3, 2, 1), rotation=180),
            duration=2,
        )
        locker = PropertyLocker()
        locker.update(animation1.locker)

        animation2 = TranslationAnimation(obj, Vec3(2, 2, 2), duration=2)

        animation3 = ScaleAnimation(obj, Vec3(2, 2, 2), duration=2)

        animation4 = RotationAnimation(obj, 180, duration=2)

        animation5 = TransformAnimation(
            obj,
            Transform(translation=Vec3(1, 1, 1), scale=Vec3(3, 2, 1), rotation=180),
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

    def test_flash(self):
        from visuscript.animation import flash

        circle = Circle(5).set_stroke(Color(Rgb(0, 0, 0)))

        animation = flash(circle.stroke, Rgb(100, 100, 100), duration=4)

        self.assertEqual(circle.stroke.rgb, Rgb(0, 0, 0))
        run_for(animation, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(50, 50, 50))
        run_for(animation, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(100, 100, 100))
        run_for(animation, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(50, 50, 50))
        run_for(animation, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(0, 0, 0))

    def test_sequence(self):
        from visuscript.animation import fade_in, fade_out, flash

        circle = Circle(5).set_stroke(Color(Rgb(50, 50, 50))).set_opacity(0.25)

        sequence = AnimationSequence(
            fade_in(circle, duration=2),
            flash(circle.stroke, Rgb(100, 100, 100), duration=4),
            fade_out(circle, duration=2),
        )

        circle.set_stroke(Color(Rgb(0, 0, 0))).set_opacity(0)

        # Fade in
        self.assertEqual(circle.opacity, 0)
        run_for(sequence, 1)
        self.assertAlmostEqual(circle.opacity, 0.5)
        run_for(sequence, 1)
        self.assertEqual(circle.opacity, 1)

        self.assertEqual(circle.stroke.rgb, Rgb(0, 0, 0))
        run_for(sequence, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(50, 50, 50))
        run_for(sequence, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(100, 100, 100))
        run_for(sequence, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(50, 50, 50))
        run_for(sequence, 1)
        self.assertEqual(circle.stroke.rgb, Rgb(0, 0, 0))

        # Fade out
        run_for(sequence, 1)

        self.assertAlmostEqual(circle.opacity, 0.5)

        run_for(sequence, 1)
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

    def advance(self):
        self.actual_advances += 1
        if self.actual_advances > self.total_advances:
            return False
        self.obj[0] = self.obj_value + self.adder
        return True

    def __init_locker__(
        self,
        total_advances,
        obj: list[int] = [0],
        adder: int = 1,
        locked: dict[object, list[str]] = dict(),
    ):
        return PropertyLocker(locked)
