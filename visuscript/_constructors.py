from visuscript.primatives import Vec2, Vec3
from typing import Iterable

def construct_vec3(value: int | float | Iterable[int | float] | None, z = None) -> Vec3 | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return Vec3(value, value, z)
    if isinstance(value, Iterable):
        value = list(value)
        if len(value) == 2:
            return Vec3(*value, z)
        return Vec3(*value)
    raise ValueError(f"Cannot construct a Vec3 out of '{value}'")



