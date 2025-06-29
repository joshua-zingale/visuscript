from visuscript._internal._invalidator import Invalidator, Invalidatable, invalidates
from visuscript._internal._interpolable import Interpolable
from visuscript.lazy_object import Lazible

import numpy as np

from typing import Self, Tuple, Sequence, Callable, Iterator, overload, Union, TypeAlias, no_type_check, Iterable
from operator import add, mul, sub, truediv, neg, pow, eq
from array import array
from copy import deepcopy

class SizeMismatch(ValueError):
    def __init__(self, size1: int, size2: int, operation: str):
        super().__init__(f"Size mismatch for {operation}: Size {size1} is not compatible with Size {size2}.")

_VecLike: TypeAlias = Sequence[float]
#TODO Add support for arbitrary dimensions in a base class, which can be used for matrices etc later
class Vec(Sequence[float], Interpolable[_VecLike]):
    # @staticmethod
    # def size_check(operation):
    #     def size_check_function(self, other):
    #         if len(self) != len(other):
    #             raise SizeMismatch(len(self, len(other), operation))
    #         return operation(self, other)
    #     return size_check_function

    def __init__(self, *args: float):
        self._arr = array('d', [*args])

    def interpolate(self, other: _VecLike, alpha: float) -> Self:
        return self._element_wise(lambda a,b: a*(1 - alpha) + b*alpha, other)
    
    def _element_wise(self, operation: Callable[[float, float], float], other: _VecLike | float | int):
        if not isinstance(other, Sequence):
            return self.__class__(*(operation(s, other) for s in self))
        
        if len(self) != len(other):
            raise SizeMismatch(len(self), len(other), f"__{operation.__name__}__")
        
        return self.__class__(*(operation(s, o) for s,o in zip(self, other)))
    
    def add(self, other: _VecLike) -> Self:
        return self + other
    def sub(self, other: _VecLike) -> Self:
        return self - other
    def mul(self, other: _VecLike) -> Self:
        return self * other
    def div(self, other: _VecLike) -> Self:
        return self / other


    def dot(self, other: _VecLike) -> float:
        prods = self._element_wise(mul, other)
        return sum(prods)

    @overload
    def __getitem__(self, index: int) -> float:
        ...
    @overload
    def __getitem__(self, index: slice) -> "Vec":
        ...
    def __getitem__(self, index: int | slice) -> Union[float, "Vec"]: # type: ignore
        if isinstance(index, slice):
            return Vec(*self._arr[index])
        return self._arr[index]

    def __len__(self) -> int:
        return len(self._arr)

    def __eq__(self, other: _VecLike) -> bool: # type: ignore
        return sum(self._element_wise(eq, other)) == len(self)
    
    def __add__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(add, other)
    def __radd__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(add, other)

    def __sub__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(sub, other)
    def __rsub__(self, other: _VecLike | int | float) -> Self:
        vec = self.__class__(*map(lambda x: -x, self))
        return vec._element_wise(add, other)

    def __mul__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(mul, other)
    def __rmul__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(mul, other)
    
    def __truediv__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(truediv, other)
    def __rtruediv__(self, other: _VecLike | int | float) -> Self:
        vec = self.__class__(*map(lambda x: 1/x, self))
        return vec._element_wise(mul, other)
    
    def __pow__(self, other: _VecLike | int | float) -> Self:
        return self._element_wise(pow, other)
    # def __rpow__(self, other: "Vec") -> Self:
    #     vec = self.__class__(*map(lambda x: 1/x, self))
    #     return vec._element_wise(mul, other)
    
    
    def __neg__(self) -> Self:
        return self.__class__(*map(neg, self))
    
    #TODO fixure out a good type here for the other in matmul
    @no_type_check
    def __matmul__(self, other) -> Self:
        return self.__class__(*np.matmul(self, other))
    @no_type_check
    def __rmatmul__(self, other):
        return self.__class__(*np.matmul(other, self))
    
    def __str__(self):
        return f"Vec{(*self,)}"
    def __repr__(self):
        return str(self)
    def max(self):
        return max(self)


class Vec2(Vec):
    def __init__(self, x: float, y: float):
        super().__init__(x,y)

    def extend(self, z: float):
        """Get a Vec3 with the same x,y as this Vec2, where the parameter sets z."""
        return Vec3(*self, z=z)
    
    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    
class Vec3(Vec):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x,y,z)

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    @property
    def z(self) -> float:
        return self[2]

    @property
    def xy(self) -> Vec2:
        """
        Get a Vec2 with the same first and second value as this Vec3.
        """
        return Vec2(*self[:2])

class Rgb(Interpolable["Rgb"]):
    def __init__(self, r: int, g: int, b: int):
        for v in [r,g,b]:
            if v < 0 or v > 255:
                raise ValueError(f"{v} is not a valid RGB value. RGB values must be between 0 and 255, includsive.")
        self._rgb: list[int] = [r,g,b]
    def interpolate(self, other: "Rgb", alpha: float) -> "Rgb":
        return Rgb(*(min(max(round(s*(1-alpha) + o*alpha),0),255) for s,o in zip(self._rgb, other._rgb) ))
    
    def __iter__(self) -> Iterator[int]:
        yield from self._rgb

    def __add__(self, other: "Rgb") -> "Rgb":
        return Rgb(*[min(s+o,255) for s,o in zip(self._rgb, other._rgb)])
    
    def __mul__(self, other: float) -> "Rgb":
        return Rgb(*[min(int(s*other),255) for s in self._rgb])
    def __rmul__(self, other: float) -> "Rgb":
        return self * other
    def __truediv__(self, other: float) -> "Rgb":
        return self * (1/other)
    
    def __eq__(self, other: "Rgb"): # type: ignore
        return self._rgb[0] == other._rgb[0] and self._rgb[1] == other._rgb[1] and self._rgb[2] == other._rgb[2]
    
    def __str__(self):
        r,g,b = self._rgb
        return f"RGB({r}, {g}, {b})"
    
    def __repr__(self):
        return str(self)


def get_vec3(values: Sequence[float], z_fill: float = 0.0) -> Vec3:    
    if len(values) == 2:
        return Vec3(*values, z=z_fill)
    elif len(values) == 3:
        return Vec3(*values)
    else:
        raise ValueError(f"Cannot make Vec3 out of collection of length {len(values)}. Must be of length 2 or 3.")


class Transform(Invalidator, Interpolable["Transform"], Lazible):

    def __init__(self, translation: Vec2 | Vec3 | Sequence[float] | Self = [0,0,0], scale: Vec2 | Vec3 | Sequence[float] | float = [1,1,1], rotation: float = 0.0):
        
        if isinstance(translation, Transform):
            self._translation = translation.translation
            self._scale = translation.scale
            self._rotation = translation.rotation
            return 
        
        if isinstance(scale, (int, float)):
            scale = [scale, scale, 1]

        self._translation: Vec3 = get_vec3(translation, 0)
        self._scale: Vec3 = get_vec3(scale, 1)
        self._rotation: float = rotation

        self._invalidatables: set[Invalidatable]  = set()


    def _add_invalidatable(self, invalidatable: Invalidatable):
        self._invalidatables.add(invalidatable)
    def _iter_invalidatables(self) -> Iterable[Invalidatable]:
        yield from self._invalidatables

    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    @invalidates
    def rotation(self, value: float):
        self._rotation = value

    def rotate(self, vec3: Vec3) -> Vec3:
        r_matrix = [
            [np.cos(self.rotation*np.pi/180), -np.sin(self.rotation*np.pi/180),0],
            [np.sin(self.rotation*np.pi/180), np.cos(self.rotation*np.pi/180), 0],
            [0, 0, 1]
        ]

        return Vec3(*(r_matrix @ vec3))

    @property
    def translation(self) -> Vec3:
        return self._translation
    
    @translation.setter
    @invalidates
    def translation(self, value: Vec2 | Vec3 | Sequence[float]):
        assert 2 <= len(value) and len(value) <= 3

        value = get_vec3(value, z_fill=self.translation.z)

        self._translation = value


    @property
    def scale(self) -> Vec3:
        return self._scale
    
    @scale.setter
    @invalidates
    def scale(self, value: int | float | Sequence[float]):
        if not isinstance(value, Sequence):
            self._scale = Vec3(value, value, 1.0)
            return

        if len(value) == 2:
            self._scale = Vec3(*value, z=self._scale[2])
        elif len(value) == 3:
            self._scale = Vec3(*value)
        else:
            raise ValueError(f"Cannot set scale to a sequence of length {len(value)}: must be length 2 or 3.")


    def set_translation(self, translation: Vec2 | Vec3) -> Self:
        self.translation = translation
        return self
    
    def set_scale(self, scale: int | float | Vec2 | Vec3) -> Self:
        self.scale = scale
        return self
    
    def set_rotation(self, rotation: int | float) -> Self:
        self.rotation = rotation
        return self

    

    @property
    def svg_transform(self) -> str:
        """
        The SVG representation of this Transform, as can be specified with "transfrom="
        """
        return f"translate({" ".join(map(str, self.translation[:2]))}) scale({" ".join(map(str, self.scale[:2]))}) rotate({self.rotation})"
    
    def __str__(self):
        return self.svg_transform
    
    def __repr__(self):
        return str(self)

    def __call__(self, other: Self | Vec2 | Vec3) -> Union["Transform", Vec2, Vec3]:
        return self @ other
    
    def __matmul__(self, other: Union[Self, Vec2, Vec3]) -> Union["Transform", Vec2, Vec3]:
        t = (self.rotation * np.pi/180)
        r_matrix = [
            [np.cos(t), -np.sin(t),0],
            [np.sin(t), np.cos(t), 0],
            [0, 0, 1]
        ]

        if isinstance(other, Vec2):
            return ((r_matrix@(other.extend(0.0)*self.scale)) + self._translation).xy
        
        if isinstance(other, Vec3):
            return (r_matrix@(other*self.scale)) + self._translation

        return Transform(
            translation = r_matrix@(other._translation * self.scale) + self._translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
            )
    
    def interpolate(self, other: Self, alpha: float) -> "Transform":
        """Initializes and returns a new :class:`Transform` by interpolating between this :class:`Transform` and another.

        :param other: The other :class:`Transform` between which this :class:`Transform` is to be interpolated.
        :type other: Self
        :param alpha: The progress of the interpolation between this :class:`Transform` and another.
            If 0, returns an equivalent :class:`Transform` to self;
            if 1, returns an equivalent :class:`Transform` to other.
        :type alpha: float
        :return: A newly initialized :class:`Transform`
        :rtype: Transform
        """

        return Transform(
            translation = self.translation * (1 - alpha) + other.translation * alpha,
            scale = self.scale * (1 - alpha) + other.scale * alpha,
            rotation = self.rotation * (1 - alpha) + other.rotation * alpha
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
    
    # TODO fix to return an actual Transform
    @property
    def inv(self):
        def inverse_transform(other: Transform):
            return Transform(
                translation = (other._translation - self._translation)/self.scale,
                scale = other.scale/self.scale,
                rotation = -self.rotation
                )
        return inverse_transform
    



class Color(Lazible):

    PALETTE: dict[str, Rgb] = {
    "dark_slate": Rgb(*[28, 28, 28]),
    "soft_blue": Rgb(*[173, 216, 230]),
    "vibrant_orange": Rgb(*[255, 165, 0]),
    "pale_green": Rgb(*[144, 238, 144]),
    "bright_yellow": Rgb(*[255, 255, 0]),
    "steel_blue": Rgb(*[70, 130, 180]),
    "forest_green": Rgb(*[34, 139, 34]),
    "burnt_orange": Rgb(*[205, 127, 50]),
    "light_gray": Rgb(*[220, 220, 220]),
    "off_white": Rgb(*[245, 245, 220]),
    "medium_gray": Rgb(*[150, 150, 150]),
    "slate_gray": Rgb(*[112, 128, 144]),
    "crimson": Rgb(*[220, 20, 60]),
    "gold": Rgb(*[255, 215, 0]),
    "sky_blue": Rgb(*[135, 206, 235]),
    "light_coral": Rgb(*[240, 128, 128]),
    "red": Rgb(*[255, 99, 71]),
    "orange": Rgb(*[255, 165, 0]),
    "yellow": Rgb(*[255, 215, 0]),
    "green": Rgb(*[124, 252, 0]),
    "blue": Rgb(*[65, 105, 225]),
    "purple": Rgb(*[138, 43, 226]),
    "white": Rgb(*[255,255,255])
}

    def __init__(self, color: str | Sequence[int] | Self = "off_white", opacity: float = 1.0):

        self.opacity: float = color.opacity if isinstance(color, Color) else opacity
        self._rgb: Rgb

        if isinstance(color, Color):
            self._rgb = deepcopy(color._rgb)
        elif isinstance(color, Rgb):
            self._rgb = deepcopy(color)
        elif isinstance(color, str):
            self._rgb = Color.PALETTE[color]
        else: #elif isinstance(color, Sequence):
            self._rgb = Rgb(*color)
        

    def set_opacity(self, opacity: float) -> Self:
        self.opacity = opacity
        return self
    
    def set_rgb(self, rgb: str | Tuple[int,int,int]) -> Self:
        self.rgb = rgb
        return self


    @property
    def rgb(self) -> Rgb:
        return self._rgb
    
    @rgb.setter
    def rgb(self, value: str | Tuple[int, int, int]):
        if isinstance(value, str):
            self._rgb = Color.PALETTE[value]
        else:
            self._rgb = Rgb(*value)

    @property
    def svg_rgb(self):
        r,g,b = self._rgb
        return f"rgb({r},{g},{b})"

    def __str__(self) -> str:
        return f"Color(color={tuple(self._rgb)}, opacity={self.opacity}"