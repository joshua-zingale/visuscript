import numpy as np
from typing import Self
from ast import literal_eval

class Transform:

    def __init__(self, translation: np.ndarray | list = np.array([0.0,0.0,0.0]), scale: np.ndarray | list | float = np.array([1,1,1]), rotation: np.ndarray | list = 0.0):
        
        translation = list(translation)
        if len(translation) == 2:
            translation.append(0.0)
        translation = np.array(translation, dtype=float)


        if isinstance(scale, float) or isinstance(scale, int):
            scale = [scale, scale, 1.0]        
        scale = list(scale)
        if len(scale) == 2:
            scale.append(1.0)

        scale = np.array(scale, dtype=float)
        
        self.translation: np.ndarray = translation
        self.scale: np.ndarray = scale
        self.rotation: np.ndarray = rotation

    
    def copy(self):
        return Transform(translation=self.translation.copy(), scale=self.scale, rotation=self.rotation)

    def __str__(self):
        return f"Transform(translation={self.translation}, scale={self.scale}, rotation={self.rotation})"
    
    def __repr__(self):
        return str(self)

    def __call__(self, other: Self):
        return Transform(
            translation = other.translation * self.scale + self.translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
            )
    
    def __add__(self, other: Self):
        return Transform(
            translation = self.translation + other.translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
        )
    
    def __mul__(self, other: float):
        return Transform(
            translation = self.translation * other,
            scale = self.scale**other,
            rotation = self.rotation * other
        )
    def __rmul__(self, other: float):
        return self * other
    def __div__(self, other: float):
        return self * 1/other
    
    def interpolate(self, other: Self, alpha: float):
        np.clip(alpha, 0.0, 1.0)
        return self * (1-alpha) + other * alpha
    
    @property
    def inv(self):
        def inverse_transform(other: Transform):
            return Transform(
                translation = (other.translation - self.translation)/self.scale,
                scale = other.scale/self.scale,
                rotation = -self.rotation
                )
        return inverse_transform
    

    @property
    def scale_x(self) -> float:
        return float(self.scale[0])
    @property
    def scale_y(self) -> float:
        return float(self.scale[1])
    @property
    def scale_z(self) -> float:
        return float(self.scale[2])
    
    @scale_x.setter
    def scale_x(self, value):
        self.scale[0] = value
    @scale_y.setter
    def scale_y(self, value):
        self.scale[1] = value
    @scale_z.setter
    def scale_z(self, value):
        self.scale[2] = value
    
    @property
    def x(self) -> float:
        return float(self.translation[0])
    @property
    def y(self) -> float:
        return float(self.translation[1])
    @property
    def z(self) -> float:
        return float(self.translation[2])
    
    @x.setter
    def x(self, value):
        self.translation[0] = value
    @y.setter
    def y(self, value):
        self.translation[1] = value
    @z.setter
    def z(self, value):
        self.translation[2] = value



class Color():

    PALETTE: dict = {
        "red": np.array([255, 0, 0]),
        "orange": np.array([255, 165, 0]),
        "yellow": np.array([255, 255, 0]),
        "green": np.array([0, 128, 0]),
        "blue": np.array([0, 0, 255]),
        "indigo": np.array([75, 0, 130]),
        "violet": np.array([238, 130, 238]),
        "black": np.array([0, 0, 0]),
        "white": np.array([255, 255, 255]),
    }

    def __init__(self, color: str | np.ndarray | Self = "blue", opacity: float = 1.0):

        self.opacity: float = color.opacity if isinstance(color, Color) else opacity
        self._rgb: np.ndarray

        if isinstance(color, np.ndarray):
            assert len(color) == 3
            assert color.dtype == int
            self._rgb = color
        elif isinstance(color, Color):
            self._rgb = color._rgb
        elif isinstance(color, str) and color[:3] == "rgb":
            self._rgb = np.array(literal_eval(color[4:])).astype(int)
        elif isinstance(color, str):
            self._rgb = Color.PALETTE.get(color)
        else:
            raise TypeError(f"{type(color)} is not accepted.")


    @property
    def rgb(self) -> str:
        return str(self)

    def __str__(self) -> str:
        r,g,b = list(self._rgb)
        return f"rgb({r},{g},{b})"
    
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
    
    def __div__(self, other: float) -> Self:
        color = (self._rgb / other).round().astype(int)
        return Color(color=color)

    
