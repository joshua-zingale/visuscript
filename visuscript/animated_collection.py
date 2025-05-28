from visuscript.animation import NoAnimation, PathAnimation, AnimationBundle, TransformAnimation
from visuscript.segment import Path
from visuscript.config import ConfigurationDeference, DEFER_TO_CONFIG
from visuscript.element import Element
from visuscript.text import Text
from visuscript.organizer import BinaryTreeOrganizer, Organizer, GridOrganizer
from visuscript.element import Circle, Pivot
from visuscript.primatives import Transform


from abc import ABC, abstractmethod
from visuscript.primatives import Vec2
from typing import Collection, Iterable, MutableSequence, Self


import numpy as np


class Var:

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

NilVar = Var(None)
"""A Var representing no value."""


class VarContainer(ABC):

    @property
    @abstractmethod
    def var(self) -> Var:
        ...

    @property
    @abstractmethod
    def element(self) -> Element:
        ...

class BlankContainer(VarContainer):

    def __init__(self, var: Var):
        self._var = var
        self._element = Pivot()

    @property
    def var(self) -> Var:
        return self._var
    
    @property
    def element(self) -> Element:
        return self._element
    

class Node(VarContainer):
    def __init__(self, *, var: Var, radius: float):

        self._var = var

        self._element = Circle(radius).with_child(Text(str(self._var.value), font_size=radius))

    @property
    def var(self) -> Var:
        return self._var

    @property
    def element(self) -> Element:
        return self._element
    
class TextContainer(VarContainer):
    def __init__(self, *, var: Var, font_size: float):
        self._var = var
        self._element = Text(str(self._var.value), font_size=font_size)

    @property
    def var(self) -> Var:
        return self._var

    @property
    def element(self) -> Element:
        return self._element

# TODO Fix this hack, which allows the canvas to reflect the current elements of the AnimatedCollection
# This should be replaced with something that does not depend on implementational details like _children
class _AnimatedCollectionElement(Pivot):
    def __init__(self, animated_collection: "AnimatedCollection", **kwargs):
        super().__init__(**kwargs)
        self._animated_collection = animated_collection

    @property
    def _children(self):
        return self._animated_collection.all_elements
    
    @_children.setter
    def _children(self, value):
        pass
    
class AnimatedCollection(Collection[Var]):

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
        yield from self.elements
        yield from self.auxiliary_elements

    @property
    def structure_element(self):
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
        self._list = list(map(lambda v: self.new_container_for(v), variables))
        

    @property
    def transform(self) -> Transform:
        return self._transform

    @abstractmethod
    def new_container_for(self, var: Var) -> VarContainer:
        ...

    @property
    def organizer(self) -> Organizer:
        ...

    @property
    def elements(self):
        return list(map(lambda x: x.element, self._list))

    def target_for(self, var: Var):
        index = next(index for index, container in enumerate(self._list) if container.var is var)
        return self.organizer[index]

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
        self._list[index] = self.new_container_for(value)

    def __delitem__(self, index: int | slice):
        del self._list[index]

    def insert(self, index: int, value: Var, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG):
        if not isinstance(value, Var):
            raise TypeError(f"Cannot insert value of type {type(value).__name__}: must be of type Var")
        self._list.insert(index, self.new_container_for(value))
        return self.organize(duration=duration)

    def _swap(self, a, b):
        tmp = self._list[a]
        self._list[a] = self._list[b]
        self._list[b] = tmp


    def swap(self, a: int, b: int) -> AnimationBundle:
        assert a != b

        element_a = self.element_for(self[a])
        element_b = self.element_for(self[b])

        diff = element_b.transform.translation.xy - element_a.transform.translation.xy
        distance = np.linalg.norm(diff)
        direction = diff / distance
        ortho = Vec2(-direction.y, direction.x)

        mid = element_a.transform.translation.xy + direction * distance/2
        lift = ortho * element_a.shape.circumscribed_radius*2

        self._swap(a,b)
        
        return AnimationBundle(
            PathAnimation(element_a.transform, Path().M(*element_a.transform.translation.xy).Q(*(mid - lift), *element_b.transform.translation.xy)),
            PathAnimation(element_b.transform, Path().M(*element_b.transform.translation.xy).Q(*(mid + lift), *element_a.transform.translation.xy))
        )
    
    def extend(self, values: Iterable, *, duration: float | ConfigurationDeference = DEFER_TO_CONFIG) -> AnimationBundle:
        super().extend(values)
        return self.organize(duration=duration)
    

    def is_index(self, var: Var) -> int:
        return list(map(lambda x: x is var, map(lambda x: x.var, self._list))).index(True)


class AnimatedArray(AnimatedList):

    def __init__(self, variables: Iterable, *, font_size: float, **kwargs):

        self._font_size = font_size

        super().__init__(variables, **kwargs)
   
    @property
    def organizer(self):
        return GridOrganizer((1,len(self)), (self._font_size*2, self._font_size*2), transform = self.transform)
    
    def new_container_for(self, var):
        if var.is_none:
            return BlankContainer(var)
        return TextContainer(var=var, font_size=self._font_size)


class AnimatedBinaryTreeArray(AnimatedList):

    def __init__(self, variables: Iterable[Var], *, radius: float, level_heights: float | None = None, node_width: float | None = None, **kwargs):

        self._radius = radius
        self.level_heights = level_heights or 3*radius
        self.node_width = node_width or 3*radius

        super().__init__(variables, **kwargs)
   
    @property
    def organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(num_levels=num_levels, level_heights=self.level_heights, node_width=self.node_width, transform = self.transform)
    
    def new_container_for(self, var):
        if var.is_none:
            return BlankContainer(var)
        
        n = Node(var=var, radius=self._radius)
        n.element.set_transform(self.transform)
        return n

    def get_parent_index(self, var: Var):
        return int((self.is_index(var) + 1)//2) - 1
    
    def get_left_index(self, var: Var):
        return int((self.is_index(var) + 1) * 2) - 1 
    
    def get_right_index(self, var: Var):
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
    
    # def insert(self, index, value, *, duration = DEFER_TO_CONFIG):
    #     self.extend([None]*max(index - len(self), 0))
    #     return super().insert(index, value, duration=duration)
