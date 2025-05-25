import numpy as np
from typing import Self, Collection, Tuple
from copy import deepcopy
from ast import literal_eval

class Vec2(np.ndarray):

    def __new__(cls, x: float, y: float):
        obj = super().__new__(cls, (2,), dtype=float)
        obj[:] = x, y
        return obj

    def extend(self, z: float) -> "Vec3":
        """
        Get a Vec3 with the same first and second values and input `z` as the third value.
        """
        return Vec3(*self, z)
    
    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, value: float):
        self[0] = value

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, value: float):
        self[1] = value


    def __matmul__(self, other):
        return self.view(np.ndarray).__matmul__(other.view(np.ndarray))
    def __rmatmul__(self, other):
        return self.view(np.ndarray).__rmatmul__(other.view(np.ndarray))

    # These are added to help intellisense
    def __mul__(self, other) -> Self:
        return super().__mul__(other)
    def __rmul__(self, other) -> Self:
        return super().__rmul__(other)
    def __truediv__(self, other) -> Self:
        return super().__truediv__(other)
    def __rtruediv__(self, other) -> Self:
        return super().__rtruediv__(other)
    def __floordiv__(self, other) -> Self:
        return super().__floordiv__(other)
    def __rfloordiv__(self, other) -> Self:
        return super().__rfloordiv__(other)
    def __sub__(self, other) -> Self:
        return super().__sub__(other)
    def __rsub__(self, other) -> Self:
        return super().__rsub__(other)
    def __add__(self, other) -> Self:
        return super().__add__(other)
    def __radd__(self, other) -> Self:
        return super().__radd__(other)

class Vec3(np.ndarray):

    def __new__(cls, x: float, y: float, z: float):
        obj = super().__new__(cls, (3,), dtype=float)
        obj[:] = x,y,z
        return obj
    
    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, value: float):
        self[0] = value

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, value: float):
        self[1] = value

    @property
    def z(self) -> float:
        return self[2]

    @z.setter
    def z(self, value: float):
        self[2] = value

    @property
    def xy(self) -> Vec2:
        """
        Get a Vec2 with the same first and second value as this Vec3.
        """
        return Vec2(*self[:2])
    
    @xy.setter
    def xy(self, other: Collection):
        assert len(other) == 2
        self[:2] = other

    def __matmul__(self, other):
        return self.view(np.ndarray).__matmul__(other.view(np.ndarray))
    def __rmatmul__(self, other):
        return self.view(np.ndarray).__rmatmul__(other.view(np.ndarray))

    # These are added to help intellisense
    def __mul__(self, other) -> Self:
        return super().__mul__(other)
    def __rmul__(self, other) -> Self:
        return super().__rmul__(other)
    def __truediv__(self, other) -> Self:
        return super().__truediv__(other)
    def __rtruediv__(self, other) -> Self:
        return super().__rtruediv__(other)
    def __floordiv__(self, other) -> Self:
        return super().__floordiv__(other)
    def __rfloordiv__(self, other) -> Self:
        return super().__rfloordiv__(other)
    def __sub__(self, other) -> Self:
        return super().__sub__(other)
    def __rsub__(self, other) -> Self:
        return super().__rsub__(other)
    def __add__(self, other) -> Self:
        return super().__add__(other)
    def __radd__(self, other) -> Self:
        return super().__radd__(other)
        

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
            self.translation = translation.translation
            self.scale = translation.scale
            self.rotation = translation.rotation
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

    @property
    def translation(self) -> Vec3:
        return deepcopy(self._translation)
    
    @translation.setter
    def translation(self, value: Vec2 | Vec3 | Collection[float]):
        assert 2 <= len(value) and len(value) <= 3

        value = get_vec3(value)

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

    def __call__(self, other: Self) -> Self:
        return self @ other
    
    def __matmul__(self, other: Self | Vec2 | Vec3) -> Self | Vec2 | Vec3:
        t = (self.rotation * np.pi/180)
        r_matrix = np.array([
            [np.cos(t), -np.sin(t),0],
            [np.sin(t), np.cos(t), 0],
            [0, 0, 1]
        ])

        if isinstance(other, np.ndarray):
            vec3 = get_vec3(other)
            result = ((r_matrix@(vec3*self.scale)) + self._translation)

            if len(other) == 2:
                return result[:2].view(Vec2)
            if len(other) == 3:
                return result.view(Vec3)       

        return Transform(
            translation = r_matrix@(other._translation * self.scale) + self._translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
            )
    
    def __add__(self, other: Self):
        assert isinstance(other, Transform)
        return Transform(
            translation = self._translation + other._translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
        )
    
    def __mul__(self, other: float):
        return Transform(
            translation = self._translation * other,
            scale = self.scale**other,
            rotation = self.rotation * other
        )
    def __rmul__(self, other: float):
        return self * other
    def __truediv__(self, other: float):
        return self * (1/other)
    
    def interpolate(self, other: Self, alpha: float):
        np.clip(alpha, 0.0, 1.0)
        return self * (1-alpha) + other * alpha
    
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
    "dark_slate": np.array([28, 28, 28]),
    "soft_blue": np.array([173, 216, 230]),
    "vibrant_orange": np.array([255, 165, 0]),
    "pale_green": np.array([144, 238, 144]),
    "bright_yellow": np.array([255, 255, 0]),
    "steel_blue": np.array([70, 130, 180]),
    "forest_green": np.array([34, 139, 34]),
    "burnt_orange": np.array([205, 127, 50]),
    "light_gray": np.array([220, 220, 220]),
    "off_white": np.array([245, 245, 220]),
    "medium_gray": np.array([150, 150, 150]),
    "slate_gray": np.array([112, 128, 144]),
    "crimson": np.array([220, 20, 60]),
    "gold": np.array([255, 215, 0]),
    "sky_blue": np.array([135, 206, 235]),
    "light_coral": np.array([240, 128, 128]),
    "red": np.array([255, 99, 71]),
    "orange": np.array([255, 165, 0]),
    "yellow": np.array([255, 215, 0]),
    "green": np.array([124, 252, 0]),
    "blue": np.array([65, 105, 225]),
    "purple": np.array([138, 43, 226]),
    "white": np.array([255,255,255])
}

    def __init__(self, color: str | Collection[int] | Self = "off_white", opacity: float = 1.0):

        self.opacity: float = color.opacity if isinstance(color, Color) else opacity
        self._rgb: np.ndarray

        if isinstance(color, Color):
            self._rgb = color._rgb
        elif isinstance(color, str) and color[:3] == "rgb":
            self._rgb = np.array(literal_eval(color[4:])).astype(int)
        elif isinstance(color, str):
            self._rgb = Color.PALETTE[color]
        elif isinstance(color, Collection):
            assert len(color) == 3, f"length was {len(color)}"
            self._rgb = np.array(color, dtype=int)
        else:
            raise TypeError(f"{type(color)} is not accepted.")


    @property
    def rgb(self) -> str:
        return deepcopy(self._rgb)
    
    @rgb.setter
    def rgb(self, value: Tuple[int, int, int]):
        value = tuple(value)
        self._rgb[:] = value

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