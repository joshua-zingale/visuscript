from visuscript import *
from visuscript.animation import Animation
from visuscript.organizer import BinaryTreeOrganizer, Organizer
from visuscript.element import Element
from abc import ABC, abstractmethod
from visuscript.primatives import Vec3, get_vec3
from typing import Generator, Collection, Self, Iterable, MutableSequence
import numpy as np
import sys

from visuscript.config import config

class Var:
    def __init__(self, value, *, type_: type | None = None):

        if type_ is None:
            type_ = type(value)

        self._value = type_(value)
        self._type = type_

    @property
    def drawable(self) -> Text:
        return self._text
    
    @property
    def value(self):
        return self._value
    
    def __add__(self, other: "Var"):
        value = self.value + other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __sub__(self, other: "Var"):
        value = self.value - other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __mul__(self, other: "Var"):
        value = self.value * other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __truediv__(self, other: "Var"):
        value = self.value / other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __mod__(self, other: "Var"):
        value = self.value % other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __floordiv__(self, other: "Var"):
        value = self.value // other.value
        type_ = type(value)
        return Var(value, type_)
    
    def __pow__(self, other: "Var"):
        value = self.value ** other.value
        type_ = type(value)
        return Var(value, type_)
    

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
        return str(self.value)
    
    # def __matmul__(self, other: "Var"):
    #     value = self.value @ other.value
    #     type_ = type(value)
    #     return Var(value, type_)


class VarContainer(ABC):

    @property
    @abstractmethod
    def var(self) -> Var:
        ...

    @property
    @abstractmethod
    def element(self) -> Element:
        ...
    

class Node(VarContainer):
    def __init__(self, *, var: Var, radius: float):

        self._var = var
        self._radius: float = radius

        self._element = Text(str(self._var), font_size=self._radius).with_children(
            Circle(radius)
        )

    @property
    def var(self) -> Var:
        return self._var

    @property
    def element(self) -> Element:
        return self._element
    
class AnimatedCollection(Collection[Var]):

    @abstractmethod
    def element_for(self, var: Var) -> Element:
        ...

    @abstractmethod
    def target_for(self, var: Var) -> Transform:
        ...

    def transform_for(self, var: Var) -> Transform:
        return self.element_for(var).transform
    
    def organize(self):
        for var in self:
            if var is None:
                continue
            self.element_for(var).set_transform(self.target_for(var))
    
    
    @property
    @abstractmethod
    def animations(self) -> Iterable[Animation]:
        ...
    
    @property
    @abstractmethod
    def elements(self) -> Iterable[Element]:
        ...


    # @property
    # @abstractmethod
    # def removed(self) -> dict[Var, Element]:
    #     """Returns a dictionary mapping Var objects that have been removed since the last finish of the Animations in this Structure."""
    #     ...

    # @abstractmethod
    # def remove(self, var: Var) -> Self:
    #     ...

class AnimatedList(AnimatedCollection, MutableSequence):
    def __init__(self, variables: Iterable[Var | None], *, transform: Transform | None = None):
        self._list = list(map(lambda v: None if v is None else self.new_container_for(v), variables))
        self._transform = Transform() if transform is None else Transform(transform)

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
        return list(map(lambda x: None if x is None else x.element, self._list))

    def target_for(self, var: Var):
        index = next(index for index, container in enumerate(self._list) if container and container.var is var)
        return self.organizer[index]

    def element_for(self, var: Var):
        for container in self._list:
            if container is None:
                continue
            if container.var is var:
                return container.element
            
        raise ValueError(f"Var {var} is not present in this AnimatedList")
    

    def _element_iter(self):
        yield from map(lambda x: x.element, filter(None, self._list))


    def __len__(self):
        return len(self._list)

    def __getitem__(self, index: int | slice):
        container = self._list[index]
        if isinstance(index, slice):
            return list(map(lambda x: None if x is None else x.var, container))
        else:
            return None if container is None else container.var
        
    def __setitem__(self, index: int | slice, value: Var):
        self._list[index] = self.new_container_for(value)

    def __delitem__(self, index: int | slice):
        del self._list[index]

    def insert(self, index: int, value: Var):
        self._list.insert(index, self.new_container_for(value))


class AnimatedBinaryTreeArray(AnimatedList):

    def __init__(self, variables: Iterable[Var | None], *, radius: float, level_heights: float | None = None, node_width: float | None = None, **kwargs):

        self._radius = radius
        self.level_heights = level_heights or 3*radius
        self.node_width = node_width or 3*radius

        self._animations = AnimationBundle()

        super().__init__(variables, **kwargs)
        

   
    @property
    def animations(self):
        return self._animations
    
    @property
    def organizer(self):
        num_levels = int(np.log2(len(self))) + 1
        return BinaryTreeOrganizer(num_levels=num_levels, level_heights=self.level_heights, node_width=self.node_width, transform = self.transform)
    

    def new_container_for(self, var):
        return Node(var=var, radius=self._radius)

def main():
    config.canvas_color='off_white'
    config.drawing_stroke='dark_slate'
    config.text_fill='dark_slate'
    radius = 16
    with Canvas() as c:
        arr = AnimatedBinaryTreeArray([1,2,3,4,5,6,7,8,9,None,11], radius=radius, transform=Transform([0,-75,0], rotation=5))
        
        arr.organize()

        c << arr.elements

        arr.append(12)

        c << arr.elements



if __name__ == '__main__':
    main()