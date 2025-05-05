import numpy as np
from typing import Self
from ast import literal_eval
from .utility import ellipse_arc_length

class Transform:

    def __init__(self, translation: np.ndarray | list | Self = [0,0,0], scale: np.ndarray | list | float = [1,1,1], rotation: float = 0.0):
        
        if isinstance(translation, Transform):
            self.translation = translation.translation
            self.scale = translation.scale
            self.rotation = translation.rotation
            return 

        
        self.translation: np.ndarray = translation
        self.scale: np.ndarray = scale
        self.rotation: float = rotation




    @property
    def xy(self) -> np.ndarray:
        return np.array(self._translation[:2], dtype=float)

    @property
    def translation(self) -> np.ndarray:
        return np.array(self._translation, dtype=float)
    
    @translation.setter
    def translation(self, value: np.ndarray | list):
        assert 2 <= len(value) and len(value) <= 3
        value = list(value)
        if len(value) == 2:
            value.append(0.0)
        self._translation = np.array(value, dtype=float)


    @property
    def scale(self) -> np.ndarray:
        return self._scale
    
    @scale.setter
    def scale(self, value):
        scale = list(value)
        if len(scale) == 1:
            scale.append(value)
        if len(scale) == 2:
            scale.append(1.0)

        self._scale = np.array(scale, dtype=float)
        

    @property
    def pivot(self):
        if self._pivot == None:
            return self.translation
        else:
            return self._pivot

    def __str__(self):
        return f"translate({" ".join(self.translation[:2].astype(str))}) scale({" ".join(self.scale[:2].astype(str))}) rotate({self.rotation})"
    
    def __repr__(self):
        return str(self)

    def __call__(self, other: Self) -> Self:
        return self @ other
    
    def __matmul__(self, other: Self) -> Self:
        t = (self.rotation * np.pi/180)
        r_matrix = np.array([
            [np.cos(t), -np.sin(t),0],
            [np.sin(t), np.cos(t), 0],
            [0, 0, 1]
        ])
        return Transform(
            translation = r_matrix@(other._translation * self.scale) + self._translation,
            scale = self.scale * other.scale,
            rotation = self.rotation + other.rotation
            )
    
    def __add__(self, other: Self):
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
    
    @property
    def inv(self):
        def inverse_transform(other: Transform):
            return Transform(
                translation = (other._translation - self._translation)/self.scale,
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
        return float(self._translation[0])
    @property
    def y(self) -> float:
        return float(self._translation[1])
    @property
    def z(self) -> float:
        return float(self._translation[2])
    
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

    def __init__(self, color: str | np.ndarray | Self = "off_white", opacity: float = 1.0):

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
            self._rgb = Color.PALETTE[color]
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
    
    def __truediv__(self, other: float) -> Self:
        color = (self._rgb / other).round().astype(int)
        return Color(color=color)