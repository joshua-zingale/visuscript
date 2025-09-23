import typing as t

from .primatives import Transform, Vec2



class HasCalculatableShape(t.Protocol):

    def calculate_top_left(self) -> Vec2: ...
    def calculate_width(self) -> float: ...
    def calculate_height(self) -> float: ...
    def calculate_circumscribed_radius(self) -> float: ...

@t.runtime_checkable
class HasAnchorOffset(t.Protocol):
    @property
    def anchor_offset(self) -> Vec2: ...



class Shape:
    """Holds geometric properties for an object."""

    def __init__(self, obj: HasCalculatableShape, transform: Transform = Transform()):
        """
        :param obj: The object for which to initialize a :class:`Shape`.
        :param transform: Applies this :class:`~visuscript.Transform` to the :class:`Shape` of obj.
        """

        top_left = obj.calculate_top_left() + (
            obj.anchor_offset if isinstance(obj, HasAnchorOffset) else 0
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