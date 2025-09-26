from . import run_for, number_of_frames, MockAnimation
from tests.primatives import rgb_diff
from visuscript import Color, Rgb, Circle


def test_set_speed_number_of_advances():
    num_advances = 17
    for speed in [1, 2, 10, 11]:
        animation = MockAnimation(num_advances).set_speed(speed)
        assert int(num_advances / speed) == number_of_frames(animation), f"speed={speed}"

def test_finish():
    animation = MockAnimation(13)
    animation.finish()
    assert not animation.advance()

def test_compress():
    animation = MockAnimation(13).compress()
    assert animation.advance()
    assert not animation.advance()


def test_flash():
    from visuscript.animation import flash


    circle = Circle(5).set_stroke(Color(Rgb(0, 0, 0)))

    animation = flash(circle.stroke, Rgb(100, 100, 100), duration=4)

    assert rgb_diff(circle.stroke.rgb, Rgb(0, 0, 0)) == 0
    run_for(animation, 1)
    # assert rgb_diff(circle.stroke.rgb, Rgb(50, 50, 50)) < 4
    run_for(animation, 1)
    assert rgb_diff(circle.stroke.rgb, Rgb(100, 100, 100)) < 4
    run_for(animation, 1)
    # assert rgb_diff(circle.stroke.rgb, Rgb(50, 50, 50)) < 4
    run_for(animation, 1)
    assert rgb_diff(circle.stroke.rgb, Rgb(0, 0, 0)) == 0