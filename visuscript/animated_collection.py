"""This module contains functionality for :class:`~AnimatedCollection`.
"""

from visuscript.animation import NoAnimation, PathAnimation, AnimationBundle, TransformAnimation, LazyAnimation, Animation
from visuscript.segment import Path
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.element import Element
from visuscript.text import Text
from visuscript.organizer import BinaryTreeOrganizer, Organizer, GridOrganizer
from visuscript.element import Circle, Pivot
from visuscript.primatives import Transform
from visuscript.drawable import Drawable
from visuscript.math_utility import magnitude

from abc import ABC, abstractmethod
from visuscript.primatives import Vec2
from typing import Collection, Iterable, MutableSequence, Self, Any, Generator


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

# TODO Refactor VarContainer to inherit from Drawable.
class VarContainer(ABC):
    """A container for a :class:`Var` that stores an :class:`~visuscript.element.Element` therewith."""

    def __init__(self, var: Var, *args, **kwargs):
        """
        :param var: The Var to be contained.
        :type var: Var
        :param args: Arbitrary positional arguments to be passed to :meth:`~VarContainer.element_from_var`.
        :type args: tuple
        :param kwargs: Arbitrary keyword arguments to be passed to :meth:`~VarContainer.element_from_var`.
        :type kwargs: dict
        """
        self._var = var
        self._element = self.element_from_var(var, *args, **kwargs)

    @property
    def var(self) -> Var:
        """The :class:`Var` contained by this :class:`VarContainer`.
        """
        return self._var

    @property
    def element(self) -> Element:
        """The :class:`~visuscript.element.Element` for the :class:`Var` contained by this :class:`VarContainer`.
        """
        return self._element

    @abstractmethod
    def element_from_var(self, var: Var) -> Element:
        """Initializes a new :class:`~visuscript.element.Element` to be used by this :class:`VarContainer` to represent the contained :class:`Var`.

        This is an abstract method that must be implemented by subclasses. Subclasses
        should define the parameters that :attr:`~VarContainer.element_from_var`
        requires to properly construct the element.

        :param var: The :class:`Var` used to initialize the :class:`~visuscript.element.Element`.
        :type var: Var
        :param args: Arbitrary positional arguments passed through from :meth:`~VarContainer.__init__`.
                     Subclasses may define these as explicit positional parameters.
        :type args: tuple
        :param kwargs: Arbitrary keyword arguments passed through from :meth:`~VarContainer.__init__`.
                       Subclasses may define these as explicit keyword-only parameters.
        :type kwargs: dict
        :return: The initialized :class:`~visuscript.element.Element`.
        :rtype: Element
        """
        ...
        ...

class BlankContainer(VarContainer):
    """A :class:`VarContainer` that has an invisible :class:`~visuscript.element.Element`.
    """
    def element_from_var(self, var: Var) -> Pivot:
        return Pivot()
    

class Node(VarContainer):
    """A :class:`VarContainer` that displays the :class:`Var`'s value inside a circle."""
    def __init__(self, *, var: Var, radius: float):
        super().__init__(var=var, radius=radius)
    
    def element_from_var(self, var: Var, radius: float) -> Element:
        return Circle(radius).with_child(Text(str(var.value), font_size=radius))
    
class TextContainer(VarContainer):
    """A :class:`VarContainer` that displays the :class:`Var`'s value only with characters."""
    def __init__(self, *, var: Var, font_size: float):
        super().__init__(var=var, font_size=font_size)
        
    def element_from_var(self, var: Var, font_size: float):
        return Text(str(var.value), font_size=font_size)

class _AnimatedCollectionElement(Drawable):
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
    
   
    
class AnimatedCollection(Collection[Var]):
    """Stores data in form of :class:`Var` instances alongside corresponding :class:`~visuscript.element.Element` instances
    and organizational functionality to transform the elements according to the rules of the given :class:`AnimatedCollection`.
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
            animation_bundle << TransformAnimation(self.element_for(var).transform, self.target_for(var), duration=duration)
        return animation_bundle
        
    
    @property
    @abstractmethod
    def elements(self) -> Iterable[Element]:
        """An iterable over the :class:`~visuscript.element.Element` instances managed by this collection
        that correspond to the :class:`Var` instances stored herein."""
        ...


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
        return _AnimatedCollectionElement(self)
    
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
        self._list: list[VarContainer] = []
        for var in variables:
            self.insert(len(self), var).finish()

    @property
    def transform(self) -> Transform:
        return self._transform

    @abstractmethod
    def new_container_for(self, var: Var) -> VarContainer:
        """Initializes and returns a :class:`VarContainer` for a :class:`Var` newly inserted into this :class:`AnimatedList`.
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

    @property
    def elements(self) -> list[Element]:
        return list(map(lambda x: x.element, self._list))

    def target_for(self, var: Var):
        index = next(index for index, container in enumerate(self._list) if container.var is var)
        return self._transform(self.organizer[index])

    def element_for(self, var: Var):
        for container in self._list:
            if container.var is var:
                return container.element
            
        raise ValueError(f"Var {var} is not present in this AnimatedList")
    
    def container_at(self, index: int) -> VarContainer:
        return self._list[index]
    

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index: int | slice):
        container = self._list[index]
        if isinstance(container, list):
            return list(map(lambda x: x.var, container))
        else:
            return container.var
        
    def __setitem__(self, index: int | slice, value: Var):
        if not isinstance(value, Var):
            raise TypeError(f"Cannot set value of type {type(value).__name__}: must be of type Var")
        if self.is_contains(value):
            raise ValueError(f"Cannot have the same Var in this AnimatedList twice.")
        self._list[index] = self.new_container_for(value)

    def __delitem__(self, index: int | slice):
        del self._list[index]

    def insert(self, index: int, value: Var, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        if not isinstance(value, Var):
            raise TypeError(f"Cannot insert value of type {type(value).__name__}: must be of type Var")
        if self.is_contains(value):
            raise ValueError(f"Cannot have the same Var in this AnimatedList twice.")
        self._list.insert(index, self.new_container_for(value))
        return self.organize(duration=duration)

    def _swap(self, a, b):
        tmp = self._list[a]
        self._list[a] = self._list[b]
        self._list[b] = tmp

    def swap(self, a: int, b: int) -> Animation:
        """Swaps the :class:`Var` instances stored at the input indices.

        :param a: The first swap index.
        :type a: int
        :param b: The second swap index.
        :type b: int
        :return: An Animation swapping each :class:`Var`'s :class:`~visuscript.element.Element`'s respective :class:`~visuscript.primatives.Transform`.
        :rtype: Animation
        """
        if a == b:
            return NoAnimation()

        if isinstance(a, Var):
            a = self.is_index(a)
        if isinstance(b, Var):
            b = self.is_index(b)

        element_a = self.element_for(self[a])
        element_b = self.element_for(self[b])

        self._swap(a,b)
        
        return LazyAnimation(lambda: AnimationBundle(
            TransformAnimation(element_a.transform, element_b.transform),
            TransformAnimation(element_b.transform, element_a.transform)
        ))



        self._swap(self, a, b)
        
    
    def extend(self, values: Iterable, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> AnimationBundle:
        super().extend(values)
        return self.organize(duration=duration)
    

    def _var_iter(self):
        return map(lambda x: x.var, self._list)
    def is_index(self, var: Var) -> int:
        return list(map(lambda x: x is var, self._var_iter())).index(True)
    def is_contains(self, var: Var):
        return sum(map(lambda x: x is var, self._var_iter())) > 0


class QuadraticSwapAnimatedList(AnimatedList):
    def swap(self, a: int | Var, b: int | Var) -> LazyAnimation:

        if isinstance(a, Var):
            a = self.is_index(a)
        if isinstance(b, Var):
            b = self.is_index(b)

        assert a != b

        element_a = self.element_for(self[a])
        element_b = self.element_for(self[b])

        diff = element_b.transform.translation.xy - element_a.transform.translation.xy
        distance = magnitude(diff)
        direction = diff / distance
        ortho = Vec2(-direction.y, direction.x)

        mid = element_a.transform.translation.xy + direction * distance/2
        lift = ortho * element_a.shape.circumscribed_radius*2

        self._swap(a,b)
        
        return LazyAnimation(lambda: AnimationBundle(
            PathAnimation(element_a.transform, Path().M(*element_a.transform.translation.xy).Q(*(mid - lift), *element_b.transform.translation.xy)),
            PathAnimation(element_b.transform, Path().M(*element_b.transform.translation.xy).Q(*(mid + lift), *element_a.transform.translation.xy))
        ))

class AnimatedArray(QuadraticSwapAnimatedList):

    def __init__(self, variables: Iterable, *, font_size: float, **kwargs):

        self._font_size = font_size

        super().__init__(variables, **kwargs)
   
    def get_organizer(self):
        return GridOrganizer((1,len(self)), (self._font_size*2, self._font_size*2))
    
    def new_container_for(self, var):
        if var.is_none:
            return BlankContainer(var)
        return TextContainer(var=var, font_size=self._font_size)
    
    


class AnimatedBinaryTreeArray(QuadraticSwapAnimatedList):

    def __init__(self, variables: Iterable[Var], *, radius: float, level_heights: float | None = None, node_width: float | None = None, **kwargs):

        self._radius = radius
        self.level_heights = level_heights or 3*radius
        self.node_width = node_width or 3*radius

        super().__init__(variables, **kwargs)
   
    def get_organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(num_levels=num_levels, level_heights=self.level_heights, node_width=self.node_width)
    
    def new_container_for(self, var):
        if var.is_none:
            return BlankContainer(var)
        
        n = Node(var=var, radius=self._radius)
        # n.element.set_transform(self.transform)
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
    
    # def insert(self, index, value, *, duration = DEFER_TO_CONFIG):
    #     self.extend([None]*max(index - len(self), 0))
    #     return super().insert(index, value, duration=duration)
