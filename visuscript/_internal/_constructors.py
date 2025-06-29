from visuscript.primatives import Vec3
from typing import Iterable, overload


@overload
def construct_vec3(
    value: int | float | Iterable[int | float], z: int | float = 0
) -> Vec3: ...
@overload
def construct_vec3(value: None, z: int | float = 0) -> None: ...
def construct_vec3(
    value: int | float | Iterable[int | float] | None, z: int | float = 0
) -> Vec3 | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return Vec3(value, value, z)
    value = list(value)
    if len(value) == 2:
        return Vec3(*value, z=z)
    return Vec3(*value)
