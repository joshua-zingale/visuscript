from visuscript import *
from visuscript.animation import Animation
from visuscript.organizer import BinaryTreeOrganizer
from visuscript.element import Element
from abc import ABC, abstractmethod
from visuscript.primatives import Vec3
from typing import Generator, Collection, Self, Iterable, Union
import sys
class Var(ABC):

    # @staticmethod
    # def updates_value(self, *args, **kwargs):
    #     pass

    def __init__(self, value, *, type_: type | None = None):

        if type_ is None:
            type_ = type(value)

        self._value = type_(value)
        self._type = type_
        # self.translation = Vec3(0,0,0)

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
    
    # @abstractmethod
    # def update_callback(self):
    #     """Called every time this Var's value is updated."""
    #     ...
    
    # def __matmul__(self, other: "Var"):
    #     value = self.value @ other.value
    #     type_ = type(value)
    #     return Var(value, type_)
    

class Node:
    def __init__(self, *, var: Var, radius: float):

        self._var = var
        self._radius: float = radius

        self._element = Text(str(self._var), font_size=self._radius).with_children(
            Circle(radius)
        )

    @property
    def data(self) -> Var:
        return self._var

    @property
    def element(self) -> Element:
        return self._element
    

class BinaryTreeNode(Node):

    def __init__(self, *, var: Var, radius: float):
        super().__init__(var=var, radius=radius)

        self._parent: BinaryTreeNode | None = None
        self._left: BinaryTreeNode | None = None
        self._right: BinaryTreeNode | None = None

    @property
    def is_left_child(self) -> bool:
        return self._parent is not None and self._parent.left is self
    
    @property
    def is_right_child(self) -> bool:
        return self._parent is not None and self._parent.right is self

    def __iter__(self) -> Generator["BinaryTreeNode"]:
        yield self
        
        if self.left is not None:
            yield from self.left
        if self.right is not None:
            yield from self.right

    @property
    def parent(self) -> Union["BinaryTreeNode", None]:
        return self._parent
        
    @property
    def left(self) -> Union["BinaryTreeNode", None]:
        return self._left
    @left.setter
    def left(self, value: Union["BinaryTreeNode", None]):
        if value is not None:
            value._parent = self
        self._left = value
    @property
    def right(self) -> Union["BinaryTreeNode", None]:
        return self._right
    @right.setter
    def right(self, value: Union["BinaryTreeNode", None]):
        if value is not None:
            value._parent = self
        self._right = value

    # def bfs(self) -> Generator["BinaryTreeNode"]:
    #     queue = [self]
    #     while len(queue) > 0:
    #         node = queue.pop(0)

    #         yield node

    #         if node.left is not None:
    #             queue.append(self.left)
    #         if node.right is not None:
    #             queue.append(self.right)


class AnimatedCollection(Collection[Var]):

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
    


class BinaryTree(AnimatedCollection):
    def __init__(self, *, num_levels, level_heights, node_width):
        self.root: BinaryTreeNode | None = None
        self._organizer = BinaryTreeOrganizer(num_levels=num_levels, level_heights=level_heights, node_width=node_width)
        self._animations = AnimationBundle()
        self._nodes: list[BinaryTreeNode | None] = [None] * (2**(num_levels) - 1)

        

    def organize(self):
        for node in self:
            var = node.data
            transform = self.target_transform(var)
            node.element.set_transform(transform)

    def target_transform(self, var: Var):
        return self._organizer[self._get_index(var)]
    
    @property
    def animations(self):
        return self._animations
    
    @property
    def elements(self) -> Generator[Element]:
        for node in self:
            yield node.element

    def _get_index(self, var: Var):
        index = BinaryTree._get_index_helper(root=self.root, var=var)

        if index is None:
            raise ValueError("var does not exist in BinaryTree.")
        
        return index
    
    @staticmethod
    def _get_index_helper(root: BinaryTreeNode, var: Var, index = 1) -> int | None:
        if root.data is var:
            return index - 1
        
        if root.left is not None:
            maybe_index = BinaryTree._get_index_helper(root.left, var, index=2*index)
            if maybe_index is not None:
                return maybe_index
        if root.right is not None:
            maybe_index = BinaryTree._get_index_helper(root.right, var, index=2*index + 1)
            if maybe_index is not None:
                return maybe_index

        return None
        
    def __len__(self):
        len_ = 0
        for _ in self:
            len_ += 1
        return len_

    def __contains__(self, var: Var) -> bool:
        for contained_var in self:
            if contained_var == var:
                return True
        return False


    def __iter__(self) -> Generator[BinaryTreeNode]:
        if self.root is not None:
            yield from self.root #map(lambda x: x.data, self.root)
    




def main():

    

    radius = 16

    
    with Canvas(anchor=Anchor.TOP).translate(y=radius*1.5) as c:
        es = [BinaryTreeNode(radius=radius, var=Var(i)).element for i in range(1,16)]
        
        root = BinaryTreeNode(radius=radius, var=Var(1))

        root.left = BinaryTreeNode(radius=radius, var=Var(2))

        root.right = BinaryTreeNode(radius=radius, var=Var(3))

        root.left.right = BinaryTreeNode(radius=radius, var=Var(5))
        root.left.right.right = BinaryTreeNode(radius=radius, var=Var(11))
        


        bt = BinaryTree(num_levels=4,level_heights=48,node_width=48)

        bt.root = root

        bt.organize()
        
        c << bt.elements




        # tog = BinaryTreeOrganizer(num_levels=4, level_heights=3*radius, node_width=radius*3)
        # tog.organize(es)
        # for t in tog:
        #     print(t.translation.xy, file=sys.stderr)
        # c << es

        # c << Drawing(path=Path().M(*tog[0].translation.xy).L(*tog[7].translation.xy))


if __name__ == '__main__':
    main()


# from visuscript import *
# from visuscript.animation import Animation
# from visuscript.organizer import BinaryTreeOrganizer
# from visuscript.element import Element
# from abc import ABC, abstractmethod
# from visuscript.primatives import Vec3
# from typing import Generator, Collection, Self, Iterable, Union
# import sys
# class Var(ABC):

#     # @staticmethod
#     # def updates_value(self, *args, **kwargs):
#     #     pass

#     def __init__(self, value, *, type_: type | None = None):

#         if type_ is None:
#             type_ = type(value)

#         self._value = type_(value)
#         self._type = type_
#         # self.translation = Vec3(0,0,0)

#     @property
#     def drawable(self) -> Text:
#         return self._text
    
#     @property
#     def value(self):
#         return self._value
    
#     def __add__(self, other: "Var"):
#         value = self.value + other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __sub__(self, other: "Var"):
#         value = self.value - other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __mul__(self, other: "Var"):
#         value = self.value * other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __truediv__(self, other: "Var"):
#         value = self.value / other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __mod__(self, other: "Var"):
#         value = self.value % other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __floordiv__(self, other: "Var"):
#         value = self.value // other.value
#         type_ = type(value)
#         return Var(value, type_)
    
#     def __pow__(self, other: "Var"):
#         value = self.value ** other.value
#         type_ = type(value)
#         return Var(value, type_)
    

#     def __gt__(self, other: "Var") -> bool:
#         return self.value > other.value
#     def __ge__(self, other: "Var") -> bool:
#         return self.value >= other.value
#     def __eq__(self, other: "Var") -> bool:
#         return self.value == other.value
#     def __le__(self, other: "Var") -> bool:
#         return self.value <= other.value
#     def __lt__(self, other: "Var") -> bool:
#         return self.value < other.value
    
#     def __str__(self):
#         return str(self.value)
    
#     # @abstractmethod
#     # def update_callback(self):
#     #     """Called every time this Var's value is updated."""
#     #     ...
    
#     # def __matmul__(self, other: "Var"):
#     #     value = self.value @ other.value
#     #     type_ = type(value)
#     #     return Var(value, type_)
    

# class Node:
#     def __init__(self, *, data: Var, radius: float):

#         self._var = data
#         self._radius: float = radius

#         self._element = Text(str(self._var), font_size=self._radius).with_children(
#             Circle(radius)
#         )

#     @property
#     def data(self) -> Var:
#         return self._var

#     @property
#     def element(self) -> Element:
#         return self._element
    
# class AnimatedCollection(Collection[Var]):

#     @property
#     @abstractmethod
#     def animations(self) -> Iterable[Animation]:
#         ...
    
#     @property
#     @abstractmethod
#     def elements(self) -> Iterable[Element]:
#         ...


#     # @property
#     # @abstractmethod
#     # def removed(self) -> dict[Var, Element]:
#     #     """Returns a dictionary mapping Var objects that have been removed since the last finish of the Animations in this Structure."""
#     #     ...

#     # @abstractmethod
#     # def remove(self, var: Var) -> Self:
#     #     ...


# class BinaryTreeNode(Node):

#     def __init__(self, *, data: Var, radius: float, tree: "BinaryTree"):
#         super().__init__(data=data, radius=radius)

#         self._tree = tree
#         self._tree._unplaced_nodes.add(self)

#     @property
#     def is_unplaced(self):
#         return self in self._tree._unplaced_nodes
    
#     @property
#     def _index(self) -> int:
#         return self._tree._nodes.index(self)
    
#     @property
#     def _left_index(self) -> int:
#         return (self._index+1)*2-1
    
#     @property
#     def _right_index(self) -> int:
#         return (self._index+1)*2
    

#     @property
#     def is_root(self) -> bool:
#         return self._index == 0

#     @property
#     def is_left_child(self) -> bool:
#         return self._index % 2 == 1
    
#     @property
#     def is_right_child(self) -> bool:
#         return self._index % 2 == 0

#     @property
#     def parent(self) -> Union["BinaryTreeNode", None]:
#         if self.is_root or self.is_unplaced:
#             return None
#         return self._tree._nodes[(self._index + 1)//2 - 1]
        
#     @property
#     def left(self) -> Union["BinaryTreeNode", None]:
#         if self._left_index >= len(self._tree._nodes):
#             return None
#         return self._tree._nodes[self._left_index]
#     @left.setter
#     def left(self, value: Union["BinaryTreeNode", None]):
#         self._tree._nodes[self._left_index] = value
#     @property
#     def right(self) -> Union["BinaryTreeNode", None]:
#         if self._right_index >= len(self._tree._nodes):
#             return None
#         return self._tree._nodes[self._right_index]
    
#     @right.setter
#     def right(self, value: Union["BinaryTreeNode", None]):
#         self._tree._nodes[self._right_index] = value


#     # def bfs(self) -> list["BinaryTreeNode"]:
#     #     queue = [self]

#     #     for node in queue:
#     #         if node.left:
#     #             queue.append(node.left)
#     #         if node.right:
#     #             queue.append(node.right)

#     #     return queue





#     def __iter__(self) -> Generator["BinaryTreeNode"]:
#         yield self
        
#         if self.left is not None:
#             yield from self.left
#         if self.right is not None:
#             yield from self.right



# class BinaryTree(AnimatedCollection):
#     def __init__(self, *, num_levels, level_heights, node_width, radius: float):

        
#         self._organizer = BinaryTreeOrganizer(num_levels=num_levels, level_heights=level_heights, node_width=node_width)
#         self._animations = AnimationBundle()
#         self._nodes: list[BinaryTreeNode | None] = [None] * (2**(num_levels) - 1)
#         self._unplaced_nodes: set[BinaryTreeNode] = set()
#         self._radius = radius
#     @property
#     def root(self):
#         return self._nodes[0]

#     @root.setter
#     def root(self, value: BinaryTreeNode | None):
#         for node in filter(lambda x: x, self._nodes):
#             self._unplaced_nodes.add(node)

#         nodes = [None] * len(self._nodes)

#         if value.is_unplaced:
#             nodes[0] = value
#             self._nodes = nodes
#             self._unplaced_nodes.discard(value)
#             return

#         queue = [(value, 1)]

#         for node, index in queue:

#             nodes[index-1] = node
#             self._unplaced_nodes.remove(node)

#             if node.left:
#                 queue.append((node.left, index*2))
#             if node.right:
#                 queue.append((node.right, index*2 + 1))

#         self._nodes = nodes
        


#     def get_node(self, data: Var, radius: float | None = None):
#         return BinaryTreeNode(data=data, radius=radius or self._radius, tree=self)

#     def organize(self):
#         self._organizer.organize(map(lambda x: x.element if x else x, self._nodes))

#     def target_transform(self, var: Var):
#         index = self._nodes.index(var)
#         return self._organizer[index]
    
#     @property
#     def animations(self):
#         return self._animations
    
#     @property
#     def elements(self) -> Generator[Element]:
#         for node in self:
#             yield node.element

        
#     def __len__(self):
#         len_ = 0
#         for _ in self:
#             len_ += 1
#         return len_

#     def __contains__(self, var: Var) -> bool:
#         for contained_var in self:
#             if contained_var == var:
#                 return True
#         return False

#     def __iter__(self) -> Generator[BinaryTreeNode]:
#         if self.root is not None:
#             yield from self.root
    




# def main():

#     radius = 16

    
#     with Canvas(anchor=Anchor.TOP).translate(y=radius*1.5) as c:
#         # es = [BinaryTreeNode(radius=radius, data=Var(i)).element for i in range(1,16)]
#         bt = BinaryTree(num_levels=4,level_heights=48,node_width=48, radius=radius)
        
#         root = bt.get_node(data=Var(1))
#         bt.root = root


#         root.left = bt.get_node(data=Var(2))

#         root.right = bt.get_node(data=Var(3))

#         root.left.right = bt.get_node(data=Var(5))
#         root.left.right.right = bt.get_node(data=Var(11))
        

#         bt.organize()
        
#         c << bt.elements




#         # tog = BinaryTreeOrganizer(num_levels=4, level_heights=3*radius, node_width=radius*3)
#         # tog.organize(es)
#         # for t in tog:
#         #     print(t.translation.xy, file=sys.stderr)
#         # c << es

#         # c << Drawing(path=Path().M(*tog[0].translation.xy).L(*tog[7].translation.xy))


# if __name__ == '__main__':
#     main()