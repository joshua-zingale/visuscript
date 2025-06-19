from .base_class import VisuscriptTestCase
import unittest

from abc import abstractmethod, ABC

from visuscript.segment import Segment, MSegment, LSegment, QSegment, ZSegment, Path
from visuscript.primatives import Vec2
from visuscript.math_utility import magnitude


class ABCTestSegment(ABC, VisuscriptTestCase):

    def init_segment(self) -> Segment:
        """Initialize a segment"""
        class MockSegment(Segment):
            offset = Vec2(0,0)
            def point_percentage(self, percentage):
                return self.offset
            @property
            def arc_length(self):
                return 0
            @property
            def start(self):
                return self.point_percentage(0)
            @property
            def end(self):
                return self.point_percentage(1)
            def set_offset(self, x_offset, y_offset):
                self.offset = Vec2(x_offset, y_offset)
                return self
            @property
            def path_str(self):
                return f"M {self.offset[0]} {self.offset[1]}"
        return MockSegment()


    def test_return_types(self):
       segment = self.init_segment()
       
       self.assertIsInstance(segment.point_percentage(0), Vec2)
       self.assertIsInstance(segment.point(0), Vec2)
       self.assertIsInstance(segment.arc_length, (float, int))

       self.assertIsInstance(segment.start, Vec2)
       self.assertIsInstance(segment.end, Vec2)

       self.assertIsInstance(segment.set_offset(10,10), type(segment))

       self.assertIsInstance(segment.path_str, str)

    def test_start_matches_points(self):

        segment = self.init_segment()

        self.assertVecAlmostEqual(segment.start, segment.point(0))
        self.assertVecAlmostEqual(segment.start, segment.point_percentage(0))

    
    def test_arc_length_and_end_match_points(self):

        segment = self.init_segment()

        self.assertVecAlmostEqual(segment.end, segment.point(segment.arc_length))
        self.assertVecAlmostEqual(segment.end, segment.point_percentage(1))
        self.assertVecAlmostEqual(segment.point(segment.arc_length), segment.point_percentage(1))


    def test_point_matches_point_percentage(self):

        segment = self.init_segment()

        for percentage in [0,0.1,0.13,0.24,0.43,0.5,0.61,0.81,0.98,1]:
            self.assertVecAlmostEqual(segment.point(segment.arc_length * percentage), segment.point_percentage(percentage))

    def test_set_offset(self):
        segment = self.init_segment()

        original_points = {}
        for p in [0,0.1,0.13,0.24,0.43,0.5,0.61,0.81,0.98,1]:
            original_points[p] = segment.point_percentage(p)

        for offset in [(0,-1), (-1,0), (1, 0), (0,1), (-12, 3), (9, -2), (4,6), (39, 120)]:
            for p in [0,0.1,0.13,0.24,0.43,0.5,0.61,0.81,0.98,1]:
                segment.set_offset(*offset)
                self.assertVecAlmostEqual(original_points[p]+Vec2(*offset), segment.point_percentage(p))




class TestMSegment(ABCTestSegment):
    def init_segment(self):
        return MSegment(0,12)
    
    def test_zero_arc_length(self):
        m = MSegment(13,-1)
        self.assertEqual(m.arc_length, 0)

    def test_stationary_point(self):
        m = MSegment(13,-1)
        self.assertEqual(m.start, Vec2(13,-1))
        self.assertEqual(m.start, m.end)
        self.assertEqual(m.point_percentage(0.5), m.start)

    def test_path_str(self):
        m = MSegment(13,-1)
        self.assertSequenceEqual(floatify_path_str(m), "M 13.0 -1.0".split())

        m.set_offset(2,-1)
        self.assertSequenceEqual(floatify_path_str(m), "M 15.0 -2.0".split())


class TestLSegment(ABCTestSegment):
    def init_segment(self):
        return LSegment(-10,0,13,24)
    
    def test_arc_length(self):
        for start, end in [(Vec2(0,0), Vec2(0,0)), (Vec2(0,0), Vec2(3,4)), (Vec2(12,-4), Vec2(8,2)), (Vec2(4,100), Vec2(70,70))]:
            l = LSegment(*start, *end)
            self.assertAlmostEqual(magnitude(start - end), l.arc_length, msg=f"failed with start={start} and end={end}")

    def test_is_line(self):
        for start, end in [(Vec2(0,0), Vec2(0,0)), (Vec2(0,0), Vec2(3,4)), (Vec2(12,-4), Vec2(8,2)), (Vec2(4,100), Vec2(70,70))]:
            l = LSegment(*start, *end)
            for p in [0,0.1,0.14,0.43,0.74,0.92,1]:
                self.assertVecAlmostEqual(l.point_percentage(p), start*(1-p) + end*p)

    def test_path_str(self):
        l = LSegment(13,-1, 10, 10)
        self.assertSequenceEqual(floatify_path_str(l), "L 10.0 10.0".split())

        l.set_offset(2,-1)
        self.assertSequenceEqual(floatify_path_str(l), "L 12.0 9.0".split())

class TestZSegment(ABCTestSegment):
    def init_segment(self):
        return ZSegment(-10,0,13,24)
    
    def test_arc_length(self):
        for start, end in [(Vec2(0,0), Vec2(0,0)), (Vec2(0,0), Vec2(3,4)), (Vec2(12,-4), Vec2(8,2)), (Vec2(4,100), Vec2(70,70))]:
            l = ZSegment(*start, *end)
            self.assertAlmostEqual(magnitude(start - end), l.arc_length, msg=f"failed with start={start} and end={end}")

    def test_is_line(self):
        for start, end in [(Vec2(0,0), Vec2(0,0)), (Vec2(0,0), Vec2(3,4)), (Vec2(12,-4), Vec2(8,2)), (Vec2(4,100), Vec2(70,70))]:
            l = ZSegment(*start, *end)
            for p in [0,0.1,0.14,0.43,0.74,0.92,1]:
                self.assertVecAlmostEqual(l.point_percentage(p), start*(1-p) + end*p)
    
    def test_path_str(self):
        l = ZSegment(13,-1, 10, 10)
        self.assertSequenceEqual(l.path_str.split(), "Z".split())

        l.set_offset(2,-1)
        self.assertSequenceEqual(l.path_str.split(), "Z".split())

class TestQSegment(ABCTestSegment):
    def init_segment(self):
        return QSegment(-1,2,10,12,15,23)
    
    def test_start_and_end(self):
        q = QSegment(-1,2,10,12,15,23)

        self.assertEqual(q.start, Vec2(-1,2))
        self.assertEqual(q.end, Vec2(15,23))

    def test_is_bezier_curve(self):
        start = Vec2(-1,2)
        mid = Vec2(10,12)
        end = Vec2(15, 23)
        q = QSegment(*start, *mid, *end)
        for p in [0,0.1,0.13,0.24,0.43,0.5,0.61,0.81,0.98,1]:
            self.assertVecAlmostEqual(
                q.point_percentage(p),
                (start * (1-p) + mid * p) * (1 - p) + (mid * (1 - p) + end * p) * p
            )

    def test_arc_length(self):
        q = QSegment(0,0,0,0,10,0)
        self.assertAlmostEqual(q.arc_length, 10)

    def test_path_str(self):
        q = QSegment(-1,2,10,12,15,23)
        self.assertSequenceEqual(floatify_path_str(q), "Q 10.0 12.0 15.0 23.0".split())

        q.set_offset(2,-1)
        self.assertSequenceEqual(floatify_path_str(q), "Q 12.0 11.0 17.0 22.0".split())



class TestPath(ABCTestSegment):
    def init_segment(self):
        return Path().M(2,-1).L(10,12).Q(30,30, 45,-45)
    
    def test_arc_length(self):
        path = Path().M(0,0).M(2,-1).L(10,12).L(0,0).Q(30,30, 45,-45).Q(40,40,8,8).Z()
        self.assertAlmostEqual(
            path.arc_length,
            (
                LSegment(2,-1, 10, 12).arc_length +
                LSegment(10,12,0,0).arc_length +
                QSegment(0,0,30,30,45,-45).arc_length +
                QSegment(45,-45,40,40,8,8).arc_length +
                ZSegment(8,8,2,-1).arc_length
                )
        )

def floatify_path_str(s: Segment) -> list[str]:
    out = []
    for arg in s.path_str.split():
        if arg.isalpha():
            out.append(arg)
        else:
            out.append(str(float(arg)))

    return out
