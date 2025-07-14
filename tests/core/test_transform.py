from visuscript.visuscript_core import Transform, Vec2
import pytest

def test_init():
    transform = Transform(Vec2(1,2), Vec2(3,4), 5)

    assert transform.rotation == 5
    assert transform.scale == Vec2(3,4)
    assert transform.translation == Vec2(1,2)

def test_composition():
    transform1 = Transform(Vec2(1,2), Vec2(3,3), 180)
    transform2 = Transform(Vec2(10,5), Vec2(2,2), 5)
    composite = transform1 @ transform2

    assert composite.rotation % 360 == pytest.approx(185)
    assert composite.scale == Vec2(6, 6)
    assert ((composite.translation - Vec2(-29, -13)).magnitude()) < 1e-6

def test_vec2_transformation():
    transform = Transform(Vec2(1,2), Vec2(4,4), 90)
    vec = Vec2(5,-3)
    transformed_vec = transform @ vec

    assert (transformed_vec - Vec2(13, 22)).magnitude() < 1e-6

def test_inverse():
    transform = Transform(Vec2(1,2), Vec2(2,2), 90)
    t = transform.inverse() @ transform
    assert t.translation.magnitude() == pytest.approx(0)
    assert t.scale.x, t.scale.y == pytest.approx((1,1))
    assert t.rotation == pytest.approx(0)

    base = Transform(Vec2(13,31), Vec2(13,131), -312)
    transform = Transform(Vec2(-381,134), Vec2(2841, 482), 846.5)
    t = transform.inverse() @ (transform @ base)
    assert (t.translation - base.translation).magnitude() == pytest.approx(0)
    assert t.scale.x, t.scale.y == pytest.approx((base.scale.x,base.scale.y))
    assert t.rotation == pytest.approx(base.rotation)