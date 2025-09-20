"""This module contains functionality for :class:`~AnimatedCollection`."""

from visuscript.animation import (
    NoAnimation,
    AnimationBundle,
    TransformAnimation,
    LazyAnimation,
    Animation,
    OpacityAnimation,
    AnimationSequence,
    RunFunction,
    quadratic_swap,
)
from visuscript.primatives import TransformMixin
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.drawable.text import Text
from visuscript.organizer import Organizer, GridOrganizer
from visuscript.drawable import Pivot, Rect
from visuscript.primatives import Transform
from visuscript.primatives.mixins import Drawable
from visuscript.primatives.protocols import (
    HasShape,
    HasTransform,
    CanBeDrawn,
    HasOpacity,
    CanBeLazed,
)

from abc import abstractmethod, ABC
from typing import (
    Iterator,
    Iterable,
    Sequence,
    Self,
    Any,
    Tuple,
    no_type_check,
    overload,
    TypeVar,
    Generic,
    Protocol,
    TypeAlias,
)


# TODO find a way to do type checking correctly
@no_type_check
class Var:
    """An immutable wrapper around any other type: useful for storage in an :class:`AnimatedCollection`."""

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
        """The value stored in this `_T`."""
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


class CollectionDrawable(
    HasShape, HasTransform, CanBeDrawn, CanBeLazed, HasOpacity, Protocol
):
    """A protocol for a drawable object that can be the visual representation for an object in an :class:`AnimatedCollection`."""

    pass


class NullDrawable(Pivot):
    """A drawable object that draws nothing, useful as a :class:`CollectionDrawable` for Null types."""


AnyValue: TypeAlias = Any
_T = TypeVar("_T", bound=AnyValue)
_CollectionDrawable = TypeVar("_CollectionDrawable", bound=CollectionDrawable)
_V = TypeVar("_V")


class IdMap(Generic[_T, _V]):
    """A mapping from `_T` instances to arbitrary values.
    All keys are hashed according to their identity, not their value.

    .. note::
        This class is needed for types like `_T`, where instances are equalwhen their values are equal
        and sometimes the exact identity of such an instance should be the key to a map.

    """

    def __init__(self):
        self._map: dict[int, _V] = {}

    def __getitem__(self, key: _T) -> Any:
        return self._map[id(key)]

    def __setitem__(self, key: _T, value: _V) -> None:
        self._map[id(key)] = value

    def __contains__(self, key: _T) -> bool:
        return id(key) in self._map

    def __delitem__(self, key: _T) -> None:
        del self._map[id(key)]


class _AnimatedCollectionDrawable(Drawable):
    def __init__(
        self, animated_collection: "AnimatedCollection[_T, _CollectionDrawable]"
    ):
        super().__init__()
        self._animated_collection = animated_collection

    def draw(self):
        return "".join(
            drawable.draw() for drawable in self._animated_collection.all_drawables
        )


class AnimatedCollection(ABC, Generic[_T, _CollectionDrawable]):
    """Stores data in form of `_T` instances alongside corresponding :class:`CollectionDrawable` instances
    and organizational functionality to transform the ::class:`CollectionDrawable` instances according to the rules
    of the given :class:`AnimatedCollection`.
    """

    @abstractmethod
    def drawable_for(self, var: _T, /) -> _CollectionDrawable:
        """Returns the :class:`CollectionDrawable` for a `_T` stored in this collection.

        :param var: The `_T` for which the corresponding :class:`CollectionDrawable` is to be returned.
        :raises ValueError: If the input `_T` is not stored in this :class:`AnimatedCollection`.
        """
        ...

    @abstractmethod
    def set_drawable_for(self, var: _T, drawable: _CollectionDrawable, /) -> None:
        """Sets the :class:`CollectionDrawable` for a `_T` stored in this collection."""
        ...

    @abstractmethod
    def target_for(self, var: _T, /) -> Transform:
        """Returns the :class:`~visuscript.primatives.Transform` that the input `_T`'s :class:`CollectionDrawable`
        should have to be positioned according to this :class:`AnimatedCollection`'s rules.

        :param var: The `_T` for which the target :class:`~visuscript.primatives.Transform` is to be returned.
        :raises ValueError: If the input `_T` is not stored in this :class:`AnimatedCollection`.
        """
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[_T]:
        """Returns an iterable over the `_T` instances stored in this :class:`AnimatedCollection`."""
        ...

    def __contains__(self, var: _T, /) -> bool:
        """Returns True if a `_T` with an equivalent value is stored in this :class:`AnimatedCollection`."""
        return var in list(self)

    def __len__(self) -> int:
        """Returns the number of `_T` instances stored in this :class:`AnimatedCollection`."""
        return len(list(self))

    def organize(
        self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
    ) -> Animation:
        """Returns an :class:`~visuscript.animation.Animation` that positions all of the :class:`CollectionDrawable` instances
        corresponding to `_T` instances in this :class:`AnimatedCollection` according to its rules."""
        animation_bundle = AnimationBundle(NoAnimation(duration=duration))
        for var in self:
            animation_bundle.push(
                TransformAnimation(
                    self.drawable_for(var).transform,
                    self.target_for(var),
                    duration=duration,
                )
            )
        return animation_bundle

    @property
    def drawables(self) -> Iterable[_CollectionDrawable]:
        """An iterable over the :class:`CollectionDrawable` instances managed by this collection
        that correspond to the `_T` instances stored herein."""
        for var in self:
            yield self.drawable_for(var)

    @property
    def all_drawables(self) -> Iterable[CanBeDrawn]:
        """An iterable over all drawable objects that comprise
        this :class:`AnimatedCollection`'s visual component."""
        yield from self.auxiliary_drawables
        yield from self.drawables

    @property
    def collection_drawable(self) -> CanBeDrawn:
        """A :class:`~visuscript.drawable.Drawable` that, when drawn, draws all drawable instances that comprise this
        :class:`AnimatedCollection`'s visual component."""
        return _AnimatedCollectionDrawable(self)

    @property
    def auxiliary_drawables(self) -> list[CanBeDrawn]:
        """A list of all auxiliary drawable object instances that comprise this
        :class:`AnimatedCollection`'s visual component.
        """
        if not hasattr(self, "_auxiliary_drawables"):
            self._auxiliary_drawables: list[CanBeDrawn] = []
        return self._auxiliary_drawables

    def add_auxiliary_drawable(self, drawable: CanBeDrawn, /) -> Self:
        """Adds an drawable object to de displayed along with this :class:`AnimatedCollection`."""
        self.auxiliary_drawables.append(drawable)
        return self

    def remove_auxiliary_drawable(self, drawable: CanBeDrawn, /) -> Self:
        """Removes an auxiliar drawable from this :class:`AnimatedCollection`."""
        self.auxiliary_drawables.remove(drawable)
        return self

    def is_contains(self, var: _T, /) -> bool:
        """Returns True if a specific `_T`, not just a `_T` with an equivalent value, is stored in this :class:`AnimatedCollection`."""
        for v in self:
            if v is var:
                return True
        return False


class AnimatedSequence(AnimatedCollection[_T, _CollectionDrawable]):
    """Stores sequential data for animation."""

    @overload
    @abstractmethod
    def __getitem__(self, index: int, /) -> _T: ...
    @overload
    @abstractmethod
    def __getitem__(self, index: slice, /) -> Sequence[_T]: ...
    @abstractmethod
    def __getitem__(self, index: int | slice, /) -> _T | Sequence[_T]: ...

    def index(self, var: _T, /) -> int:
        """Returns the index of a `_T` with an equivalent value stored in this :class:`AnimatedCollection`."""
        for idx, v in enumerate(self):
            if v == var:
                return idx
        raise ValueError(f"{var} not found in this {self.__class__.__name__}.")

    def count(self, var: _T, /) -> int:
        """Returns the number of occurrences of a `_T` with an equivalent value stored in this :class:`AnimatedCollection`."""
        return sum(1 for v in self if v == var)

    def is_index(self, var: _T, /) -> int:
        """Returns the index of a specific `_T`, not just a `_T` with an equivalent value, stored in this :class:`AnimatedCollection`.

        :raises ValueError: If the input `_T` is not stored in this :class:`AnimatedCollection`.
        """
        for idx, v in enumerate(self):
            if v is var:
                return idx
        raise ValueError(f"{var} not found in this {self.__class__.__name__}.")

    def __contains__(self, var: _T, /) -> bool:
        return self.count(var) > 0

    def __iter__(self) -> Iterator[_T]:
        for i in range(len(self)):
            yield self[i]

    def __reversed__(self) -> Iterator[_T]:
        for i in range(len(self) - 1, -1, -1):
            yield self[i]


class AnimatedMutableSequence(AnimatedSequence[_T, _CollectionDrawable]):
    """Stores mutable sequential data for animation."""

    @abstractmethod
    def insert(
        self,
        index: int,
        value: _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Inserts a `_T` into this :class:`AnimatedCollection` at the specified index.

        :param index: The index at which to insert the input `_T`.
        :param value: The `_T` to be inserted.
        :param duration: The duration of the returned :class:`~visuscript.animation.Animation`, defaults to DEFER_TO_CONFIG.
        :raises ValueError: If the exact `_T`, not just one with an equivalent value, is already stored in this :class:`AnimatedCollection`.
        :return: An :class:`~visuscript.animation.Animation` inserting the value.
        """
        ...

    @overload
    @abstractmethod
    def __setitem__(self, index: int, value: _T, /) -> None: ...
    @overload
    @abstractmethod
    def __setitem__(self, index: slice, value: Iterable[_T], /) -> None: ...
    @abstractmethod
    def __setitem__(self, index: int | slice, value: _T | Iterable[_T], /) -> None:
        """Sets the `_T` or `_T` instances at the specified index or slice.

        :param index: The index or slice at which to set the input `_T` or `_T` instances.
        :param value: The `_T` or iterable of `_T` instances to be set.
        """
        ...

    @overload
    @abstractmethod
    def __delitem__(self, index: int, /) -> None: ...
    @overload
    @abstractmethod
    def __delitem__(self, index: slice, /) -> None: ...
    @abstractmethod
    def __delitem__(self, index: int | slice, /) -> None:
        """Deletes the `_T` or `_T` instances at the specified index or slice
        along with their corresponding visual representations.

        :param index: The index or slice at which to delete the `_T` or `_T` instances.
        """
        ...

    def append(
        self,
        value: _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Appends a `_T` to the end of this :class:`AnimatedCollection`.

        :param value: The `_T` to be appended.
        :return: An :class:`~visuscript.animation.Animation` appending the value.
        """
        return self.insert(len(self), value, duration=duration)

    def clear(
        self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
    ) -> Animation:
        """Clears all `_T` instances from this :class:`AnimatedCollection` along with their corresponding visual representations.

        :param duration: The duration of the returned :class:`~visuscript.animation.Animation`, defaults to DEFER_TO_CONFIG.
        :return: An :class:`~visuscript.animation.Animation` clearing the collection.
        """
        animations = AnimationBundle()
        while len(self) > 0:
            animations.push(self.pop(-1, duration=duration))
        return animations

    def extend(
        self,
        values: Iterable[_T],
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Extends this :class:`AnimatedCollection` by appending all `_T` instances in the input iterable.

        :param values: The iterable of `_T` instances to be appended.
        :param duration: The duration of the returned :class:`~visuscript.animation.Animation`, defaults to DEFER_TO_CONFIG.
        :return: An :class:`~visuscript.animation.Animation` extending the collection.
        """
        for value in values:
            self.append(value, duration=duration)
        return self.organize(duration=duration)

    def reverse(
        self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG
    ) -> Animation:
        """Reverses the order of `_T` instances in this :class:`AnimatedCollection`.

        :param duration: The duration of the returned :class:`~visuscript.animation.Animation`, defaults to DEFER_TO_CONFIG.
        :return: An :class:`~visuscript.animation.Animation` reversing the collection.
        """
        return AnimationBundle(
            *[
                self.swap(i, j, duration=duration)
                for i, j in zip(
                    range(len(self) // 2), range(len(self) - 1, len(self) // 2 - 1, -1)
                )
            ]
        )

    def pop(
        self,
        index: int = -1,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Removes and returns the `_T` at the specified index along with its corresponding visual representation.

        :param index: The index at which to remove the `_T`, defaults to -1.
        :return: An :class:`~visuscript.animation.Animation` popping the `_T`.
        """
        var = self[index]
        drawable = self.drawable_for(var)
        self.add_auxiliary_drawable(drawable)
        del self[index]
        return AnimationSequence(
            OpacityAnimation(drawable, 0.0, duration=duration),
            RunFunction(lambda: self.remove_auxiliary_drawable(drawable)),
        )

    def remove(
        self,
        value: _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Removes the first occurrence of a `_T` with an equivalent value along with its corresponding visual representation.

        :param value: The `_T` to be removed.
        :return: An :class:`~visuscript.animation.Animation` removing the `_T`.
        """
        index = self.index(value)
        return self.pop(index, duration=duration)

    def _swap(
        self, a: int | _T, b: int | _T
    ) -> Tuple[_CollectionDrawable, _CollectionDrawable]:
        """Swaps the `_T` instances stored at the input indices and returns their old drawable representations."""
        if isinstance(a, int):
            ai, av = a, self[a]
        else:
            ai, av = self.is_index(a), a
        if isinstance(b, int):
            bi, bv = b, self[b]
        else:
            bi, bv = self.is_index(b), b

        if ai < 0:
            ai += len(self)
        if bi < 0:
            bi += len(self)

        drawable_a = self.drawable_for(av)
        drawable_b = self.drawable_for(bv)

        var_a, var_b = self[ai], self[bi]

        self.remove(var_a)
        self.remove(var_b)

        if ai < bi:
            self.insert(ai, var_b)
            self.insert(bi, var_a)
        else:
            self.insert(bi, var_a)
            self.insert(ai, var_b)

        self.set_drawable_for(var_a, drawable_a)
        self.set_drawable_for(var_b, drawable_b)

        return drawable_a, drawable_b

    def swap(
        self,
        a: int | _T,
        b: int | _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        """Swaps the `_T` instances stored at the input indices.

        If `_T` is used instead of an index, the index herein of `_T` is used for the index.

        :param a: The first swap index or a specific `_T`.
        :param b: The second swap index or a specific `_T`.
        :return: An Animation linearly swapping each `_T`'s :class:`CollectionDrawable`'s respective :class:`~visuscript.primatives.Transform`.        :rtype: Animation
        """
        if a == b:
            return NoAnimation(duration=duration)

        drawable_a, drawable_b = self._swap(a, b)

        return AnimationBundle(
            TransformAnimation(drawable_a.transform, drawable_b.lazy.transform),
            TransformAnimation(drawable_b.transform, drawable_a.lazy.transform),
        )

    def qswap(
        self,
        a: int | _T,
        b: int | _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
        height_multiplier: float = 1,
    ) -> Animation:
        """Swaps the `_T` instances stored at the input indices.

        If `_T` is used instead of an index, the index herein of `_T` is used for the index.

        :param a: The first swap index or a specific `_T`.
        :param b: The second swap index or a specific `_T`.
        :param duration: The duration of the returned :class:`~visuscript.animation.Animation`, defaults to DEFER_TO_CONFIG.
        :param height_multiplier: A multiplier for the height of the quadratic curve along which the swap occurs.
        :return: An Animation along a quadratic curve swapping each `_T`'s :class:`CollectionDrawable`'s respective :class:`~visuscript.primatives.Transform`.
        """
        if a == b:
            return NoAnimation(duration=duration)

        drawable_a, drawable_b = self._swap(a, b)

        return LazyAnimation(
            lambda: quadratic_swap(
                drawable_a,
                drawable_b,
                height_multiplier=height_multiplier,
                duration=duration,
            )
        )


class AnimatedList(AnimatedMutableSequence[_T, _CollectionDrawable], TransformMixin):
    """Stores list data for animation."""

    def __init__(
        self,
        vars: Iterable[_T] = [],
        *,
        transform: Transform.TransformLike | None = None,
    ):
        super().__init__()
        self._vars: list[_T] = []
        self._drawable_map: IdMap[_T, _CollectionDrawable] = IdMap()
        if transform:
            self.set_transform(transform)
        for var in vars:
            self.append(var).finish()
        self.organize().finish()

    @abstractmethod
    def get_organizer(self) -> Organizer:
        """Initializes and returns an :class:`~visuscript.organizer.Organizer` for this :class:`AnimatedList`.
        The returned :class:`~visuscript.organizer.Organizer` sets the rule for how `animated_list[i]` should
        be transformed with `organizer[i]`.
        """
        ...

    @abstractmethod
    def new_drawable_for(self, var: _T, /) -> _CollectionDrawable:
        """Initializes and returns an :class:`CollectionDrawable` for a `_T` newly inserted into this :class:`AnimatedList`."""
        ...

    @property
    def drawables(self) -> list[_CollectionDrawable]:
        return list(self._drawable_map[v] for v in self._vars)

    @property
    def organizer(self) -> Organizer:
        return self.get_organizer().set_transform(self.transform)

    def target_for(self, var: _T, /) -> Transform:
        index = self.is_index(var)
        return self.organizer[index]

    def insert(
        self,
        index: int,
        value: _T,
        /,
        *,
        duration: float | ConfigurationDeference = DEFER_TO_CONFIG,
    ) -> Animation:
        if self.is_contains(value):
            raise ValueError(
                f"Cannot have the same '{value.__class__.__name__}' in this AnimatedList twice."
            )
        self._vars.insert(index, value)
        new_drawable = self.new_drawable_for(value)
        new_drawable.opacity = 0.0
        new_drawable.transform = self.target_for(value)
        self._drawable_map[value] = new_drawable
        return OpacityAnimation(new_drawable, 1.0, duration=duration)

    def drawable_for(self, var: _T, /) -> _CollectionDrawable:
        if var not in self._drawable_map:
            raise ValueError(f"{var} is not present in this {self.__class__.__name__}")
        return self._drawable_map[var]

    def set_drawable_for(self, var: _T, drawable: _CollectionDrawable, /) -> None:
        self._drawable_map[var] = drawable

    @overload
    def __getitem__(self, index: int, /) -> _T: ...
    @overload
    def __getitem__(self, index: slice, /) -> list[_T]: ...
    def __getitem__(self, index: int | slice, /) -> _T | list[_T]:
        return self._vars[index]

    @overload
    def __setitem__(self, index: int, value: _T, /) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[_T], /) -> None: ...
    def __setitem__(self, index: int | slice, value: _T | Iterable[_T], /) -> None:
        if not isinstance(index, slice):
            index = slice(index, index + 1, 1)
            value = [value]  # type: ignore

        for idx, var in zip(
            range(index.start or 0, index.stop or len(self), index.step or 1), value
        ):
            if self.is_contains(var):
                raise ValueError(
                    f"Cannot have the same '{var.__class__.__name__}' in this AnimatedList twice."
                )
            old_var = self._vars[idx]
            del self._drawable_map[old_var]
            self._vars[idx] = var
            self._drawable_map[var] = self.new_drawable_for(var)

    def __delitem__(self, index: int | slice, /):
        if isinstance(index, int):
            index = slice(index, index + 1, 1)
        for var in self[index]:
            del self._drawable_map[var]
        del self._vars[index]

    def __iter__(self):
        for var in self._vars:
            yield var

    def __len__(self):
        return len(self._vars)


class AnimatedArray(AnimatedList[Var, Text]):
    def __init__(
        self,
        variables: Iterable[Var],
        font_size: float,
        transform: Transform | None = None,
    ):
        variables = list(variables)
        self._max_length = len(variables)
        self._font_size = font_size
        super().__init__(variables)
        for transform in self.organizer:
            self.add_auxiliary_drawable(
                Rect(font_size, font_size).set_transform(self.transform @ transform)
            )

    def get_organizer(self):
        return GridOrganizer((1, len(self)), (self._font_size, self._font_size))

    def new_drawable_for(self, var: Var) -> Text:
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
        ushape: Tuple[int, int],
        transform: Transform | None = None,
    ):
        self._ushape = ushape
        super().__init__(variables, font_size, transform=transform)

    def _tuple_to_index(self, index: Tuple[int, int]):
        for axis, (idx, size) in enumerate(zip(index, self._ushape)):
            if idx >= size:
                raise IndexError(
                    f"Index {idx} is too large for axis {axis} of size {size}."
                )

        return index[0] * self._ushape[1] + index[1]

    @overload
    def __getitem__(self, index: int) -> Var: ...
    @overload
    def __getitem__(self, index: slice) -> list[Var]: ...
    @overload
    def __getitem__(self, index: Tuple[int, int]) -> Var: ...
    def __getitem__(self, index: int | slice | Tuple[int, int]) -> Var | list[Var]:
        if isinstance(index, (int, slice)):
            return super()[index]
        return super()[self._tuple_to_index(index)]

    @overload
    def __setitem__(self, index: int, value: Var) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[Var]) -> None: ...
    @overload
    def __setitem__(self, index: Tuple[int, int], value: Var) -> None: ...
    def __setitem__(
        self, index: int | slice | Tuple[int, int], value: Var | Iterable[Var]
    ) -> None:
        if isinstance(index, int) and isinstance(value, Var):
            super().__setitem__(index, value)
        elif isinstance(index, slice) and isinstance(value, Iterable):
            super().__setitem__(index, value)
        elif isinstance(index, Tuple) and isinstance(value, Var):
            super().__setitem__(self._tuple_to_index(index), value)
        else:
            raise TypeError("Invalid index or value type.")

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
        return GridOrganizer(self._ushape, (self._font_size, self._font_size))
