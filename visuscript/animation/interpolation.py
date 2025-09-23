"""Contains functions for interpolating between objects."""
import typing as t

from .protocols import Interpolable, Keyframe
_T = t.TypeVar("_T")


__all__ = [
    "keyframe",
    "linearly_interpolate",
    "cattmul_rom_interpolate",
    "interpolate",
]


def keyframe(interpolable: Interpolable[_T], alpha: float) -> Keyframe[_T]:
    return (interpolable, alpha)

def linearly_interpolate(alpha: float, first_keyframe: Keyframe[_T], *keyframes: Keyframe[_T]) -> Interpolable[_T]:
    start = next(filter(lambda k: k[1] <= alpha, reversed(keyframes)), first_keyframe)
    end = next(filter(lambda k: k[1] >= alpha, keyframes), keyframes[-1] if len(keyframes) > 0 else first_keyframe)
    if start[1] == end[1]:
        return start[0]
    sub_alpha = min(max((alpha - start[1]) / (end[1] - start[1]), 0), 1)
    return start[0] + sub_alpha*(end[0] - start[0])

def cattmul_rom_interpolate(alpha: float, first_keyframe: Keyframe[_T], *keyframes: Keyframe[_T]) -> Interpolable[_T]:
    if len(keyframes) == 0:
        return first_keyframe[0]
    if len(keyframes) == 1:
        return linearly_interpolate(alpha, first_keyframe, *keyframes)
    
    left_pad = (2*first_keyframe[0] - keyframes[0][0], 2*first_keyframe[1] - keyframes[0][1])
    right_pad = (2*keyframes[-1][0] - keyframes[-2][0], 2*keyframes[-1][1] - keyframes[-2][1]) 
    padded_keyframes = (left_pad, first_keyframe, *keyframes, right_pad)


    values: tuple[Interpolable[_T], ...]
    alphas: tuple[float, ...]
    values, alphas = zip(*padded_keyframes)


    segment_index = -1
    for i in range(1, len(alphas) - 2):
        if alphas[i] <= alpha <= alphas[i+1]:
            segment_index = i
            break
    

    if segment_index == -1:
        if alpha <= alphas[1]:
            segment_index = 1
        elif alpha >= alphas[-2]:
            segment_index = len(alphas) - 2
        else:
            min_diff_idx = min(range(1, len(alphas) - 2), key=lambda i: abs(alphas[i] - alpha))
            segment_index = min_diff_idx


    # Control points
    p0 = values[segment_index - 1]
    p1 = values[segment_index]
    p2 = values[segment_index + 1]
    p3 = values[segment_index + 2]


    segment_start_alpha = alphas[segment_index]
    segment_end_alpha = alphas[segment_index + 1]
    
    if segment_end_alpha == segment_start_alpha:
        return p1
        
    t = (alpha - segment_start_alpha) / (segment_end_alpha - segment_start_alpha)
    t = min(max(t, 0), 1)

    # Catmull-Rom spline formula
    t_squared = t * t
    t_cubed = t_squared * t

    a = 2 * p1
    b = (p2 - p0) * t
    c = (2 * p0 - 5 * p1 + 4 * p2 - p3) * t_squared
    d = (3 * p1 - 3 * p2 + p3 - p0) * t_cubed

    result = a + b + c + d
    
    return 0.5 * result


def interpolate(alpha: float, first_keyframe: Keyframe[_T], *keyframes: Keyframe[_T]) -> Interpolable[_T]:
    """An easing interpolation function. This is a good general interpolator for animations."""
    return cattmul_rom_interpolate(alpha, first_keyframe, *keyframes)



# def bezier_interpolate(alpha: float, first_keyframe: Keyframe[_T], *keyframes: Keyframe[_T]) -> Interpolable[_T]:
#     if len(keyframes) == 0:
#         return first_keyframe[0]
#     if len(keyframes) == 1:
#         return linearly_interpolate(alpha, first_keyframe, *keyframes)
    
    
#     alpha = keyframes[-1][1]*(alpha - first_keyframe[1]) / (keyframes[-1][1] - first_keyframe[1])

#     keyframes = (first_keyframe, *keyframes)

#     if len(keyframes) == 3:
#         return _bezier(alpha, *keyframes)
#     # left_pad = (2*keyframes[0][0] - keyframes[1][0], 2*keyframes[0][1] - keyframes[1][1])
#     # right_pad = (2*keyframes[-1][0] - keyframes[-2][0], 2*keyframes[-1][1] - keyframes[-2][1]) 
    

#     decreasing_lower_bounds = filter(lambda k: k[1] <= alpha, reversed(keyframes))
#     increasing_upper_bounds = filter(lambda k: k[1] >= alpha, keyframes)

#     p2, p1 = next(decreasing_lower_bounds), next(decreasing_lower_bounds, None)
#     p3, p4 = next(increasing_upper_bounds), next(increasing_upper_bounds, None)


#     if p1 is None:
#         p1, p2, p3, p4, = p2, p3, p4, next(increasing_upper_bounds)
#         assert p3
#     elif p4 is None:
#         p1, p2, p3, p4 = next(decreasing_lower_bounds), p1, p2, p3


#     t = (alpha - p1[1]) / (p3[1] - p1[1])

#     assert t >= 0
#     assert t <= 1

#     return _bezier(alpha, p1, p2, p3) * (1 - t) + _bezier(alpha, p2, p3, p4) * t



# def _bezier(alpha: float, k1: Keyframe[_T], k2: Keyframe[_T], k3: Keyframe[_T]) -> Interpolable[_T]:

#     t = k3[1]*(alpha - k1[1])/(k3[1] - k1[1])

#     p1 = k1[0] + (k2[0] - k1[0]) * t
#     p2 = k2[0] + (k3[0] - k2[0]) * t
#     return p1 + (p2 - p1) * t

