from visuscript._internal._invalidator import Invalidator, Invalidatable, invalidates
from visuscript._internal._interpolable import Interpolable
from visuscript.lazy_object import Lazible

import math

from typing import (
    Self,
    Sequence,
    Callable,
    Iterator,
    overload,
    Union,
    TypeAlias,
    no_type_check,
    Iterable,
)
from operator import add, mul, sub, truediv, neg, pow, eq
from array import array


_Number: TypeAlias = Union[int, float]
_MatrixLike: TypeAlias = Sequence[Sequence[_Number]]


class SizeMismatch(ValueError):
    def __init__(self, size1: int, size2: int, operation: str):
        super().__init__(
            f"Size mismatch for {operation}: Size {size1} is not compatible with Size {size2}."
        )


class Vec(Sequence[_Number], Interpolable):
    _VecLike: TypeAlias = Union["Vec", Sequence[_Number]]

    def __init__(self, *args: _Number):
        self._arr = array("d", [*args])

    def interpolate(self, other: _VecLike, alpha: _Number) -> Self:
        return self._element_wise(lambda a, b: a * (1 - alpha) + b * alpha, other)

    def _element_wise(
        self,
        operation: Callable[[_Number, _Number], _Number],
        other: _VecLike | _Number,
    ):
        if not isinstance(other, Sequence):
            return self.__class__(*(operation(s, other) for s in self))

        if len(self) != len(other):
            raise SizeMismatch(len(self), len(other), f"__{operation.__name__}__")

        return self.__class__(*(operation(s, o) for s, o in zip(self, other)))

    def add(self, other: _VecLike) -> Self:
        return self + other

    def sub(self, other: _VecLike) -> Self:
        return self - other

    def mul(self, other: _VecLike) -> Self:
        return self * other

    def div(self, other: _VecLike) -> Self:
        return self / other

    def dot(self, other: _VecLike) -> _Number:
        prods = self._element_wise(mul, other)
        return sum(prods)

    @overload
    def __getitem__(self, index: int) -> _Number: ...
    @overload
    def __getitem__(self, index: slice) -> "Vec": ...
    def __getitem__(self, index: int | slice) -> Union[_Number, "Vec"]:  # type: ignore
        if isinstance(index, slice):
            return Vec(*self._arr[index])
        return self._arr[index]

    def __len__(self) -> int:
        return len(self._arr)

    def __eq__(self, other: _VecLike) -> bool:  # type: ignore
        return sum(self._element_wise(eq, other)) == len(self)

    def __add__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(add, other)

    def __radd__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(add, other)

    def __sub__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(sub, other)

    def __rsub__(self, other: _VecLike | _Number) -> Self:
        vec = self.__class__(*map(lambda x: -x, self))
        return vec._element_wise(add, other)

    def __mul__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(mul, other)

    def __rmul__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(mul, other)

    def __truediv__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(truediv, other)

    def __rtruediv__(self, other: _VecLike | _Number) -> Self:
        vec = self.__class__(*map(lambda x: 1 / x, self))
        return vec._element_wise(mul, other)

    def __pow__(self, other: _VecLike | _Number) -> Self:
        return self._element_wise(pow, other)

    # def __rpow__(self, other: "Vec") -> Self:
    #     vec = self.__class__(*map(lambda x: 1/x, self))
    #     return vec._element_wise(mul, other)

    def __neg__(self) -> Self:
        return self.__class__(*map(neg, self))

    @no_type_check
    def __rmatmul__(self, other: _MatrixLike):
        return self.__class__(
            *(
                sum(map(lambda a: a[0] * a[1], zip(other[i], self, strict=True)))
                for i in range(len(self))
            )
        )

    def __str__(self):
        return f"{[*self]}"

    def __repr__(self):
        return f"Vec{(*self,)}"

    def max(self):
        return max(self)


class Vec2(Vec):
    _Vec2Like: TypeAlias = Union["Vec2", Sequence[_Number]]

    def __init__(self, x: _Number, y: _Number):
        super().__init__(x, y)

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    @staticmethod
    def construct(other: _Vec2Like) -> "Vec2":
        """Constructs and returns a :class:`Vec2` from an integer sequence of length two."""
        if len(other) == 2:
            return Vec2(*other)

        end_string = f"of length {len(other)}" if hasattr(other, "__len__") else ""
        raise ValueError(
            f"Cannot create a vector out of '{other.__class__.__name__}' {end_string}."
        )


class Rgb(Interpolable):
    _RgbLike: TypeAlias = Union["Rgb", str, tuple[int, int, int]]

    def __init__(self, r: int, g: int, b: int):
        for v in [r, g, b]:
            if v < 0 or v > 255:
                raise ValueError(
                    f"{v} is not a valid RGB value. RGB values must be between 0 and 255, includsive."
                )
        self._rgb: list[int] = [r, g, b]

    def interpolate(self, other: "Rgb", alpha: float) -> "Rgb":
        return Rgb(
            *(
                min(max(round(s * (1 - alpha) + o * alpha), 0), 255)
                for s, o in zip(self._rgb, other._rgb)
            )
        )

    def __iter__(self) -> Iterator[int]:
        yield from self._rgb

    def __add__(self, other: "Rgb") -> "Rgb":
        return Rgb(*[min(s + o, 255) for s, o in zip(self._rgb, other._rgb)])

    def __sub__(self, other: "Rgb") -> "Rgb":
        return Rgb(*[max(s - o, 0) for s, o in zip(self._rgb, other._rgb)])

    def __mul__(self, other: _Number) -> "Rgb":
        return Rgb(*[min(int(s * other), 255) for s in self._rgb])

    def __rmul__(self, other: _Number) -> "Rgb":
        return self * other

    def __truediv__(self, other: _Number) -> "Rgb":
        return self * (1 / other)

    def __eq__(self, other: "Rgb"):  # type: ignore
        return (
            self._rgb[0] == other._rgb[0]
            and self._rgb[1] == other._rgb[1]
            and self._rgb[2] == other._rgb[2]
        )

    def __str__(self):
        r, g, b = self._rgb
        return f"RGB({r}, {g}, {b})"

    def __repr__(self):
        return str(self)

    @property
    def svg(self):
        r, g, b = self._rgb
        return f"rgb({r},{g},{b})"

    @property
    def r(self) -> int:
        return self._rgb[0]

    @property
    def g(self) -> int:
        return self._rgb[1]

    @property
    def b(self) -> int:
        return self._rgb[2]


class Transform(Invalidator, Interpolable, Lazible):
    _TransformLike: TypeAlias = Union["Transform", Vec2._Vec2Like]

    def __init__(
        self,
        translation: Vec2._Vec2Like = [0, 0],
        scale: Vec2._Vec2Like | _Number = [1, 1],
        rotation: _Number = 0.0,
    ):
        if isinstance(scale, _Number):
            scale = [scale, scale]

        self._translation: Vec2 = Vec2.construct(translation)
        self._scale: Vec2 = Vec2.construct(scale)
        self._rotation: _Number = rotation

        self._invalidatables: set[Invalidatable] = set()

    @staticmethod
    def construct(other: _TransformLike):
        if isinstance(other, Transform):
            return Transform(
                translation=other.translation,
                scale=other.scale,
                rotation=other.rotation,
            )
        else:
            return Transform(translation=other, scale=[1, 1], rotation=0)

    def _add_invalidatable(self, invalidatable: Invalidatable):
        self._invalidatables.add(invalidatable)

    def _iter_invalidatables(self) -> Iterable[Invalidatable]:
        yield from self._invalidatables

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    @invalidates
    def rotation(self, value: _Number):
        self._rotation = value

    def rotate(self, vec2: Vec2._Vec2Like) -> Vec2:
        t = self.rotation * math.pi / 180
        r_matrix = [[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]]

        return Vec2(*(r_matrix @ Vec2.construct(vec2)))

    @property
    def translation(self) -> Vec2:
        return self._translation

    @translation.setter
    @invalidates
    def translation(self, value: Vec2._Vec2Like):
        value = Vec2.construct(value)
        self._translation = value

    @property
    def scale(self) -> Vec2:
        return self._scale

    @scale.setter
    @invalidates
    def scale(self, value: _Number | Vec2._Vec2Like):
        if isinstance(value, _Number):
            self._scale = Vec2(value, value)
            return

        self._scale = Vec2.construct(value)

    def set_translation(self, translation: Vec2._Vec2Like) -> Self:
        self.translation = translation
        return self

    def set_scale(self, scale: _Number | Vec2._Vec2Like) -> Self:
        self.scale = scale
        return self

    def set_rotation(self, rotation: _Number) -> Self:
        self.rotation = rotation
        return self

    @property
    def svg_transform(self) -> str:
        """
        The SVG representation of this Transform, as can be specified with "transfrom="
        """
        return f"translate({' '.join(map(str, self.translation[:2]))}) scale({' '.join(map(str, self.scale[:2]))}) rotate({self.rotation})"

    def __str__(self):
        return self.svg_transform

    def __repr__(self):
        return str(self)

    @overload
    def __call__(self, other: "Transform") -> "Transform": ...
    @overload
    def __call__(self, other: Vec2) -> Vec2: ...
    def __call__(self, other: Union["Transform", Vec2]) -> Union["Transform", Vec2]:
        return self @ other

    @overload
    def __matmul__(self, other: "Transform") -> "Transform": ...
    @overload
    def __matmul__(self, other: Vec2) -> Vec2: ...
    def __matmul__(self, other: Union["Transform", Vec2]) -> Union["Transform", Vec2]:
        t = self.rotation * math.pi / 180
        r_matrix = [[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]]

        if isinstance(other, (Vec2, Sequence)):
            return (r_matrix @ (other * self.scale)) + self._translation

        return Transform(
            translation=r_matrix @ (other._translation * self.scale)
            + self._translation,
            scale=self.scale * other.scale,
            rotation=self.rotation + other.rotation,
        )

    def interpolate(self, other: Self, alpha: _Number) -> "Transform":
        """Initializes and returns a new :class:`Transform` by interpolating between this :class:`Transform` and another.

        :param other: The other :class:`Transform` between which this :class:`Transform` is to be interpolated.
        :param alpha: The progress of the interpolation between this :class:`Transform` and another.
            If 0, returns an equivalent :class:`Transform` to self;
            if 1, returns an equivalent :class:`Transform` to other.
        :return: A newly initialized :class:`Transform`
        """

        return Transform(
            translation=self.translation * (1 - alpha) + other.translation * alpha,
            scale=self.scale * (1 - alpha) + other.scale * alpha,
            rotation=self.rotation * (1 - alpha) + other.rotation * alpha,
        )

    # DOUBLE REFERENCES
    # These double refeences should not be a problem because Vecs are immutable
    @invalidates
    def update(self, other: Self):
        """Updates this :class:`Transform` with another.

        :param other: The other :class:`Transform` of which the members will update this :class:`Transform`
        :type other: Self
        """
        self._translation = other.translation
        self._scale = other.scale
        self._rotation = other.rotation
