import pytest

from visuscript.animation import animations as an
from visuscript.animation import Animation
from visuscript.config import config
from visuscript import Rect
from visuscript.primatives import Vec2

def test_translate():

    rect = Rect(5)

    animation = an.animate_translation(rect.transform, Vec2(0,100), duration=10)

    rect.translate(0, 50)

    run_for(animation, 5)

    rect.transform.translation.y == pytest.approx(75)





def run_for(animation: Animation, duration: int):
    total_frames = config.fps * duration
    for _ in range(total_frames):
        animation.advance()