from . import MockAnimationState, MockObject, WFloat, WMockObject, run_for
from tests.primatives import rgb_diff

import pytest

from visuscript import Color, Circle, Rgb
from visuscript.animation.constructors import construct, laze, keyframe_construct, sequence
from visuscript.lazy_object import Lazible
from visuscript.property_locker import PropertyLocker
from visuscript.animation.protocols import Keyframe

def test_construct():
    times_called = 0
    def decrement_to_0(num: int):
        nonlocal times_called
        times_called += 1
        if num == 0:
            return None
        return num -1

    animation = construct(decrement_to_0, 5)
    animation.finish()
    assert times_called == 5

def test_non_lazy_animation_eagerly_initializes():

    obj = MockObject(x=0)
    animation = get_mock_interpolation(obj, 10, 100)
    obj.x = 5

    animation.advance()
    assert obj.x == pytest.approx(0.1)


def test_lazy_animation_delays_initializes_until_first_advance():

    obj = MockObject(x=0)
    animation = laze(get_mock_interpolation, obj, 10, 100)
    obj.x = 5

    animation.advance()
    assert obj.x == pytest.approx(5.05)

def test_lazy_arguments_not_evaluated_until_first_advance():

    obj = MockObject(x=0)
    destination = MockObject(10)
    animation = laze(get_mock_interpolation, obj, destination.lazy.x, 100)
    destination.x = 100

    animation.finish()
    assert obj.x == 100


def test_lazy_with_locker():

    obj = MockObject(x=0)
    destination = MockObject(10)
    animation = laze(PropertyLocker({obj:["x"]}), get_mock_interpolation, obj, destination.lazy.x, 100)
    destination.x = 100
    assert animation.locker.locks(obj, "x")

    animation.finish()
    assert obj.x == 100


def test_keyframe_construct():
    obj = WMockObject(0)
    keyframes: list[tuple[WFloat, float]] = [(WFloat(0), 0), (WFloat(0), 0.3), (WFloat(2), 0.7), (WFloat(11), 1.0)]

    def jump_interpolate(alpha: float, *keyframes: Keyframe[WFloat]):
        for frame, next_frame in zip(keyframes, keyframes[1:]):
            if alpha >= frame[1] and alpha <= next_frame[1]:
                return next_frame[0]
        return keyframes[-1][0]

    animation = keyframe_construct(obj.set_x, 10, jump_interpolate, keyframes[0], keyframes[1:])

    assert obj.x == 0
    animation.advance()
    assert obj.x == pytest.approx(0)
    animation.advance()
    assert obj.x == pytest.approx(0)
    animation.advance()
    assert obj.x == pytest.approx(0)

    animation.advance()
    assert obj.x == pytest.approx(2)
    animation.advance()
    assert obj.x == pytest.approx(2)
    animation.advance()
    assert obj.x == pytest.approx(2)
    animation.advance()
    assert obj.x == pytest.approx(2)

    animation.advance()
    assert obj.x == pytest.approx(11)
    animation.advance()
    assert obj.x == pytest.approx(11)
    animation.advance()
    assert obj.x == pytest.approx(11)

def test_keyframe_construct_with_locker():

    obj = WMockObject(0)
    keyframes = [(WFloat(0), 0), (WFloat(0), 0.3), (WFloat(2), 0.7), (WFloat(11), 1.0)]

    def jump_interpolate(alpha: float, *keyframes: Keyframe[WFloat]):
        for frame, next_frame in zip(keyframes, keyframes[1:]):
            if alpha >= frame[1] and alpha <= next_frame[1]:
                return next_frame[0]
        return keyframes[-1][0]

    animation = keyframe_construct(obj.set_x, 10, jump_interpolate, keyframes[0], keyframes[1:], locker=PropertyLocker({obj: "x"}))

    assert animation.locker.locks(obj, "x")
    assert not animation.locker.locks(obj, "y")

    

def test_sequence():
    from visuscript.animation import fade_in, fade_out, flash

    circle = Circle(5).set_stroke(Color(Rgb(50, 50, 50))).set_opacity(0.25)

    seq = sequence(
        fade_in(circle, duration=2),
        flash(circle.stroke, Rgb(100, 100, 100), duration=4),
        fade_out(circle, duration=2),
    )

    circle.set_stroke(Color(Rgb(0, 0, 0))).set_opacity(0)

    # Fade in
    assert circle.opacity == 0
    run_for(seq, 1)
    assert circle.opacity == pytest.approx(0.5)
    run_for(seq, 1)
    assert circle.opacity == 1

    # Flash
    assert circle.stroke.rgb == Rgb(0, 0, 0)
    run_for(seq, 1)
    # assert rgb_diff(circle.stroke.rgb, Rgb(50, 50, 50)) < 4
    run_for(seq, 1)
    assert rgb_diff(circle.stroke.rgb, Rgb(100, 100, 100)) < 4
    run_for(seq, 1)
    # assert rgb_diff(circle.stroke.rgb, Rgb(50, 50, 50)) < 4
    run_for(seq, 1)
    assert circle.stroke.rgb == Rgb(0, 0, 0)

    # Fade out
    run_for(seq, 1)

    assert circle.opacity == pytest.approx(0.5)

    run_for(seq, 1)
    assert circle.opacity == 0







def get_mock_interpolation(obj: MockObject, destination: float, num_frames: int):
    state = MockAnimationState(obj = obj, start=obj.x, destination=destination, total_frames=num_frames)
    def advance(state: MockAnimationState):
        state.num_processed_frames += 1
        if state.num_processed_frames == state.total_frames:
            state.obj.x = destination
            return state
        elif state.num_processed_frames > state.total_frames:
            return None
        p = state.num_processed_frames / state.total_frames
        state.obj.x = state.start * (1-p) + state.destination * p
        return state
    return construct(advance, state)

