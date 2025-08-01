from abc import ABC, abstractmethod
from typing import Union, TypeVar


T = TypeVar("T", bound="Interpolable")


class Interpolable(ABC):
    @abstractmethod
    def interpolate(self: T, other: T, alpha: float) -> T:
        """Interpolates between this object and another and returns the result as a new object."""


InterpolableLike = Union[Interpolable, int, float]  # type: ignore


_InterpolableLike = TypeVar("_InterpolableLike", bound=InterpolableLike)


def interpolate(
    a: _InterpolableLike, b: _InterpolableLike, alpha: float
) -> _InterpolableLike:
    if isinstance(a, (int, float)):
        return a * (1 - alpha) + b * alpha  # type: ignore
    return a.interpolate(b, alpha)  # type: ignore
