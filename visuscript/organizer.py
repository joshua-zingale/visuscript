"""Contains :class:`Organizer` types for arranging displayable objects."""

from visuscript.mixins import TransformMixin
from visuscript.primatives import Transform, Vec2
from typing import Iterable, Iterator
from abc import ABC, abstractmethod
import numpy as np


class Organizer(ABC, TransformMixin):
    """An Organizer maps integer indices to Transforms."""

    @abstractmethod
    def __len__(self) -> int:
        """The maximum number of drawables that can be organized by this Organizer."""
        ...

    @abstractmethod
    def transform_for(self, index: int) -> Transform:
        """Gets a Transform for a given index.

        Note that implementors of this base class should NOT transform the output by this :class:`Organizer`'s transform."""
        ...

    def __getitem__(self, index: int) -> Transform:
        """Gets a Transform for a given index that is transformed by this :class:`Organizer`'s transform."""
        return self._transform(self.transform_for(index))

    def __iter__(self) -> Iterator[Transform]:
        """Iterates over all Transform objects herein contained in order."""
        for i in range(len(self)):
            yield self[i]

    def organize(self, drawables: Iterable[TransformMixin | None]):
        """
        Applies transformations to at most len(self) of the input drawables

        The first Drawable in drawables is transformed with self[0]', the second with self[1] etc.
        """
        for drawable, transform in zip(drawables, self):
            if drawable is None:
                continue
            drawable.set_transform(transform)


class GridOrganizer(Organizer):
    """GridOrganizer arranges its output Transform objects into a two dimensional grid."""

    def __init__(self, ushape: tuple[int, int], sizes: tuple[float, float]):
        super().__init__()
        self._ushape = ushape
        self._sizes = sizes

    def __len__(self):
        return self._ushape[0] * self._ushape[1]

    def transform_for(self, index: int | tuple[int, int]) -> Transform:
        indices = index
        if isinstance(indices, int):
            y = (indices // self._ushape[1]) % self._ushape[0]
            x = indices % self._ushape[1]
            indices = (y, x)

        for i, (index, size) in enumerate(zip(indices, self._ushape)):
            if index >= size:
                raise IndexError(
                    f"index {index} is out of bounds for axis {i} with size {size}"
                )

        translation = [i * size for i, size in zip(indices, self._sizes)]

        translation = [translation[1], translation[0]]

        return Transform(translation=translation)


class BinaryTreeOrganizer(Organizer):
    """BinaryTreeOrganizer arranges its Transform objects into a binary tree."""

    def __init__(
        self,
        *,
        num_levels: int,
        level_heights: float | Iterable[float],
        node_width: float,
    ):
        super().__init__()
        assert num_levels >= 1
        self._len = int(2 ** (num_levels) - 1)
        self._num_levels = num_levels

        if isinstance(level_heights, Iterable):
            self._heights = list(level_heights)
        else:
            self._heights = [level_heights * l for l in range(num_levels)]

        self._node_width = node_width

        self._leftmost = -(2 ** (num_levels - 2) - 1 / 2) * self._node_width

    def __len__(self) -> int:
        return self._len

    def transform_for(self, index: int) -> Transform:
        level = int(np.log2(index + 1))
        row_index = index - 2 ** (level) + 1

        horizontal_separation = Vec2(
            self._node_width * 2 ** (self._num_levels - level - 1), 0
        )

        start_x = (
            self._leftmost
            + (2 ** (self._num_levels - level - 1) - 1) * self._node_width / 2
        )
        start_y = self._heights[level]
        start_of_row = Vec2(start_x, start_y)
        return Transform(translation=start_of_row + row_index * horizontal_separation)
