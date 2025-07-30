from abc import ABC, abstractmethod
from typing import Self, Union, TypeVar


class Interpolable(ABC):
    @abstractmethod
    def interpolate(self, other: Self, alpha: float) -> Self: ...


InterpolableLike = Union[Interpolable, int, float]  # type: ignore


_InterpolableLike = TypeVar("_InterpolableLike", bound=InterpolableLike)


def interpolate(
    a: _InterpolableLike, b: _InterpolableLike, alpha: float
) -> _InterpolableLike:
    if isinstance(a, (int, float)):
        return a * (1 - alpha) + b * alpha  # type: ignore
    return a.interpolate(b, alpha)  # type: ignore
