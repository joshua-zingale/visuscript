from abc import ABC, abstractmethod
from functools import cached_property
from typing import Sequence, Self, Union, Iterable, Callable, Iterator, TypeAlias


from visuscript.constants import Anchor
from visuscript.primatives import Transform, Vec3, Vec2, Rgb
from visuscript._internal._invalidator import Invalidatable
from visuscript.config import config
from .color import Color, HasOpacity, HasRgb

class HasTransform:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._transform = Transform()

        if isinstance(self, Invalidatable):
            self._transform._add_invalidatable(self)

    @property
    def transform(self):
        return self._transform

    def translate(
        self, x: float | None = None, y: float | None = None, z: float | None = None
    ) -> Self:
        """Sets the translation on this Drawable's Transform.

        Any of x,y, and z not set will be set in the new translation to match the current value on this Drawable's Transfom.translation.
        """
        if x is None:
            x = self.transform.translation.x
        if y is None:
            y = self.transform.translation.y
        if z is None:
            z = self.transform.translation.z

        self.transform.translation = Vec3(x, y, z)
        return self

    def scale(self, scale: int | float | Sequence[float]) -> Self:
        """Sets the scale on this Drawable's Transform."""
        self.transform.scale = scale
        return self

    def rotate(self, degrees: float) -> Self:
        """Sets the rotation on this Drawable's Transform."""
        self.transform.rotation = degrees
        return self

    def set_transform(self, transform: Transform) -> Self:
        """Sets this Drawable's Transform."""
        self._transform.update(Transform(transform))
        return self
    

class HasFill:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fill = Color(config.element_fill)

    @property
    def fill(self) -> Color:
        return Color(self._fill)
    
    @fill.setter
    def fill(self, other: Color._ColorLike):
        self.set_fill(other)

    def set_fill(self, color: Color._ColorLike) -> Self:
        """Sets the fill for this object."""
        color = Color(color)
        self._fill.rgb = color.rgb
        self._fill.opacity = color.opacity
        return self
    
class HasStroke:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stroke = Color(config.element_stroke)
        self._stroke_width = config.element_stroke_width

    @property
    def stroke(self) -> Color:
        return Color(self._stroke)
    
    @stroke.setter
    def stroke(self, other: Color._ColorLike):
        self.set_stroke(other)

    def set_stroke(self, color: Color._ColorLike) -> Self:
        """Sets the stroke for this object."""
        color = Color(color)
        self._stroke.rgb = color.rgb
        self._stroke.opacity = color.opacity
        return self
    
    @property
    def stroke_width(self) -> float:
        return self._stroke_width
    @stroke_width.setter
    def stroke_width(self, other: float):
        self.set_stroke_width(other)
    
    def set_stroke_width(self, width: float) -> Self:
        """Sets the stroke width for this object."""
        self._stroke_width = width
        return self


class HasShape(ABC):
    @abstractmethod
    def calculate_top_left(self) -> Vec2:
        """Returns the un-transformed top-left (x,y) coordinate for this object's `:class:Shape`."""
        ...
    @abstractmethod
    def calculate_width(self) -> float:
        """Returns the un-transformed width of this object's :class:`Shape`."""
        ...

    @abstractmethod
    def calculate_height(self) -> float:
        """Returns the un-transformed height of this object's :class:`Shape`."""
        ...

    def calculate_circumscribed_radius(self):
        """The radius of the smallest circle centered at this un-transformed objects's center that can circumscribe this object's :class:`Shape`."""
        return (self.calculate_width()**2 + self.calculate_height()**2) ** 0.5 / 2
    
    @cached_property
    def shape(self):
        """The un-transformed Shape for this object."""
        return Shape(self)
    
class HasTransformableShape(HasShape, HasTransform):
    @cached_property
    def transformed_shape(self):
        """The Shape for this Drawable when it has been transformed by its Transform."""
        return Shape(self, self.transform)
    
    def _invalidate(self):
        if hasattr(self, "transformed_shape"):
            del self.transformed_shape

class HasAnchor(HasShape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._anchor: Anchor = Anchor.CENTER

    def set_anchor(self, anchor: Anchor, keep_position=False) -> Self:
        """Sets thie anchor.

        :param anchor: The anchor to set for this object.
        :param keep_position: If True, updates this object's translation such that the visual position of this Drawable will not change, defaults to False
        :type keep_position: bool, optional
        :return: self
        """
        old_anchor_offset = self.anchor_offset

        self._anchor = anchor

        if isinstance(self, HasTransform) and keep_position:
            self.translate(*old_anchor_offset - self.anchor_offset)
            # Invalidate shapes
            if hasattr(self, "shape"):
                del self.shape
            if isinstance(self, HasTransformableShape) and hasattr(self, "transformed_shape"):
                del self.transformed_shape
        return self

    @property
    def anchor_offset(self) -> Vec2:
        """The (x,y) offset of this object for it to be anchored properly."""
        top_left = self.calculate_top_left()
        width = self.calculate_width()
        height = self.calculate_height()
        if self._anchor == Anchor.DEFAULT:
            return Vec2(0, 0)
        if self._anchor == Anchor.TOP_LEFT:
            return -top_left
        if self._anchor == Anchor.TOP:
            return -(top_left + [width / 2, 0])
        if self._anchor == Anchor.TOP_RIGHT:
            return -(top_left + [width, 0])
        if self._anchor == Anchor.RIGHT:
            return -(top_left + [width, height / 2])
        if self._anchor == Anchor.BOTTOM_RIGHT:
            return -(top_left + [width / 2, height])
        if self._anchor == Anchor.BOTTOM:
            return -(top_left + [width / 2, height])
        if self._anchor == Anchor.BOTTOM_LEFT:
            return -(top_left + [0, height])
        if self._anchor == Anchor.LEFT:
            return -(top_left + [0, height / 2])
        if self._anchor == Anchor.CENTER:
            return -(top_left + [width / 2, height / 2])
        else:
            raise NotImplementedError()

class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str:
        """Returns the SVG representation of this object."""
        ...


class HierarchicalDrawable(Drawable, HasTransform, HasOpacity, Iterable["HierarchicalDrawable"]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._children: list[HierarchicalDrawable] = []
        self._parent: HierarchicalDrawable | None = None

    @abstractmethod
    def draw_self(self) -> str:
        """
        Returns the SVG representation for this Element but not for its children.
        """
        ...

    def _invalidate(self):
        if hasattr(self, "global_transform"):
            del self.global_transform
        for child in self.iter_children():
            child._invalidate()

    @property
    def parent(self) -> Union["HierarchicalDrawable", None]:
        """The parent of this object if it exists, else None."""
        return self._parent

    def iter_children(self) -> Iterable["HierarchicalDrawable"]:
        yield from self._children

    def set_global_transform(self, transform: Transform) -> Self:
        """
        The global transform on this object.

        Returns the composition of all transforms, including that on this object, up this object's hierarchy.
        """
        self.global_transform = transform
        return self

    def has_ancestor(self, element: "HierarchicalDrawable") -> bool:
        """
        Returns True if `element` is an ancestor of this object.
        """
        ancestor = self
        while (ancestor := ancestor._parent) is not None:
            if ancestor == element:
                return True
        return False

    def set_parent(
        self, parent: Union["HierarchicalDrawable", None], preserve_global_transform: bool = False
    ) -> Self:
        """
        Sets this object's parent, replacing any that may have already existed.

        Also adds this object as a child of the new parent and removes it as a child of any previous parent.
        """
        if self.parent:
            self.parent._children.remove(self)

        if parent is None:
            self._parent = None
        else:
            if parent.has_ancestor(self):
                raise ValueError("Cannot set an object's descendant as its parent")

            if parent is self:
                raise ValueError("Cannot set an object to be its own parent.")

            if preserve_global_transform:
                global_transform = self.global_transform

            parent._children.append(self)
            self._parent = parent

            if preserve_global_transform:
                self.global_transform = global_transform # type: ignore

        return self

    def add_child(
        self,
        child_or_initializer: "HierarchicalDrawable" | Callable[["HierarchicalDrawable"], "HierarchicalDrawable" | Iterable["HierarchicalDrawable"]],
        preserve_global_transform: bool = False,
    ) -> Self:
        """
        Adds `child` as a child to this object. If `preserve_global_transform` is True, then the
        transform on `child` is set such that its global transform not change.
        """

        if isinstance(child_or_initializer, Callable):
            child = child_or_initializer(self)
            if isinstance(child, HierarchicalDrawable):
                child.set_parent(
                    self, preserve_global_transform=preserve_global_transform
                )
            elif isinstance(child, Iterable):
                for actual_element in child:
                    if not isinstance(actual_element, HierarchicalDrawable):
                        raise TypeError(
                            f"Cannot add child of type '{actual_element.__class__.__name__}': child must inherit from HierarcicalDrawable."
                        )
                    actual_element.set_parent(
                        self, preserve_global_transform=preserve_global_transform
                    )
        else:
            child_or_initializer.set_parent(self, preserve_global_transform=preserve_global_transform)
        return self

    def remove_child(
        self, child: "HierarchicalDrawable", preserve_global_transform: bool = True
    ) -> Self:
        """
        Removes `child` as a child to this Element. If `preserve_global_transform` is True, then the
        transform on `child` is set such that its global transform not change.
        """
        if child not in self._children:
            raise ValueError(
                "Attempted to remove a child from an Element that is not a child of the Element."
            )
        child.set_parent(None, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(
        self,
        *children: "HierarchicalDrawable" | Callable[["HierarchicalDrawable"], "HierarchicalDrawable" | Iterable["HierarchicalDrawable"]],
        preserve_global_transform: bool = False,
    ) -> Self:
        """
        Adds each input child as a child of this Element. If `preserve_global_transform` is True, then the
        transform on each child is set such that its global transform not change.
        """
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self

    @property
    def global_opacity(self) -> float:
        """
        The global opacity of this Element.

        Returns the product of all ancestor opacities and that of this Element.
        """
        curr = self

        opacity = self.opacity

        while curr._parent is not None:
            opacity *= curr._parent.opacity
            curr = curr._parent

        return opacity

    @cached_property
    def global_transform(self) -> Transform:
        """
        The global transform of this Element. Do NOT update this value manually.

        Returns the composition of all ancestor transforms and this Element's transform.

        """
        curr = self

        transform = self.transform

        if self._parent:
            transform = self._parent.global_transform @ transform
            curr = curr._parent

        return transform

    def __iter__(self) -> Iterator["HierarchicalDrawable"]:
        """
        Iterate over this Element and its children in ascending z order, secondarily ordering parents before children.
        """
        elements: list[HierarchicalDrawable] = [self]
        for child in self._children:
            elements.extend(child)

        yield from sorted(elements, key=lambda d: d.global_transform.translation.z)

    def draw(self) -> str:
        return "".join(map(lambda element: element.draw_self(), self))


class HasGlobalShape(HierarchicalDrawable, HasShape):
    def _invalidate(self):
        super()._invalidate()
        if hasattr(self, "global_shape"):
            del self.global_shape
    @cached_property
    def global_shape(self):
        return Shape(self, self.global_transform)

class Shape:
    """Holds geometric properties for an object."""

    def __init__(self, obj: HasShape, transform: Transform = Transform()):
        """
        :param obj: The object for which to initialize a :class:`Shape`.
        :param transform: Applies this transform to the :class:`Shape` of obj, defaults to Transform()
        """

        top_left = obj.calculate_top_left() + (obj.anchor_offset if isinstance(obj, HasAnchor) else 0)
        width = obj.calculate_width()
        height = obj.calculate_height()
        circumscribed_radius = obj.calculate_circumscribed_radius()

        self.width: float = width * transform.scale.x
        """The width of the object's rectangular circumscription."""

        self.height: float = height * transform.scale.y
        """The height of the object's rectangular circumscription."""

        self.circumscribed_radius: float = (
            circumscribed_radius * transform.scale.xy.max()
        )
        """The radius of the smallest circle that circumscribes the obj."""

        self.top_left: Vec2 = transform @ (top_left)
        """The top-left coordinate of the object's rectangular circumscription."""

        self.top: Vec2 = transform @ (top_left + [width / 2, 0])
        """The top-middle coordinate of the object's rectangular circumscription."""

        self.top_right: Vec2 = transform @ (top_left + [width, 0])
        """The top-right coordinate of the object's rectangular circumscription."""

        self.left: Vec2 = transform @ (top_left + [0, height / 2])
        """The left-middle coordinate of the object's rectangular circumscription."""

        self.bottom_left: Vec2 = transform @ (top_left + [0, height])
        """The bottom-left coordinate of the object's rectangular circumscription."""

        self.bottom: Vec2 = transform @ (
            top_left + [width / 2, height]
        )
        """The bottom-middle coordinate of the object's rectangular circumscription."""

        self.bottom_right: Vec2 = transform @ (
            top_left + [width, height]
        )
        """The bottom-right coordinate of the object's rectangular circumscription."""

        self.right: Vec2 = transform @ (
            top_left + [width, height / 2]
        )
        """The right-middle coordinate of the object's rectangular circumscription."""

        self.center: Vec2 = transform @ (
            top_left + [width / 2, height / 2]
        )
        """The center coordinate of the object's rectangular circumscription."""
