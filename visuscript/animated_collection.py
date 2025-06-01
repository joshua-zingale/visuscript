"""This module contains functionality for AnimatedCollections"""

from visuscript.animation import NoAnimation, PathAnimation, AnimationBundle, TransformAnimation, LazyAnimation
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
from typing import Collection, Iterable, MutableSequence, Self


import numpy as np


class Var:
    """A wrapper around any other type: the foundational bit of data to be stored in an AnimatedCollection."""

    def __init__(self, value, *, type_: type | None = None):

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
        return self._value
    
    @property
    def is_none(self):
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
"""A Var representing no value."""


class VarContainer(ABC):
    """A container for variable"""

    def __init__(self, var: Var, *args, **kwargs):
        """Initializes self.

        :param var: The Var to be contained.
        :type var: Var
        """
        self._var = var
        self._element = self.element_from_var(var, *args, **kwargs)

    @property
    def var(self) -> Var:
        """Returns the Var contained by the VarContainer."""
        return self._var

    @property
    def element(self) -> Element:
        """Returns the Element for the Var contained by the VarContainer"""
        return self._element

    @abstractmethod
    def element_from_var(self, var: Var) -> Element:
        """Initializes a new Element to be used by this VarContainer to represent the contained Var.

        :param var: The Var used to initialize the Element.
        :type var: Var
        :return: The initialized Element.
        :rtype: Element
        """
        ...

class BlankContainer(VarContainer):
    def element_from_var(self, var: Var) -> Element:
        return Pivot()
    

class Node(VarContainer):
    def __init__(self, *, var: Var, radius: float):
        super().__init__(var=var, radius=radius)
    
    def element_from_var(self, var: Var, radius: float) -> Element:
        return Circle(radius).with_child(Text(str(var.value), font_size=radius))
    
class TextContainer(VarContainer):
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
    """The Base class for all AnimatedCollections.
    
    An AnimatedCollection stores data in form of Var instances alongside corresponding Element instances.
    """

    # @property
    # @abstractmethod
    # def scaffolding(self) -> Iterable[Element]:
    #     ...

    @abstractmethod
    def element_for(self, var: Var) -> Element:
        ...

    @abstractmethod
    def target_for(self, var: Var) -> Transform:
        ...

    def transform_for(self, var: Var) -> Transform:
        return self.element_for(var).transform
    
    def organize(self, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> AnimationBundle:
        animation_bundle = AnimationBundle(NoAnimation(duration=duration))
        for var in self:
            animation_bundle << TransformAnimation(self.element_for(var).transform, self.target_for(var), duration=duration)
        return animation_bundle
        
    
    @property
    @abstractmethod
    def elements(self) -> Iterable[Element]:
        ...


    @property
    def all_elements(self) -> Iterable[Element]:
        yield from self.auxiliary_elements
        yield from self.elements

    @property
    def collection_element(self):
        return _AnimatedCollectionElement(self)
    
    @property
    def auxiliary_elements(self) -> list[Element]:
        if not hasattr(self, "_auxiliary_elements"):
            self._auxiliary_elements: list[Element] = []
        return self._auxiliary_elements
    

    def add_auxiliary_element(self, element: Element) -> Self:
        self.auxiliary_elements.append(element)
        return self
    
    def remove_auxiliary_element(self, element: Element) -> Self:
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
        ...

    @property
    def organizer(self) -> Organizer:
        return self.get_organizer()
    
    @abstractmethod
    def get_organizer() -> Organizer:
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

    def swap(self, a: int, b: int) -> LazyAnimation:
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
