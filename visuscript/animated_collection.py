"""This module contains functionality for :class:`~AnimatedCollection`.
"""
from visuscript.animation import NoAnimation, PathAnimation, AnimationBundle, TransformAnimation, LazyAnimation, Animation
from visuscript.segment import Path
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.text import Text
from visuscript.organizer import BinaryTreeOrganizer, Organizer
from visuscript.element import Circle, Pivot, Element
from visuscript.primatives import Transform
from visuscript.drawable import Drawable
from visuscript.math_utility import magnitude

from abc import abstractmethod
from visuscript.primatives import Vec2
from typing import Collection, Iterable, MutableSequence, Self, Any


import numpy as np


class Var:
    """An immutable wrapper around any other type: the foundational bit of data to be stored in an :class:`AnimatedCollection`.
    """

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
    def value(self):
        """The value stored in this :class:`Var`."""
        return self._value
    
    @property
    def is_none(self) -> bool:
        """True if and only if None is the value stored herein.
        """
        return self.value is None
    
    def __add__(self, other: "Var"):
        value = self.value + other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __sub__(self, other: "Var"):
        value = self.value - other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __mul__(self, other: "Var"):
        value = self.value * other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __truediv__(self, other: "Var"):
        value = self.value / other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __mod__(self, other: "Var"):
        value = self.value % other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __floordiv__(self, other: "Var"):
        value = self.value // other.value
        type_ = type(value)
        return Var(value, type_=type_)
    
    def __pow__(self, other: "Var"):
        value = self.value ** other.value
        type_ = type(value)
        return Var(value, type_=type_)
    

    def __gt__(self, other: "Var") -> bool:
        return self.value > other.value
    def __ge__(self, other: "Var") -> bool:
        return self.value >= other.value
    def __eq__(self, other: "Var") -> bool:
        return self.value == other.value
    def __le__(self, other: "Var") -> bool:
        return self.value <= other.value
    def __lt__(self, other: "Var") -> bool:
        return self.value < other.value
    
    def __str__(self):
        return f"Var({self.value}, type={self._type.__name__})"
    
    def __repr__(self):
        return str(self)
    
    def __bool__(self):
        return self.value is not None and self.value is not False

NilVar = Var(None)
"""A :class:`Var` representing no value."""

class _AnimatedCollectionDrawable(Drawable):
    def __init__(self, animated_collection: "AnimatedCollection", **kwargs):
        super().__init__(**kwargs)
        self._animated_collection = animated_collection

    @property
    def top_left(self):
        return Vec2(0,0)
    @property
    def width(self):
        return 0.0
    @property
    def height(self):
        return 0.0
    
    def draw(self):
        return "".join(element.draw() for element in self._animated_collection.all_elements)
    
   
#TODO Consider changing Element in all the below to Drawable.
# Drawable would be sufficient for the ABC
class AnimatedCollection(Collection[Var]):
    """Stores data in form of :class:`Var` instances alongside corresponding :class:`~visuscript.element.Element` instances
    and organizational functionality to transform the :class:`~visuscript.element.Element` instances according to the rules of the given :class:`AnimatedCollection`.
    """

    @abstractmethod
    def element_for(self, var: Var) -> Element:
        """Returns the :class:`~visuscript.element.Element` for a :class:`Var` stored in this collection."""
        ...

    @abstractmethod
    def target_for(self, var: Var) -> Transform:
        """Returns the :class:`~visuscript.primatives.Transform` that the input :class:`Var`'s :class:`~visuscript.element.Element`
        should have to be positioned according to this :class:`AnimatedCollection`'s rules.
        """
        ...
    
    def organize(self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> AnimationBundle:
        """Returns an :class:`~visuscript.animation.Animation` that positions all of the :class:`~visuscript.element.Element` instances
        corresponding to :class:`Var` instances in this :class:`AnimatedCollection` according to its rules."""
        animation_bundle = AnimationBundle(NoAnimation(duration=duration))
        for var in self:
            animation_bundle << TransformAnimation.lazy(self.element_for(var).transform, self.target_for(var), duration=duration)
        return animation_bundle  
    
    @property
    def elements(self) -> Iterable[Element]:
        """An iterable over the :class:`~visuscript.element.Element` instances managed by this collection
        that correspond to the :class:`Var` instances stored herein."""
        for var in self:
            yield self.element_for(var)

    @property
    def all_elements(self) -> Iterable[Element]:
        """An iterable over all :class:`~visuscript.element.Element` instances that comprise
        this :class:`AnimatedCollection`'s visual component."""
        yield from self.auxiliary_elements
        yield from self.elements

    @property
    def collection_element(self) -> Drawable:
        """A :class:`~visuscript.drawable.Drawable` that, when drawn,
        draws all :class:`~visuscript.element.Element` instances that comprise this
        :class:`AnimatedCollection`'s visual component."""
        return _AnimatedCollectionDrawable(self)
    
    @property
    def auxiliary_elements(self) -> list[Element]:
        """A list of all auxiliary :class:`~visuscript.element.Element` instances that comprise this
        :class:`AnimatedCollection`'s visual component.
        """
        if not hasattr(self, "_auxiliary_elements"):
            self._auxiliary_elements: list[Element] = []
        return self._auxiliary_elements
    

    def add_auxiliary_element(self, element: Element) -> Self:
        """Adds an :class:`~visuscript.element.Element` to de displayed along with the :class:`~visuscript.element.Element`
        instances that correspond to the :class:`Var` instances stored herein."""
        self.auxiliary_elements.append(element)
        return self
    
    def remove_auxiliary_element(self, element: Element) -> Self:
        """Removes an auxiliar element form this :class:`AnimatedCollection`."""
        self.auxiliary_elements.remove(element)
        return self



class AnimatedList(AnimatedCollection, MutableSequence[Var]):
    def __init__(self, variables: Iterable = [], *, transform: Transform | None = None):
        self._transform = Transform() if transform is None else Transform(transform)
        variables = map(lambda v: v if isinstance(v, Var) else Var(v), variables)
        self._vars: list[Var] = []
        self._elements: list[Element] = []
        for var in variables:
            self.insert(len(self), var).finish()

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    @property
    def transform(self) -> Transform:
        return self._transform

    @abstractmethod
    def new_element_for(self, var: Var) -> Element:
        """Initializes and returns an :class:`~visuscript.element.Element` for a :class:`Var` newly inserted into this :class:`AnimatedList`.
        """
        ...

    @property
    def organizer(self) -> Organizer:
        return self.get_organizer()
    
    @abstractmethod
    def get_organizer() -> Organizer:
        """Initializes and returns an :class:`~visuscript.organizer.Organizer` for this :class:`AnimatedList`.
        The returned :class:`~visuscript.organizer.Organizer` sets the rule for how `animated_list[i]` should
        be transformed with `organizer[i]`.
        """
        ...

    def target_for(self, var: Var) -> Transform:
        return self._transform(self.organizer[self.is_index(var)])

    def element_for(self, var: Var) -> Element:
        if var not in self._vars:
            raise ValueError(f"Var {var} is not present in this {self.__class__.__name__}")
        return self._elements[self.is_index(var)]
                
    def __len__(self):
        return len(self._vars)

    def __getitem__(self, index: int | slice):
        return self._vars[index]
        
    def __setitem__(self, index: int | slice, value: Var):
        if not isinstance(value, Var):
            raise TypeError(f"Cannot set value of type {type(value).__name__}: must be of type Var")
        if self.is_contains(value):
            raise ValueError(f"Cannot have the same Var in this AnimatedList twice.")
        self._vars[index] = value
        self._elements[index] = self.new_element_for(value)

    def __delitem__(self, index: int | slice):
        del self._vars[index]
        del self._elements[index]

    def insert(self, index: int, value: Var, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        if not isinstance(value, Var):
            raise TypeError(f"Cannot insert value of type {type(value).__name__}: must be of type Var")
        if self.is_contains(value):
            raise ValueError(f"Cannot have the same Var in this AnimatedList twice.")
        self._vars.insert(index, value)
        self._elements.insert(index, self.new_element_for(value))
        return self.organize(duration=duration)

    def _swap(self, a, b):
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

        element_a, element_b = self._swap(a,b)
        
        return AnimationBundle(
            TransformAnimation.lazy(element_a.transform, element_b.transform),
            TransformAnimation.lazy(element_b.transform, element_a.transform)
        )
    
    def quadratic_swap(self, a: int | Var, b: int | Var) -> LazyAnimation:
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
            return NoAnimation()

        element_a, element_b = self._swap(a,b)

        diff = element_b.transform.translation.xy - element_a.transform.translation.xy
        distance = magnitude(diff)
        direction = diff / distance
        ortho = Vec2(-direction.y, direction.x)

        mid = element_a.transform.translation.xy + direction * distance/2
        lift = ortho * element_a.shape.circumscribed_radius*2
        
        return LazyAnimation(lambda: AnimationBundle(
            PathAnimation(element_a.transform, Path().M(*element_a.transform.translation.xy).Q(*(mid - lift), *element_b.transform.translation.xy)),
            PathAnimation(element_b.transform, Path().M(*element_b.transform.translation.xy).Q(*(mid + lift), *element_a.transform.translation.xy))
        ))
        
    def extend(self, values: Iterable, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> AnimationBundle:
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
        """Returns True if a specific :class:`Var`, not just a :class:`Var` with an equivalent value, is herein contained.
        """
        return sum(map(lambda x: x is var, self)) > 0
    
class AnimatedBinaryTreeArray(AnimatedList):

    def __init__(self, variables: Iterable[Var], *, radius: float, level_heights: float | None = None, node_width: float | None = None, **kwargs):

        self._radius = radius
        self.level_heights = level_heights or 3*radius
        self.node_width = node_width or 3*radius

        super().__init__(variables, **kwargs)
   
    def get_organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(num_levels=num_levels, level_heights=self.level_heights, node_width=self.node_width)
    
    def new_element_for(self, var):
        if var.is_none:
            return Pivot()
        n = Circle(radius=self._radius).add_child(Text(str(var.value), font_size=self._radius))
        return n

    def get_parent_index(self, var: int | Var):
        if isinstance(var, int):
            var = self[var]
        return int((self.is_index(var) + 1)//2) - 1
    
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