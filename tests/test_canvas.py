from .base_class import VisuscriptTestCase
from .test_animation import MockAnimation
from .test_updater import MockUpdater
from visuscript.config import config
from visuscript._property_locker import LockedPropertyError
from visuscript.canvas import Scene

class TestScene(VisuscriptTestCase):
    def setUp(self):
        self.mock_stream = MockStream()
        config.canvas_output_stream = self.mock_stream

    def test_animations_play(self):
        scene = Scene(print_initial=False)
        animation = MockAnimation(11)
        scene.player << animation
        self.assertGreaterEqual(animation.actual_advances, 11)
        self.assertEqual(self.mock_stream.writes, 11)
        
        animation10 = MockAnimation(10)
        animation9 = MockAnimation(9)
        with scene as s:
            s.animations << animation10
            s.animations << animation9
        self.assertEqual(self.mock_stream.writes, 21)
        self.assertGreaterEqual(animation10.actual_advances, 10)
        self.assertGreaterEqual(animation9.actual_advances, 9)

    def test_with_print_initial_animations_play(self):
        scene = Scene(print_initial=True)
        animation = MockAnimation(11)
        scene.player << animation
        self.assertGreaterEqual(animation.actual_advances, 12)
        self.assertEqual(self.mock_stream.writes, 12)
        
        animation10 = MockAnimation(10)
        animation9 = MockAnimation(9)
        with scene as s:
            s.animations << animation10
            s.animations << animation9
        self.assertEqual(self.mock_stream.writes, 22)
        self.assertGreaterEqual(animation10.actual_advances, 10)
        self.assertGreaterEqual(animation9.actual_advances, 9)


    def test_updaters_play(self):
        scene = Scene()
        updater = MockUpdater()
        scene.updaters << updater
        scene.player << MockAnimation(config.fps)
        self.assertEqual(updater.update_calls, 30)
        scene.player << MockAnimation(config.fps)
        self.assertEqual(updater.update_calls, 60)

    def test_animations_locked(self):
        scene = Scene()
        obj1 = object()
        obj2 = object()

        with scene as s:
            s.animations << MockAnimation(10, locked={obj1: ["strawberry"]})
            s.animations << MockAnimation(10, locked={obj1: ["shortcake"]})
            s.animations << MockAnimation(9, locked={obj2: ["strawberry"]})

        with scene as s:
            s.animations << MockAnimation(10, locked={obj1: ["strawberry"]})
            s.animations << MockAnimation(10, locked={obj1: ["shortcake"]})
            s.animations << MockAnimation(9, locked={obj2: ["strawberry"]})

        def conflict():
            with scene as s:
                s.animations << MockAnimation(10, locked={obj1: ["strawberry"]})
                s.animations << MockAnimation(10, locked={obj1: ["shortcake"]})
                s.animations << MockAnimation(9, locked={obj2: ["strawberry"]})
                s.animations << MockAnimation(9, locked={obj1: ["shortcake"]})

        self.assertRaises(LockedPropertyError, conflict)

    def test_updaters_locked(self):
        scene = Scene()
        obj1 = object()
        obj2 = object()

        # TODO uncomment and fix
        # with scene as s:
        #     s.updaters << MockUpdater(locked={obj1: ["strawberry"]})
        #     s.updaters << MockUpdater(locked={obj1: ["shortcake"]})
        #     s.updaters << MockUpdater(locked={obj2: ["strawberry"]})
        
        scene.updaters << MockUpdater(locked={obj1: ["strawberry"]})
        scene.updaters << MockUpdater(locked={obj1: ["shortcake"]})
        scene.updaters << MockUpdater(locked={obj2: ["strawberry"]})

        def conflict1():
            scene.updaters << MockUpdater(locked={obj1: ["shortcake"]})

        def conflict2():
            scene.updaters << MockUpdater(locked={obj2: ["strawberry"]})

        self.assertRaises(LockedPropertyError, conflict1)
        self.assertRaises(LockedPropertyError, conflict2)


    def test_animations_and_updaters_locked(self):

        scene = Scene()
        obj1 = object()
        obj2 = object()

        with scene as s:
            s.animations << MockAnimation(10, locked={obj1: ["strawberry"]})
            s.animations << MockAnimation(10, locked={obj1: ["shortcake"]})
            s.updaters << MockUpdater(locked={obj2: ["strawberry"]})
        def conflict():
            with scene as s:
                s.animations << MockAnimation(10, locked={obj1: ["strawberry1"]})
                s.updaters << MockUpdater(locked={obj1: ["shortcake1"]})

        # TODO uncomment and fix
        # self.assertRaises(LockedPropertyError, conflict)




class MockStream:
    writes = 0
    def write(self, data: str):
        self.writes += data.count("<svg xmlns=\"http://www.w3.org/2000/svg\"")