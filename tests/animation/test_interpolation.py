import pytest
from . import WFloat
from visuscript.animation.interpolation import linearly_interpolate, keyframe, interpolate



def test_linearly_interpolate():
    
    
    assert linearly_interpolate(
        0,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == 0
    assert linearly_interpolate(
        0.25,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx(-2.5)
    assert linearly_interpolate(
        0.5,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx(-5)
    assert linearly_interpolate(
        0.75,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx((11-5)/2)
    assert linearly_interpolate(
        1,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx(11)
    

def test_interpolate():
    
    
    assert interpolate(
        0,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == 0
    assert interpolate(
        0.5,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx(-5)
    assert interpolate(
        1,
        keyframe(WFloat(0), 0.0),
        keyframe(WFloat(-5), 0.5),
        keyframe(WFloat(11), 1.0)).get_interpolated_object() == pytest.approx(11)
