from visuscript.visuscript_core import Vec2, Rgb
import pytest

def test_vec2_init():
    vec = Vec2(21,-13.5)
    assert vec.x == 21
    assert vec.y == -13.5

def test_vec2_addition():
    assert Vec2(10, 100) + Vec2(1,2) == Vec2(11, 102)

def test_vec2_subtraction():
    assert Vec2(10, 100) - Vec2(1,2) == Vec2(9, 98)

def test_vec2_multiplication():
    assert Vec2(10, 100) * Vec2(1,2) == Vec2(10, 200)

def test_vec2_division():
    assert Vec2(10, 100) / Vec2(2,10) == Vec2(5, 10)

def test_vec2_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        Vec2(100,2) / Vec2(0,1)
    with pytest.raises(ZeroDivisionError):
        Vec2(100,2) / Vec2(1,0)
    with pytest.raises(ZeroDivisionError):
        Vec2(100,2) / Vec2(0,0)


def test_rgb_init():
    rgb = Rgb(0,123,255)
    assert rgb.r == 0
    assert rgb.g == 123
    assert rgb.b == 255

def test_rgb_addition():
    assert Rgb(0,123,255) + Rgb(10,3,0) == Rgb(10,126, 255)

def test_rgb_subtraction():
    assert Rgb(0,123,255) - Rgb(0,123,5) == Rgb(0,0, 250)

def test_rgb_multiplication():
    assert Rgb(1,2,3) * Rgb(10,20,30) == Rgb(10,40,90)

def test_rgb_division():
    assert Rgb(10,40,90) / Rgb(10,20,30) == Rgb(1,2,3) 

def test_rgb_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(0,20,30) 
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(10,0,30) 
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(10,20,0)
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(0,0,0)