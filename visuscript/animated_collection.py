"""This module contains functionality for :class:`~AnimatedCollection`."""

from visuscript.animation import (
    NoAnimation,
    PathAnimation,
    AnimationBundle,
    TransformAnimation,
    LazyAnimation,
    Animation,
)
from visuscript.segment import Path
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.drawable.text import Text
from visuscript.organizer import BinaryTreeOrganizer, Organizer, GridOrganizer
from visuscript.drawable import Circle, Pivot, Rect
from visuscript.primatives import Transform
from visuscript.primatives.mixins import Drawable
from visuscript.primatives.protocols import HasShape, HasTransform, CanBeDrawn
from visuscript.math_utility import magnitude
from visuscript.drawable.connector import Edges

from abc import abstractmethod
from visuscript.primatives import Vec2
from typing import (
    Collection,
    Iterable,
    MutableSequence,
    Self,
    Any,
    Tuple,
    no_type_check,
    overload,
    TypeVar,
    Generic,
    Protocol,
)


import numpy as np


# TODO find a way to do type checking correctly
@no_type_check
class Var:
    """An immutable wrapper around any other type: the foundational bit of data to be stored in an :class:`AnimatedCollection`."""

    @no_type_check
    def __init__(self, value: Any, *, type_: type | None = None):
        """
        :param value: The value to be stored.
        :type value: Any
        :param type_: The type of the stored value.
            If None, which is the default, the type is of the value is inferred;
            else, the stored value is cast to this parameter's argument.
        :type type_: type | None, optional
        """

        if isinstance(value, Var):
            self._value = value.value
            self._type = value._type
            return

        if type_ is None:
            type_ = type(value)

        if value is None and type_ is type(None):
            self._value = None
        else:
            self._value = type_(value)

        self._type = type_

    @property
    @no_type_check
    def value(self) -> Any:
        """The value stored in this :class:`Var`."""
        return self._value

    @property
    @no_type_check
    def is_none(self) -> bool:
        """True if and only if None is the value stored herein."""
        return self.value is None

    @no_type_check
    def __add__(self, other: "Var") -> "Var":
        value = self.value + other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __sub__(self, other: "Var") -> "Var":
        value = self.value - other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __mul__(self, other: "Var") -> "Var":
        value = self.value * other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __truediv__(self, other: "Var") -> "Var":
        value = self.value / other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __mod__(self, other: "Var") -> "Var":
        value = self.value % other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __floordiv__(self, other: "Var") -> "Var":
        value = self.value // other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __pow__(self, other: "Var") -> "Var":
        value = self.value**other.value
        type_ = type(value)
        return Var(value, type_=type_)

    @no_type_check
    def __gt__(self, other: "Var") -> bool:
        return self.value > other.value

    @no_type_check
    def __ge__(self, other: "Var") -> bool:
        return self.value >= other.value

    @no_type_check
    def __eq__(self, other: "Var") -> bool:
        return self.value == other.value

    @no_type_check
    def __le__(self, other: "Var") -> bool:
        return self.value <= other.value

    @no_type_check
    def __lt__(self, other: "Var") -> bool:
        return self.value < other.value

    @no_type_check
    def __str__(self):
        return f"Var({self.value}, type={self._type.__name__})"

    @no_type_check
    def __repr__(self):
        return str(self)

    @no_type_check
    def __bool__(self):
        return self.value is not None and self.value is not False


NilVar = Var(None)
"""A :class:`Var` representing no value."""


class CollectionDrawable(HasShape, HasTransform, CanBeDrawn, Protocol):
    pass


T = TypeVar("T", bound=CollectionDrawable)


class _AnimatedCollectionDrawable(Drawable):
    def __init__(self, animated_collection: "AnimatedCollection[T]"):
        super().__init__()
        self._animated_collection = animated_collection

    def draw(self):
        return "".join(
            element.draw() for element in self._animated_collection.all_elements
        )


class AnimatedCollection(Generic[T], Collection[Var]):
    """Stores data in form of :class:`Var` instances alongside corresponding :class:`~visuscript.element.Element` instances
    and organizational functionality to transform the :class:`~visuscript.element.Element` instances according to the rules of the given :class:`AnimatedCollection`.
    """

    @abstractmethod
    def element_for(self, var: Var) -> T:
        """Returns the :class:`CollectionDrawable` for a :class:`Var` stored in this collection."""
        ...

    @abstractmethod
    def target_for(self, var: Var) -> Transform:
        """Returns the :class:`~visuscript.primatives.Transform` that the input :class:`Var`'s :class:`~visuscript.element.Element`
        should have to be positioned according to this :class:`AnimatedCollection`'s rules.
        """
        ...

    def organize(
        self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
    ) -> AnimationBundle:
        """Returns an :class:`~visuscript.animation.Animation` that positions all of the :class:`~visuscript.element.Element` instances
        corresponding to :class:`Var` instances in this :class:`AnimatedCollection` according to its rules."""
        animation_bundle = AnimationBundle(NoAnimation(duration=duration))
        for var in self:
            animation_bundle << TransformAnimation(
                self.element_for(var).transform, self.target_for(var), duration=duration
            )  # type: ignore[reportUnusedExpression]
        return animation_bundle

    @property
    def elements(self) -> Iterable[T]:
        """An iterable over the :class:`~visuscript.element.Element` instances managed by this collection
        that correspond to the :class:`Var` instances stored herein."""
        for var in self:
            yield self.element_for(var)

    @property
    def all_elements(self) -> Iterable[CanBeDrawn]:
        """An iterable over all :class:`~visuscript.element.Element` instances that comprise
        this :class:`AnimatedCollection`'s visual component."""
        yield from self.auxiliary_elements
        yield from self.elements

    @property
    def collection_element(self) -> CanBeDrawn:
        """A :class:`~visuscript.drawable.Drawable` that, when drawn,
        draws all :class:`~visuscript.element.Element` instances that comprise this
        :class:`AnimatedCollection`'s visual component."""
        return _AnimatedCollectionDrawable(self)

    @property
    def auxiliary_elements(self) -> list[CanBeDrawn]:
        """A list of all auxiliary :class:`~visuscript.element.Element` instances that comprise this
        :class:`AnimatedCollection`'s visual component.
        """
        if not hasattr(self, "_auxiliary_elements"):
            self._auxiliary_elements: list[CanBeDrawn] = []
        return self._auxiliary_elements

    def add_auxiliary_element(self, element: CanBeDrawn) -> Self:
        """Adds an :class:`~visuscript.element.Element` to de displayed along with the :class:`~visuscript.element.Element`
        instances that correspond to the :class:`Var` instances stored herein."""
        self.auxiliary_elements.append(element)
        return self

    def remove_auxiliary_element(self, element: CanBeDrawn) -> Self:
        """Removes an auxiliar element form this :class:`AnimatedCollection`."""
        self.auxiliary_elements.remove(element)
        return self


class AnimatedList(AnimatedCollection[T], MutableSequence[Var]):
    def __init__(
        self, variables: Iterable[Var] = [], *, transform: Transform | None = None
    ):
        self._transform = Transform() if transform is None else Transform(transform)
        self._vars: list[Var] = []
        self._elements: list[T] = []
        for var in variables:
            self.insert(len(self), var).finish()

    @property
    def elements(self) -> list[T]:
        return list(self._elements)

    @property
    def transform(self) -> Transform:
        return self._transform

    @abstractmethod
    def new_element_for(self, var: Var) -> T:
        """Initializes and returns an :class:`~visuscript.element.Element` for a :class:`Var` newly inserted into this :class:`AnimatedList`."""
        ...

    @property
    def organizer(self) -> Organizer:
        return self.get_organizer()

    @abstractmethod
    def get_organizer(self) -> Organizer:
        """Initializes and returns an :class:`~visuscript.organizer.Organizer` for this :class:`AnimatedList`.
        The returned :class:`~visuscript.organizer.Organizer` sets the rule for how `animated_list[i]` should
        be transformed with `organizer[i]`.
        """
        ...

    def target_for(self, var: Var) -> Transform:
        return self._transform(self.organizer[self.is_index(var)])

    def element_for(self, var: Var) -> T:
        if var not in self._vars:
            raise ValueError(
                f"Var {var} is not present in this {self.__class__.__name__}"
            )
        return self._elements[self.is_index(var)]

    def __len__(self):
        return len(self._vars)

    @overload
    def __getitem__(self, index: int) -> Var: ...
    @overload
    def __getitem__(self, index: slice) -> list[Var]: ...
    def __getitem__(self, index: int | slice):
        return self._vars[index]

    @overload
    def __setitem__(self, index: int, value: Var) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[Var]) -> None: ...

    def __setitem__(self, index: int | slice, value: Var | Iterable[Var]) -> None:
        if not isinstance(value, Iterable):
            value = [value]
        if not isinstance(index, slice):
            index = slice(index, index + 1, 1)

        for idx, var in zip(range(index.start, index.stop, index.step), value):
            if self.is_contains(var):
                raise ValueError(
                    f"Cannot have the same Var in this AnimatedList twice."
                )
            self._vars[idx] = var
            self._elements[idx] = self.new_element_for(var)

    def __delitem__(self, index: int | slice):
        del self._vars[index]
        del self._elements[index]

    def insert(  # type: ignore
        self,
        index: int,
        value: Var,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        if self.is_contains(value):
            raise ValueError(f"Cannot have the same Var in this AnimatedList twice.")
        self._vars.insert(index, value)
        self._elements.insert(index, self.new_element_for(value))
        return self.organize(duration=duration)

    def _swap(self, a: int | Var, b: int | Var):
        if isinstance(a, Var):
            a = self.is_index(a)
        if isinstance(b, Var):
            b = self.is_index(b)

        element_a = self.element_for(self[a])
        element_b = self.element_for(self[b])

        tmp = self._vars[a]
        self._vars[a] = self._vars[b]
        self._vars[b] = tmp

        tmp = self._elements[a]
        self._elements[a] = self._elements[b]
        self._elements[b] = tmp
        return element_a, element_b

    def swap(self, a: int | Var, b: int | Var) -> Animation:
        """Swaps the :class:`Var` instances stored at the input indices.

        If :class:`Var` is used instead of an index, the index herein of :class:`Var` is used for the index.

        :param a: The first swap index or a specific Var.
        :type a: int | Var
        :param b: The second swap index or a specific Var.
        :type b: int | Var
        :return: An Animation linearly swapping each :class:`Var`'s :class:`~visuscript.element.Element`'s respective :class:`~visuscript.primatives.Transform`.
        :rtype: Animation
        """
        if a == b:
            return NoAnimation()

        element_a, element_b = self._swap(a, b)

        return AnimationBundle(
            TransformAnimation(element_a.transform, element_b.transform),
            TransformAnimation(element_b.transform, element_a.transform),
        )

    def quadratic_swap(
        self,
        a: int | Var,
        b: int | Var,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Swaps the :class:`Var` instances stored at the input indices.

        If :class:`Var` is used instead of an index, the index herein of :class:`Var` is used for the index.

        :param a: The first swap index or a specific Var.
        :type a: int | Var
        :param b: The second swap index or a specific Var.
        :type b: int | Var
        :return: An Animation along a quadratic curve swapping each :class:`Var`'s :class:`~visuscript.element.Element`'s respective :class:`~visuscript.primatives.Transform`.
        :rtype: Animation
        """
        if a == b:
            return NoAnimation(duration=duration)

        element_a, element_b = self._swap(a, b)

        def get_quadratic_swap():
            diff = (
                element_b.transform.translation.xy - element_a.transform.translation.xy
            )
            distance = magnitude(diff)
            direction = diff / distance
            ortho = Vec2(-direction.y, direction.x)

            mid = element_a.transform.translation.xy + direction * distance / 2
            lift = ortho * element_a.shape.circumscribed_radius * 2

            return AnimationBundle(
                PathAnimation(
                    element_a.transform,
                    Path()
                    .M(*element_a.transform.translation.xy)
                    .Q(*(mid - lift), *element_b.transform.translation.xy),
                    duration=duration,
                ),
                PathAnimation(
                    element_b.transform,
                    Path()
                    .M(*element_b.transform.translation.xy)
                    .Q(*(mid + lift), *element_a.transform.translation.xy),
                    duration=duration,
                ),
            )

        return LazyAnimation(get_quadratic_swap)

    def extend(  # type: ignore
        self,
        values: Iterable[Var],
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        super().extend(values)
        return self.organize(duration=duration)

    def is_index(self, var: Var) -> int:
        """Returns the index herein for a specific :class:`Var`, not just a :class:`Var` with an equivalent value.

        :param var: The :class:`Var` for which the index is to be found.
        :type var: Var
        :raises ValueError: If the input :class:`Var` is not herein contained.
        :return: The index.
        :rtype: int
        """
        try:
            return list(map(lambda x: x is var, self)).index(True)
        except ValueError:
            raise ValueError(f"Var is not present in this {self.__class__.__name__}.")

    def is_contains(self, var: Var) -> bool:
        """Returns True if a specific :class:`Var`, not just a :class:`Var` with an equivalent value, is herein contained."""
        return sum(map(lambda x: x is var, self)) > 0


class AnimatedBinaryTreeArray(AnimatedList[Pivot | Circle]):
    def __init__(
        self,
        variables: Iterable[Var],
        *,
        radius: float,
        level_heights: float | None = None,
        node_width: float | None = None,
        transform: Transform | None = None,
    ):
        self._radius = radius
        self.level_heights = level_heights or 3 * radius
        self.node_width = node_width or 3 * radius

        self._edges = Edges()
        self.add_auxiliary_element(self._edges)

        super().__init__(variables, transform=transform)

    @property
    def edges(self):
        return self._edges

    def get_organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(
            num_levels=num_levels,
            level_heights=self.level_heights,
            node_width=self.node_width,
        )

    def new_element_for(self, var: Var) -> Circle | Pivot:
        if var.is_none:
            return Pivot()
        n = Circle(radius=self._radius).add_child(
            Text(str(var.value), font_size=self._radius)
        )
        return n

    def get_parent_index(self, var: int | Var):
        if isinstance(var, int):
            var = self[var]
        return int((self.is_index(var) + 1) // 2) - 1

    def get_left_index(self, var: int | Var):
        if isinstance(var, int):
            var = self[var]
        return int((self.is_index(var) + 1) * 2) - 1

    def get_right_index(self, var: int | Var):
        return self.get_left_index(var) + 1

    @property
    def root(self) -> Var:
        return self[0]

    def get_parent(self, var: Var) -> Var:
        idx = self.get_parent_index(var)

        if idx < 0:
            return NilVar

        return self[idx]

    def get_left(self, var: Var) -> Var:
        idx = self.get_left_index(var)

        if idx >= len(self):
            return NilVar

        return self[idx]

    def get_right(self, var: Var) -> Var:
        idx = self.get_right_index(var)

        if idx >= len(self):
            return NilVar

        return self[idx]

    def is_root(self, var: Var) -> bool:
        return self.root is var

    def is_child(self, var: Var) -> bool:
        return not self.get_parent(var).is_none

    def is_leaf(self, var: Var) -> bool:
        return self.get_left(var).is_none and self.get_right(var).is_none

    def number_of_children(self, var: Var) -> int:
        return int((not self.get_left(var).is_none) + (not self.get_right(var).is_none))

    def get_children(self, var: Var):
        return map(lambda x: not x.is_none, [self.get_left(var), self.get_right(var)])


class AnimatedArray(AnimatedList[Text]):
    def __init__(
        self,
        variables: Iterable[Var],
        font_size: float,
        transform: Transform | None = None,
    ):
        variables = list(variables)
        self._max_length = len(variables)
        self._font_size = font_size
        super().__init__(variables, transform=transform)
        for transform in self.organizer:
            self.add_auxiliary_element(
                Rect(font_size, font_size).set_transform(self.transform @ transform)
            )

    def get_organizer(self):
        return GridOrganizer((1, len(self)), (self._font_size, self._font_size))

    def new_element_for(self, var: Var) -> Text:
        return Text(f"{var.value}", font_size=self._font_size)

    def insert(
        self,
        index: int,
        value: Var,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ):
        if len(self) == self._max_length:
            raise ValueError(
                "Cannot insert a Var into an AnimatedArray that is already at its maximal length."
            )
        return super().insert(index, value, duration=duration)


class AnimatedArray2D(AnimatedArray):
    def __init__(
        self,
        variables: Iterable[Var],
        font_size: float,
        shape: Tuple[int, int],
        transform: Transform | None = None,
    ):
        self._shape = shape
        super().__init__(variables, font_size, transform=transform)

    def _tuple_to_index(self, index: Tuple[int, int]):
        for axis, (idx, size) in enumerate(zip(index, self._shape)):
            if idx >= size:
                raise IndexError(
                    f"Index {idx} is too large for axis {axis} of size {size}."
                )

        return index[0] * self._shape[1] + index[1]

    @overload
    def __getitem__(self, index: int) -> Var: ...
    @overload
    def __getitem__(self, index: slice) -> list[Var]: ...
    def __getitem__(self, index: int | slice | Tuple[int, int]) -> Var | list[Var]:
        if isinstance(index, (int, slice)):
            return super()[index]
        return super()[self._tuple_to_index(index)]

    def insert(
        self,
        index: int | Tuple[int, int],
        value: Var,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        if isinstance(index, Tuple):
            index = self._tuple_to_index(index)
        return super().insert(index, value, duration=duration)

    def get_organizer(self):
        return GridOrganizer(self._shape, (self._font_size, self._font_size))
