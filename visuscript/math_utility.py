from visuscript.primatives import Vec
from typing import Sequence, TypeVar

import numpy as np

_VecType = TypeVar('_VecType', bound='Vec')


def magnitude(vec: Vec) -> float:
    return vec.dot(vec)**0.5

def unit_diff(vec1: _VecType, vec2: _VecType) -> _VecType:
    diff = vec1 - vec2
    norm = magnitude(diff)
    if norm == 0:
        return type(vec1)(*(0 for _ in vec1))
    return diff/magnitude(diff)

def invert(matrix: Sequence[Sequence[float]]) -> Sequence[Sequence[float]]:
    return np.linalg.inv(matrix).tolist()
