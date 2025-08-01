from visuscript.primatives.primatives import Rgb


def test_init():
    rgb = Rgb(0, 123, 255)
    assert rgb.r == 0
    assert rgb.g == 123
    assert rgb.b == 255


def test_addition():
    assert Rgb(0, 123, 255) + Rgb(10, 3, 0) == Rgb(10, 126, 255)


def test_subtraction():
    assert Rgb(0, 123, 255) - Rgb(0, 123, 5) == Rgb(0, 0, 250)


def test_multiplication():
    assert Rgb(2, 4, 6) * 2.5 == Rgb(5, 10, 15)


def test_saturating_operations():
    assert Rgb(255, 255, 255) + Rgb(1, 2, 3) == Rgb(255, 255, 255)
    assert Rgb(0, 0, 0) - Rgb(1, 2, 3) == Rgb(0, 0, 0)
