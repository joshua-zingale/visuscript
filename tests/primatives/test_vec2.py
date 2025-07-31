from visuscript.primatives.primatives import Vec2
import pytest


def test_init():
    vec = Vec2(21, -13.5)
    assert vec.x == 21
    assert vec.y == -13.5


def test_addition():
    assert Vec2(10, 100) + Vec2(1, 2) == Vec2(11, 102)


def test_subtraction():
    assert Vec2(10, 100) - Vec2(1, 2) == Vec2(9, 98)


def test_multiplication():
    assert Vec2(10, 100) * Vec2(1, 2) == Vec2(10, 200)


def test_division():
    assert Vec2(10, 100) / Vec2(2, 10) == Vec2(5, 10)


def test_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        Vec2(100, 2) / Vec2(0, 1)
    with pytest.raises(ZeroDivisionError):
        Vec2(100, 2) / Vec2(1, 0)
    with pytest.raises(ZeroDivisionError):
        Vec2(100, 2) / Vec2(0, 0)
