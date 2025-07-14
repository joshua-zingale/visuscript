from visuscript.visuscript_core import Rgb
import pytest

def test_init():
    rgb = Rgb(0,123,255)
    assert rgb.r == 0
    assert rgb.g == 123
    assert rgb.b == 255

def test_addition():
    assert Rgb(0,123,255) + Rgb(10,3,0) == Rgb(10,126, 255)

def test_subtraction():
    assert Rgb(0,123,255) - Rgb(0,123,5) == Rgb(0,0, 250)

def test_multiplication():
    assert Rgb(1,2,3) * Rgb(10,20,30) == Rgb(10,40,90)

def test_division():
    assert Rgb(10,40,90) / Rgb(10,20,30) == Rgb(1,2,3) 

def test_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(0,20,30) 
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(10,0,30) 
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(10,20,0)
    with pytest.raises(ZeroDivisionError):
        Rgb(10,40,90) / Rgb(0,0,0)

def test_saturating_operations():
    assert Rgb(255,255,255) + Rgb(1,2,3) == Rgb(255,255,255)
    assert Rgb(0,0,0) - Rgb(1,2,3) == Rgb(0,0,0)
    assert Rgb(50,34,29) * Rgb(89,74,60) == Rgb(255,255,255)