from visuscript import *
from visuscript.organizer import BinaryTreeOrganizer
from visuscript.element import Element
from abc import ABC, abstractmethod
from typing import Generator
import sys
class Var(ABC):

    # @staticmethod
    # def updates_value(self, *args, **kwargs):
    #     pass

    def __init__(self, value, *, type_: type = str):

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
    
    # @abstractmethod
    # def update_callback(self):
    #     """Called every time this Var's value is updated."""
    #     ...
    
    # def __matmul__(self, other: "Var"):
    #     value = self.value @ other.value
    #     type_ = type(value)
    #     return Var(value, type_)
    

class Node(Var):
    def __init__(self, value, *, radius: float, type_: type = str):
        super().__init__(value, type_=type_)
        self._radius: float = radius

        self._element = Text(str(self.value), font_size=self._radius).with_children(
            Circle(radius)
        )


    @property
    def element(self) -> Element:
        return self._element
    

class BinaryTreeNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent: BinaryTreeNode | None = None
        self.left: BinaryTreeNode | None = None
        self.right: BinaryTreeNode | None = None


    def __iter__(self) -> Generator["BinaryTreeNode"]:
        yield self
        
        if self.left is not None:
            yield from self.left
        if self.right is not None:
            yield from self.right

        


class BinaryTree:
    def __init__(self):
        self.root: BinaryTreeNode | None = None



    def __getitem__(self, index: int):
        NotImplementedError("Implement me please")

    def __iter__(self) -> Generator[BinaryTreeNode]:
        if self.root is not None:
            yield from self.root
    


def main():

    radius = 16
    sep = 1.5
    
    with Canvas(anchor=Anchor.TOP).translate(y=radius*1.5) as c:
        es = [Node(i, radius=radius, type_=int).element for i in range(1,16)]
        tog = BinaryTreeOrganizer(num_levels=4, level_heights=3*radius, node_width=radius*3)
        tog.organize(es)
        for t in tog:
            print(t.translation.xy, file=sys.stderr)
        c << es

        c << Drawing(path=Path().M(*tog[0].translation.xy).L(*tog[7].translation.xy))


if __name__ == '__main__':
    main()