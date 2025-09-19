from abc import ABC, abstractmethod
from functools import cached_property
from typing import Sequence, Self, Union, Iterable, Callable, Iterator, overload
from copy import deepcopy

from visuscript.constants import Anchor
from visuscript.primatives.primatives import Transform, Vec2
from visuscript._internal._invalidator import Invalidatable
from visuscript.config import config
from .color import Color, OpacityMixin
from visuscript.lazy_object import Lazible


class TransformMixin:
    """Adds a :class:`~visuscript.Transform` to this object.

    .. note::

       This mixin provides the *local* transform, which is not affected by any ancestor's transform.
       A global transform, which is dependent on its ancestors' transforms, is provided by :class:`HierarchicalDrawable`.

    """

    def __init__(self):
        super().__init__()
        self._transform = Transform()

        if isinstance(self, Invalidatable):
            self._transform._add_invalidatable(self)  # type: ignore

    @property
    def transform(self) -> Transform:
        """The local :class:`~visuscript.Transform` for this object."""
        return self._transform

    @transform.setter
    def transform(self, other: Transform.TransformLike):
        self.set_transform(other)

    @overload
    def translate(self, x: Vec2) -> Self:
        """Sets the translation on this object's :class:`~visuscript.Transform`."""

    @overload
    def translate(self, x: float | None = None, y: float | None = None) -> Self:
        """Sets the translation on this object's :class:`~visuscript.Transform`.

        :param x: The new x value for this object's translation. If None, defaults to the current translation's x value.
        :param y: The new y value for this object's translation. If None, defaults to the current translation's y value.
        :return: self
        """

    def translate(self, x: Vec2 | float | None = None, y: float | None = None) -> Self:
        if isinstance(x, Vec2):
            self.transform.translation = x
            return self

        if x is None:
            x = self.transform.translation.x
        if y is None:
            y = self.transform.translation.y

        self.transform.translation = Vec2(x, y)
        return self

    def scale(self, scale: int | float | Sequence[float]) -> Self:
        """Sets the scale on this object's :class:`~visuscript.Transform`."""
        self.transform.scale = scale
        return self

    def rotate(self, degrees: float) -> Self:
        """Sets the rotation on this object's :class:`~visuscript.Transform`."""
        self.transform.rotation = degrees
        return self

    def set_transform(self, transform: Transform.TransformLike) -> Self:
        """Sets this object's :class:`~visuscript.Transform`."""
        self._transform.update(Transform.construct(transform))
        return self


class FillMixin:
    """Adds a fill :class:`~visuscript.Color` to this object."""

    def __init__(self):
        super().__init__()
        self._fill = Color.construct(config.element_fill)

    @property
    def fill(self) -> Color:
        """The :class:`~visuscript.Color` of this object's fill."""
        return self._fill

    @fill.setter
    def fill(self, other: Color.ColorLike):
        self.set_fill(other)

    def set_fill(self, color: Color.ColorLike) -> Self:
        """Sets this object's fill :class:`~visuscript.Color`."""
        color = Color.construct(color)
        self._fill.rgb = color.rgb
        self._fill.opacity = color.opacity
        return self


class StrokeMixin:
    """Adds a stroke :class:`~visuscript.Color` to this object."""

    def __init__(self):
        super().__init__()
        self._stroke = Color.construct(config.element_stroke)
        self._stroke_width = config.element_stroke_width

    @property
    def stroke(self) -> Color:
        """The :class:`~visuscript.Color` of this object's stroke."""
        return self._stroke

    @stroke.setter
    def stroke(self, other: Color.ColorLike):
        self.set_stroke(other)

    def set_stroke(self, color: Color.ColorLike) -> Self:
        """Sets this object's stroke :class:`~visuscript.Color`."""
        color = Color.construct(color)
        self._stroke.rgb = color.rgb
        self._stroke.opacity = color.opacity
        return self

    @property
    def stroke_width(self) -> float:
        """The width of this object's stroke."""
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, other: float):
        self.set_stroke_width(other)

    def set_stroke_width(self, width: float) -> Self:
        """Sets the width of this object's stroke."""
        self._stroke_width = width
        return self


class ShapeMixin(ABC):
    """Adds two :class:`Shape` to this object:
    A global shape :py:meth:`shape` and an un-transformed shape :py:meth:`ushape`.

    .. note::

       This mixin provides a :class:`Shape` that is unaffected by any transforms, local or global, that are applied to this object.
       For a :class:`Shape` that is transformed by the object's local transform, use :class:`TransformableShapeMixin`; and for one
       that is transformed by the object's global transform, use :class:`GlobalShapeMixin`.

       :py:meth:`ushape` will always be untransformed;
       however, :py:meth:`shape` will be upgraded to :py:meth:`tshape` or :py:meth:`gshape` if the respective mixin is added.
       This means that :py:meth:`shape` should always contain the global shape for the object.

    """

    @abstractmethod
    def calculate_top_left(self) -> Vec2:
        """Returns the un-transformed top-left (x,y) coordinate for this object's :class:`Shape`."""
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
        return (self.calculate_width() ** 2 + self.calculate_height() ** 2) ** 0.5 / 2

    @cached_property
    def ushape(self):
        """The un-transformed :class:`Shape` for this object."""
        return Shape(self)

    @property
    def shape(self):
        """The global :class:`Shape` for this object."""
        return self.ushape


class TransformableShapeMixin(ShapeMixin, TransformMixin):
    """Adds a transformed :class:`Shape` to this object."""

    @cached_property
    def tshape(self):
        """The :class:`Shape` for this object when it has been transformed by its :class:`~visuscript.Transform`."""
        return Shape(self, self.transform)

    def _invalidate(self):
        if hasattr(self, "tshape"):
            del self.tshape

    @property
    def shape(self):
        return self.tshape


class AnchorMixin(ShapeMixin):
    """Adds an anchor to this object.
    An anchor can be used to align an object to one of its sides or corners.
    """

    def __init__(self):
        super().__init__()
        self._anchor: Anchor = Anchor.CENTER

    def set_anchor(self, anchor: Anchor, keep_position: bool = False) -> Self:
        """Sets thie anchor.

        :param anchor: The anchor to set for this object.
        :param keep_position: If True, updates this object's translation such that the visual position of this object will not change.
        :return: self
        """
        old_anchor_offset = self.anchor_offset

        self._anchor = anchor

        if isinstance(self, TransformMixin) and keep_position:
            self.translate(*old_anchor_offset - self.anchor_offset)
            # Invalidate ushapes
            if hasattr(self, "ushape"):
                del self.ushape
            if isinstance(self, TransformableShapeMixin) and hasattr(self, "tshape"):
                del self.tshape
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


class Drawable(ABC, Lazible):
    """Designates an object as being Drawable."""

    _extrusion: float = 0

    @abstractmethod
    def draw(self) -> str:
        """Returns the SVG representation of this object."""
        ...

    @property
    def extrusion(self) -> float:
        """The position of this object when determining drawing order.
        Lower extrusions are drawn before higher extrusions,
        so higher extrusions are drawn over lower extrusions."""
        return self._extrusion

    @extrusion.setter
    def extrusion(self, other: float):
        self._extrusion = other

    def set_extrusion(self, extrusion: float) -> Self:
        """Sets this object's extrusion."""
        self.extrusion = extrusion
        return self


class HierarchicalDrawable(
    Drawable,
    TransformMixin,
    OpacityMixin,
    Iterable["HierarchicalDrawable"],
    Invalidatable,
):
    """Designates an object as being drawable and as being hierarchical in that
    the object will
    * be drawn whenever its parent is drawn,
    * have a global opacity as the product of its own and its ancestor's opacity,
    * and have a global :class:`Transform` that is the composition of its own and its ancestor's :class:`Transform`s.

    .. note::

        :meth:`HierarchicalDrawable.draw` should not be overwritten.
        Instead, implementers of :class:`HierarchicalDrawable` should implement :meth:`HierarchicalDrawable.draw_self`
    """

    def __init__(self):
        super().__init__()
        self._children: list[HierarchicalDrawable] = []
        self._parent: HierarchicalDrawable | None = None

    @abstractmethod
    def draw_self(self) -> str:
        """
        Returns the SVG representation of this object but not of its children.
        """
        ...

    def _invalidate(self):
        super()._invalidate()  # type: ignore
        if hasattr(self, "global_transform"):
            del self.global_transform
        for child in self.iter_children():
            child._invalidate()

    @property
    def parent(self) -> Union["HierarchicalDrawable", None]:
        """The parent of this object if it exists, else None."""
        return self._parent

    def iter_children(self) -> Iterable["HierarchicalDrawable"]:
        """Returns an iterable over all this object's children."""
        yield from self._children

    def set_global_transform(self, transform: Transform) -> Self:
        """
        The global transform on this object.

        Returns the composition of all transforms, including that on this object, up this object's hierarchy.
        """
        self.global_transform = transform
        return self

    def has_ancestor(self, drawable: "HierarchicalDrawable") -> bool:
        """
        Returns True if a drawable is one of this object's ancestors.
        """
        ancestor = self
        while (ancestor := ancestor._parent) is not None:
            if ancestor == drawable:
                return True
        return False

    def set_parent(
        self,
        parent: Union["HierarchicalDrawable", None],
        preserve_global_transform: bool = False,
    ) -> Self:
        """
        Sets this object's parent, replacing any that may have already existed.
        Also adds this object as a child of the new parent and removes it as a child of any previous parent.

        :param parent: The parent to be set for this object.
        :param preserve_global_transform: If True, the transform on this object will be modified such that its global position not change.
        :raises ValueError: if `parent` is a descendant of this object.
        :raises ValueError: if `parent` is this object itself.
        :return: self.
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
            self._invalidate()

            if preserve_global_transform:
                self.global_transform = global_transform  # type: ignore

        return self

    def add_child(
        self,
        child_or_initializer: "HierarchicalDrawable"
        | Callable[
            ["HierarchicalDrawable"],
            "HierarchicalDrawable" | Iterable["HierarchicalDrawable"],
        ],
        preserve_global_transform: bool = False,
    ) -> Self:
        """Sets a child's parent to this object.

        :param child_or_initializer: The child to be added. This may be a :class:`HierarchicalDrawable` or a function.
            If a function, the function must take a single parameter, which will be the current object, and return a :class:`HierarchicalDrawable` to be drawn.
            The functional case is useful when something about the initialization of the child depends on the parent-to-be.
        :param preserve_global_transform: If True, the transform on the child will be modified such that its global position not change.
        :return: self.

        .. seealso::

            :meth:`HierarchicalDrawable.set_parent`
        """

        if isinstance(child_or_initializer, Callable):
            child = child_or_initializer(self)
            if isinstance(child, HierarchicalDrawable):
                child.set_parent(
                    self, preserve_global_transform=preserve_global_transform
                )
            else:
                for actual_element in child:
                    actual_element.set_parent(
                        self, preserve_global_transform=preserve_global_transform
                    )
        else:
            child_or_initializer.set_parent(
                self, preserve_global_transform=preserve_global_transform
            )
        return self

    def remove_child(
        self, child: "HierarchicalDrawable", preserve_global_transform: bool = True
    ) -> Self:
        """
        Removes a child from among this objects children by settings its parent to None.

        :param child: The child to be removed.
        :param preserve_global_transform: If True, the transform on the child will be modified such that its global position not change.
        :return: self.

        .. seealso::

            :meth:`HierarchicalDrawable.set_parent`
        """
        if child not in self._children:
            raise ValueError(
                "Attempted to remove a child from an Element that is not a child of the Element."
            )
        child.set_parent(None, preserve_global_transform=preserve_global_transform)
        return self

    def add_children(
        self,
        *children: "HierarchicalDrawable"
        | Callable[
            ["HierarchicalDrawable"],
            "HierarchicalDrawable" | Iterable["HierarchicalDrawable"],
        ],
        preserve_global_transform: bool = False,
    ) -> Self:
        """
        Adds each positional argument as a child to this object.
        This is a convenience method for adding multiple children to the object.

        .. seealso::

            :meth:`HierarchicalDrawable.add_child`
        """
        for child in children:
            self.add_child(child, preserve_global_transform=preserve_global_transform)
        return self

    @property
    def global_opacity(self) -> float:
        """
        The global opacity of this Element.

        Returns the product of all ancestors' opacities and that of this object.
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
        A copy of the global transform of this Element.

        Returns the composition of all ancestor transforms and this Element's transform.
        """
        curr = self

        transform = self.transform

        if self._parent:
            transform = self._parent.global_transform @ transform
            curr = curr._parent

        return deepcopy(transform)

    def __iter__(self) -> Iterator["HierarchicalDrawable"]:
        """
        Iterate over this object and its children in ascending order of extrusion, secondarily ordering parents before children.
        """
        elements: list[HierarchicalDrawable] = [self]
        for child in self._children:
            elements.extend(child)

        yield from sorted(elements, key=lambda d: d.extrusion)

    def draw(self) -> str:
        """Returns the SVG representation of this object and that of its descendants."""
        return "".join(map(lambda element: element.draw_self(), self))


class GlobalShapeMixin(HierarchicalDrawable, TransformableShapeMixin):
    """Adds a global :class:`Shape` to this object.
    A global :class:`Shape` is its basic :class:`Shape` (accessed with `.ushape`) with its
    global :class:`~visuscript.Transform` applied to it.

    .. seealso::

        :attr:`HierarchicalDrawable.global_transform`
    """

    def _invalidate(self):
        super()._invalidate()
        if hasattr(self, "gshape"):
            del self.gshape

    @cached_property
    def gshape(self):
        """The :class:`Shape` for this object when it has been transformed by its global :class:`~visuscript.Transform`."""
        return Shape(self, self.global_transform)

    @property
    def shape(self):
        return self.gshape


class Element(
    GlobalShapeMixin, HierarchicalDrawable, AnchorMixin, FillMixin, StrokeMixin
):
    """A convenience mixin that adds all mixins that a standard vector graphic would have."""

    pass


class Shape:
    """Holds geometric properties for an object."""

    def __init__(self, obj: ShapeMixin, transform: Transform = Transform()):
        """
        :param obj: The object for which to initialize a :class:`Shape`.
        :param transform: Applies this :class:`~visuscript.Transform` to the :class:`Shape` of obj.
        """

        top_left = obj.calculate_top_left() + (
            obj.anchor_offset if isinstance(obj, AnchorMixin) else 0
        )
        width = obj.calculate_width()
        height = obj.calculate_height()
        circumscribed_radius = obj.calculate_circumscribed_radius()

        self.width: float = width * transform.scale.x
        """The width of the object's rectangular circumscription."""

        self.height: float = height * transform.scale.y
        """The height of the object's rectangular circumscription."""

        self.circumscribed_radius: float = circumscribed_radius * transform.scale.max()
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

        self.bottom: Vec2 = transform @ (top_left + [width / 2, height])
        """The bottom-middle coordinate of the object's rectangular circumscription."""

        self.bottom_right: Vec2 = transform @ (top_left + [width, height])
        """The bottom-right coordinate of the object's rectangular circumscription."""

        self.right: Vec2 = transform @ (top_left + [width, height / 2])
        """The right-middle coordinate of the object's rectangular circumscription."""

        self.center: Vec2 = transform @ (top_left + [width / 2, height / 2])
        """The center coordinate of the object's rectangular circumscription."""
