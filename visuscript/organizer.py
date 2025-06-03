from visuscript.drawable import Drawable
from visuscript.primatives import Transform, Vec3
from typing import Collection, Tuple, Generator, Iterable, Iterator
from abc import ABC, abstractmethod
import numpy as np

class Organizer(ABC):
    """An Organizer maps integer indices to Transforms."""

    @abstractmethod
    def __len__(self) -> int:
        """The maximum number of drawables that can be organized by this Organizer."""
        ...
    
    @abstractmethod
    def __getitem__(self, index: int) -> Transform:
        """Gets a Transform for a given index."""
        ...

    def __iter__(self) -> Iterator[Transform]:
        """Iterates over all Transform objects herein contained in order."""
        for i in range(len(self)):
            yield self[i]

    def organize(self, drawables: Iterable[Drawable | None]):
        """
        Applies transformations to at most len(self) of the input drawables
        
        The first Drawable in drawables is transformed with self[0]', the second with self[1] etc.
        """
        for drawable, transform in zip(drawables, self):
            if drawable is None:
                continue
            drawable.set_transform(transform)


class GridOrganizer(Organizer):
    """GridOrganizer arranges its output Transform objects into a three dimensional grid."""

    def __init__(self, shape: Collection[int], sizes: Collection[int]):
        if len(shape) == 2:
            shape = tuple(shape) + (1,)
        elif len(shape) == 3:
            shape = tuple(shape)
        else:
            raise ValueError("shape must be of length 2 or 3")
        if len(sizes) == 2:
            sizes = tuple(sizes) + (1,)
        elif len(sizes) == 3:
            sizes = tuple(sizes)
        else:
            raise ValueError("sizes must be of length 2 or 3")

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
            raise ValueError("indices must be a tuple of length 2 or 3 or an int")
        
        for i, (index, size) in enumerate(zip(indices, self._shape)):
            if index >= size:
                raise IndexError(f"index {index} is out of bounds for axis {i} with size {size}")
        
        translation = [i * size for i, size in zip(indices, self._sizes)]

        translation = [translation[1], translation[0], translation[2]]

        return Transform(translation=translation)



class BinaryTreeOrganizer(Organizer):
    """BinaryTreeOrganizer arranges its Transform objects into a binary tree."""

    def __init__(self, *, num_levels: int, level_heights: float | Iterable[float], node_width: float):
        assert num_levels >= 1
        self._len = int(2**(num_levels) - 1)
        self._num_levels = num_levels
        
        if isinstance(level_heights, Iterable):
            self._heights = list(level_heights)
        else:
            self._heights = [level_heights * l for l in range(num_levels)]
   
        self._node_width = node_width

        self._leftmost = -(2**(num_levels-2) - 1/2)*self._node_width

    
    def __len__(self) -> int:
        return self._len
    
    
    def __getitem__(self, index: int) -> Transform:
        level = int(np.log2(index+1))
        row_index = index - 2**(level) + 1
        
        horizontal_separation = Vec3(self._node_width * 2**(self._num_levels - level - 1), 0, 0)

        start_x = self._leftmost + (2**(self._num_levels - level - 1) - 1) * self._node_width/2
        start_y = self._heights[level]
        start_of_row = Vec3(start_x, start_y, 0)
        return Transform(translation=start_of_row + row_index*horizontal_separation)
