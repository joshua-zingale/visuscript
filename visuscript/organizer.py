from visuscript.drawable import Drawable
from visuscript.primatives import Transform, Vec3, get_vec3
from typing import Collection, Tuple, Generator
from abc import ABC, abstractmethod
import sys

class Organizer(ABC):
    @abstractmethod
    def __len__(self) -> int:
        ...
    
    @abstractmethod
    def __getitem__(self, index: int) -> Transform:
        ...

    def __iter__(self) -> Generator[Transform]:
        for i in range(len(self)):
            yield self[i]

    def organize(self, drawables: Collection[Drawable]):
        for drawable, transform in zip(drawables, self):
            drawable.set_transform(transform)


class Grid(Organizer):
    def __init__(self, shape: Collection[int], sizes: Collection[int], offset: Vec3 = None):
        if len(shape) == 2:
            shape = tuple(shape) + (1,)
        elif len(shape) == 3:
            shape = tuple(shape)
        else:
            raise ValueError("`shape` must be of length 2 or 3")
        if len(sizes) == 2:
            sizes = tuple(sizes) + (1,)
        elif len(sizes) == 3:
            sizes = tuple(sizes)
        else:
            raise ValueError("`sizes` must be of length 2 or 3")

        self._offset = get_vec3(offset) if offset is not None else Vec3(0,0,0)
        self._offset[0], self._offset[1] = self._offset[1], self._offset[0]

        self._shape = shape
        self._sizes = sizes

    def __len__(self):
        return self._shape[0] * self._shape[1] * self._shape[2]

    def __getitem__(self, indices: int | Tuple[int, int] | Tuple[int, int, int]) -> Transform:
        if isinstance(indices, int):
            y = (indices // (self._shape[2] * self._shape[1]))
            x = (indices // self._shape[2]) % self._shape[1]
            z = indices % self._shape[2]
            indices = (y,x,z)
        elif len(indices) == 2:
            indices = tuple(indices) + (0,)
        elif len(indices) == 3:
            indices = tuple(indices)
        else:
            raise ValueError("`indices` must be a tuple of length 2 or 3 or an `int`")
        
        for i, (index, size) in enumerate(zip(indices, self._shape)):
            if index >= size:
                raise IndexError(f"index {index} is out of bounds for axis {i} with size {size}")
        
        translation = [i * size + self._offset[axis] for axis, (i, size) in enumerate(zip(indices, self._sizes))]

        translation = [translation[1], translation[0], translation[2]]

        return Transform(translation=translation)

