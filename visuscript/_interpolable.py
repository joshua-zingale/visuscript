from abc import ABC, abstractmethod
from typing import Self, Union, TypeVar, Generic

class Interpolable(ABC):
    @abstractmethod
    def interpolate(self, other: Self, alpha: float) -> Self:
        ...

InterpolableLike = Union[Interpolable, int, float]


_InterpolableLike = TypeVar("_InterpolableLike", bound=InterpolableLike)
def interpolate(a: _InterpolableLike, b: _InterpolableLike, alpha: float):
    if isinstance(a, (int, float)):
        return a * (1 - alpha) + b * alpha
    return a.interpolate(b, alpha)