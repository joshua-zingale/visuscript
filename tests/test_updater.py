from .base_class import VisuscriptTestCase
import unittest
from visuscript.config import config
from visuscript.updater import TranslationUpdater, Updater
from visuscript.primatives import Transform
from visuscript._property_locker import PropertyLocker
from math import sqrt


class TestUpdater(VisuscriptTestCase):
    def test_consistent_time_span_with_different_update_rates(self):        
        for update_rate in [1, config.fps // 3, config.fps//2, config.fps, 60, 75, config.fps*2, config.fps*3]:
            for length in [1, 10, 12, 19, 64, 81]:
                updater = MockUpdater().set_update_rate(update_rate)
                for _ in frame_sequence(length):
                    updater.update_for_frame()
                self.assertEqual(updater.update_calls, length*update_rate, f"failed with update rate of {update_rate} and length of {length}")
                self.assertAlmostEqual(sum(updater.dts), length, msg=f"failed with update rate of {update_rate} and length of {length}")

class TestTranslationUpdater(VisuscriptTestCase):

    def test_instantaneous_movement_and_stationary_destination(self):
        locations = [[0,0], [12,11], [0,15], [32,2], [100,0], [53,24]]
        for source_loc in locations:
            for destination_loc in locations:
                source = Transform(translation=source_loc)
                destination = Transform(translation=destination_loc)
                updater = TranslationUpdater(source, destination)
                updater.update(0,1)
                self.assertVecAlmostEqual(source.translation, destination.translation)

    def test_instantaneous_movement_and_moving_destination(self):
        locations = [[0,0], [12,11], [0,15], [32,2], [100,0], [53,24]]
        for source_loc in locations:
            for destination_loc in locations:
                source = Transform(translation=source_loc)
                destination = Transform(translation=destination_loc)
                updater = TranslationUpdater(source, destination)
                for t, dt in frame_sequence(30):
                    updater.update(t,dt)
                    self.assertVecAlmostEqual(source.translation, destination.translation)

    def test_constant_velocity_toward_stationary_destination(self):
        source = Transform(translation=[0,0])
        destination = Transform(translation=[100,0])

        updater = TranslationUpdater(source, destination, max_speed=1)
        for t, dt in frame_sequence(100):
            self.assertVecNotAlmostEqual(source.translation, destination.translation)
            updater.update(t, dt)
        self.assertVecAlmostEqual(source.translation, destination.translation)

    def test_constant_velocity_toward_moving_destination(self):
        source = Transform(translation=[0,0])
        destination = Transform(translation=[100,0])
        updater = TranslationUpdater(source, destination, max_speed=2)
        for t, dt in frame_sequence(100):
            self.assertVecNotAlmostEqual(source.translation, destination.translation)
            destination.translation += [1*dt,0,0]
            updater.update(t, dt)
        self.assertVecAlmostEqual(source.translation, destination.translation)

    def test_acceleration_toward_stationary_destination(self):
        source = Transform(translation=[0,0])
        destination = Transform(translation=[100,0])
        updater = TranslationUpdater(source, destination, acceleration=1)
        for t, dt in frame_sequence(sqrt(100)):
            self.assertLessEqual(source.translation.x, 50)
            updater.update(t, dt)
        self.assertGreaterEqual(source.translation.x, 50)

    def test_set_speed_constant_acceleration_toward_stationary_destination(self):
        for update_rate in [1, config.fps // 3, config.fps//2, config.fps, 60, 75]:
            source = Transform(translation=[0,0])
            destination = Transform(translation=[100,0])
            updater = TranslationUpdater(source, destination, acceleration=1).set_update_rate(update_rate)
            for _ in frame_sequence(sqrt(100)):
                self.assertLessEqual(source.translation.x, 50, f"failed with update rate of {update_rate}")
                updater.update_for_frame()
            self.assertGreaterEqual(source.translation.x, 50, f"failed with update rate of {update_rate}")


class MockUpdater(Updater):
    def __init__(self, locked: dict[object, list[str]] = {}):
        self.update_calls = 0
        self.dts = []
        self.ts = []
        self._locker = PropertyLocker()
        for obj, properties in locked.items():
            for property in properties:
                self._locker.add(obj, property)
    @property
    def locker(self) -> PropertyLocker:
        """
        Returns a PropertyLocker identifying all objects/properties updated by this Updater.
        """
        return self._locker
    def update(self, t: float, dt: float):
        """Makes this Updater's update."""
        self.update_calls += 1
        self.dts.append(dt)
        self.ts.append(t)
        return self
        

def frame_sequence(length):
    for frame_number in range(int(config.fps*length)):
        t = frame_number/config.fps
        dt = 1/config.fps
        yield t, dt

if __name__ == '__main__':
    unittest.main()