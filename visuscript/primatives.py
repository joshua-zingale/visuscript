import numpy as np
from typing import Self, Collection, Tuple, Generator, Type, Sequence, Callable, Iterable, Iterator
from operator import add, mul, sub, truediv, neg, pow, eq
from array import array
from copy import deepcopy


class SizeMismatch(ValueError):
    def __init__(self, size1: int, size2: int, operation: str):
        super().__init__(f"Size mismatch for {operation}: Size {size1} is not compatible with Size {size2}.")

#TODO Add support for arbitrary dimensions in a base class, which can be used for matrices etc later
class Vec(Sequence[float]):

    def __init__(self, *args):
        self._arr = array('d', [*args])

    # @staticmethod
    # def size_check(operation):
    #     def size_check_function(self, other):
    #         if len(self) != len(other):
    #             raise SizeMismatch(len(self, len(other), operation))
    #         return operation(self, other)
    #     return size_check_function
    
    def _element_wise(self, operation: Callable[[float, float], float], other: "Vec"):
        if not hasattr(other, "__len__"):
            return self.__class__(*(operation(s, other) for s in self))
        
        if len(self) != len(other):
            raise SizeMismatch(len(self), len(other), f"__{operation.__name__}__")
        
        return self.__class__(*(operation(s, o) for s,o in zip(self, other)))

    def dot(self, other: "Vec") -> float:
        prods = self._element_wise(mul, other)
        return sum(prods)

    def __getitem__(self, index: int | slice) -> float:
        if isinstance(index, slice):
            return Vec(*self._arr[index])
        return self._arr[index]

    def __len__(self) -> int:
        return len(self._arr)

    def __eq__(self, other: "Vec") -> Self:
        return sum(self._element_wise(eq, other)) == len(self)
        
    def __matmul__(self, other) -> Self:
        return self.__class__(*np.matmul(self, other))
    def __rmatmul__(self, other):
        return self.__class__(*np.matmul(other, self))
    
    def __add__(self, other: "Vec") -> Self:
        return self._element_wise(add, other)
    def __radd__(self, other: "Vec") -> Self:
        return self._element_wise(add, other)
    
    def __sub__(self, other: "Vec") -> Self:
        return self._element_wise(sub, other)
    def __rsub__(self, other: "Vec") -> Self:
        vec = self.__class__(*map(lambda x: -x, self))
        return vec._element_wise(add, other)

    def __mul__(self, other: "Vec") -> Self:
        return self._element_wise(mul, other)
    def __rmul__(self, other: "Vec") -> Self:
        return self._element_wise(mul, other)
    
    def __truediv__(self, other: "Vec") -> Self:
        return self._element_wise(truediv, other)
    def __rtruediv__(self, other: "Vec") -> Self:
        vec = self.__class__(*map(lambda x: 1/x, self))
        return vec._element_wise(mul, other)
    
    def __pow__(self, other: "Vec") -> Self:
        return self._element_wise(pow, other)
    # def __rpow__(self, other: "Vec") -> Self:
    #     vec = self.__class__(*map(lambda x: 1/x, self))
    #     return vec._element_wise(mul, other)
    
    def __neg__(self) -> Self:
        return self.__class__(*map(neg, self))
    

    def __str__(self):
        return f"Vec{(*self,)}"
    def __repr__(self):
        return str(self)
    
    def astype(self, type: Type):
        return list(map(type, self))


    def max(self):
        return max(self)


class Vec2(Vec):
    def __init__(self, x: float, y: float):
        super().__init__(x,y)

    def extend(self, z: float):
        """Get a Vec3 with the same x,y as this Vec2, where the parameter sets z."""
        return Vec3(*self, z)
    
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

# class Vec3(np.ndarray):

#     def __new__(cls, x: float, y: float, z: float):
#         obj = super().__new__(cls, (3,), dtype=float)
#         obj[:] = x,y,z
#         return obj
    
#     @property
#     def x(self) -> float:
#         return self[0]

#     @x.setter
#     def x(self, value: float):
#         self[0] = value

#     @property
#     def y(self) -> float:
#         return self[1]

#     @y.setter
#     def y(self, value: float):
#         self[1] = value

#     @property
#     def z(self) -> float:
#         return self[2]

#     @z.setter
#     def z(self, value: float):
#         self[2] = value

#     @property
#     def xy(self) -> Vec2:
#         """
#         Get a Vec2 with the same first and second value as this Vec3.
#         """
#         return Vec2(*self[:2])
    
#     @xy.setter
#     def xy(self, other: Collection):
#         assert len(other) == 2
#         self[:2] = other

#     def __matmul__(self, other):
#         return self.view(np.ndarray).__matmul__(other.view(np.ndarray))
#     def __rmatmul__(self, other):
#         return self.view(np.ndarray).__rmatmul__(other.view(np.ndarray))

#     # These are added to help intellisense
#     def __mul__(self, other) -> Self:
#         return super().__mul__(other)
#     def __rmul__(self, other) -> Self:
#         return super().__rmul__(other)
#     def __truediv__(self, other) -> Self:
#         return super().__truediv__(other)
#     def __rtruediv__(self, other) -> Self:
#         return super().__rtruediv__(other)
#     def __floordiv__(self, other) -> Self:
#         return super().__floordiv__(other)
#     def __rfloordiv__(self, other) -> Self:
#         return super().__rfloordiv__(other)
#     def __sub__(self, other) -> Self:
#         return super().__sub__(other)
#     def __rsub__(self, other) -> Self:
#         return super().__rsub__(other)
#     def __add__(self, other) -> Self:
#         return super().__add__(other)
#     def __radd__(self, other) -> Self:
#         return super().__radd__(other)


class Rgb:
    def __init__(self, r: int, g: int, b: int):
        for v in [r,g,b]:
            if not isinstance(v, int):
                raise TypeError("RGB values must be of type int")
            if v < 0 or v > 255:
                raise ValueError(f"{v} is not a valid RGB value. RGB values must be between 0 and 255, includsive.")
        self._rgb: list[int] = [r,g,b]
    def interpolate(self, other: "Rgb", alpha: float):
        assert 0 <= alpha and alpha <= 1
        return Rgb(*( round(s*(1-alpha) + o*alpha) for s,o in zip(self._rgb, other._rgb) ))
    
    def __iter__(self) -> Iterator[int]:
        yield from self._rgb

    def __add__(self, other: Self) -> Self:
        return Rgb(*[min(s+o,255) for s,o in zip(self._rgb, other._rgb)])
    
    def __mul__(self, other: float) -> Self:
        return Rgb(*[min(int(s*other),255) for s in self._rgb])
    def __rmul__(self, other: float) -> Self:
        return self * other
    def __truediv__(self, other: float) -> Self:
        return self * (1/other)


def get_vec3(values: Collection[float], z_fill: float = 0.0) -> Vec3:
    if not isinstance(values, Collection):
        raise TypeError(f"Cannot make Vec3 out of {type(values)}")
    
    if len(values) == 2:
        return Vec3(*values, z_fill)
    elif len(values) == 3:
        return Vec3(*values)
    else:
        raise ValueError(f"Cannot make Vec3 out of collection of length {len(values)}. Must be of length 2 or 3.")


class Transform:

    def __init__(self, translation: Vec2 | Vec3 | list | Self = [0,0,0], scale: Vec2 | Vec3 | list | float = [1,1,1], rotation: float = 0.0):
        
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


    @property
    def rotation(self):
        return deepcopy(self._rotation)
    
    @rotation.setter
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
    def translation(self, value: Vec2 | Vec3 | Collection[float]):
        assert 2 <= len(value) and len(value) <= 3

        value = get_vec3(value, z_fill=self.translation.z)

        self._translation = value


    @property
    def scale(self) -> Vec3:
        return deepcopy(self._scale)
    
    @scale.setter
    def scale(self, value: int | float | Collection[float]):
        if not isinstance(value, Collection):
            self._scale = Vec3(value, value, 1.0)
            return

        assert 2 <= len(value) and len(value) <= 3

        if len(value) == 2:
            self._scale.xy = value
        else:
            self._scale = value


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
        return f"translate({" ".join(self.translation[:2].astype(str))}) scale({" ".join(self.scale[:2].astype(str))}) rotate({self.rotation})"
    
    def __str__(self):
        return self.svg_transform
    
    def __repr__(self):
        return str(self)

    def __call__(self, other: Self | Vec2 | Vec3) -> Self | Vec2 | Vec3:
        return self @ other
    
    def __matmul__(self, other: Self | Vec2 | Vec3) -> Self | Vec2 | Vec3:
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
    
    def interpolate(self, other: Self, alpha: float):
        return Transform(
            translation = self.translation * (1 - alpha) + other.translation * alpha,
            scale = self.scale * (1 - alpha) + other.scale * alpha,
            rotation = self.rotation * (1 - alpha) + other.rotation * alpha
        )
    
    def update(self, other: Self):
        self.translation = other.translation
        self.scale = other.scale
        self.rotation = other.rotation
    
    @property
    def inv(self):
        def inverse_transform(other: Transform):
            return Transform(
                translation = (other._translation - self._translation)/self.scale,
                scale = other.scale/self.scale,
                rotation = -self.rotation
                )
        return inverse_transform
    



class Color():

    PALETTE: dict = {
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

    def __init__(self, color: str | Collection[int] | Self = "off_white", opacity: float = 1.0):

        self.opacity: float = color.opacity if isinstance(color, Color) else opacity
        self._rgb: Rgb

        if isinstance(color, Color):
            self._rgb = deepcopy(color._rgb)
        elif isinstance(color, str):
            self._rgb = Color.PALETTE[color]
        elif isinstance(color, Collection):
            assert len(color) == 3, f"length was {len(color)}"
            self._rgb = Rgb(*color, dtype=int)
        else:
            raise TypeError(f"{type(color)} is not accepted.")
        

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
            value = Color.PALETTE[value]
        self._rgb = value

    @property
    def svg_rgb(self):
        r,g,b = self._rgb
        return f"rgb({r},{g},{b})"

    def __str__(self) -> str:
        return f"Color(color={tuple(self._rgb)}, opacity={self.opacity}"
    
    def __add__(self, other: Self) -> Self:
        color = (self._rgb + other._rgb).clip(0,255)
        return Color(color=color)
    
    def __sub__(self, other: Self) -> Self:
        color = (self._rgb - other._rgb).clip(0,255)
        return Color(color=color)
    
    def __mul__(self, other: float) -> Self:
        color = (self._rgb * other).round().astype(int)
        return Color(color=color)
    
    def __rmul__(self, other: float) -> Self:
        return self * other
    
    def __truediv__(self, other: float) -> Self:
        color = (self._rgb / other).round().astype(int)
        return Color(color=color)