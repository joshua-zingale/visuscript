"""This module contains Scene, which allows display of Drawable and animation thereof."""

from typing import Iterable, Iterator, no_type_check, Self, Any
from copy import copy


from visuscript.mixins import (
    Drawable,
    AnchorMixin,
    TransformMixin,
    FillMixin,
)
from visuscript.constants import Anchor, OutputFormat
from visuscript.drawable import Rect
from visuscript.updater import UpdaterBundle
from visuscript.primatives import Transform, Vec2
from visuscript.primatives.protocols import CanBeDrawn
from visuscript.config import config


from visuscript.animation import AnimationBundle, Animation
from visuscript.updater import Updater


class Scene(Drawable, AnchorMixin, TransformMixin, FillMixin):
    """Can display Drawable objects under various Animations and Updaters and provides functionality to output the composite image(s).

    A Scene can receive:

    *  Objects that :class:`~visuscript.primatives.protocols.CanBeDrawn` with :code:`scene << drawable`
    * :class:`~visuscript.animation.Animation` objects, when inside the :class:`Scene`'s context manager, with :code:`scene.animations << animation`
    * :class:`~visuscript.updater.Updater` objects with :code:`scene.updaters << updater`

    Additionally, a scene can run through a single :class:`~visuscript.animations.Animation` with :code:`scene.player << animation`

    Example with context manager::

        from visuscript import *
        with Scene() as s:
            rect = Rect(20,20)
            s << rect
            s.animations << TransformAnimation(
                rect.transform,
                Transform(
                    translation=[40,20],
                    scale=2,
                    rotation=45))

    Example without context manager::

        from visuscript import *
        s = Scene()
        rect = Rect(20,20)
        s << rect
        s.player << AnimationBundle(
            TranslationAnimation(rect.transform, [-30,-60]),
            RotationAnimation(rect.transform, 135)
            )
    """

    def __init__(
        self,
        print_initial: bool = True,
    ):
        super().__init__()

        self._width = config.scene_width
        self._height = config.scene_height
        self._logical_width = config.scene_logical_width
        self._logical_height = config.scene_logical_height
        self._logical_scaling = self._width / self._logical_width

        assert (
            self._width / self._height == self._logical_width / self._logical_height
            and self._width / self._logical_width == self._height / self._logical_height
        )

        self._drawables: list[CanBeDrawn] = []
        self.set_fill(config.scene_color)

        self._output_format = config.scene_output_format
        self._output_stream = config.scene_output_stream
        self._print_initial = print_initial
        self._animation_bundle: AnimationBundle = AnimationBundle()
        self._player = _Player(self)

        self._original_drawables: list[list[CanBeDrawn]] = []
        self._original_updater_bundles: list[list[Updater]] = []

        self._updater_bundle: UpdaterBundle = UpdaterBundle()
        self._number_of_frames_animated: int = 0

    def clear(self):
        """Removes all :class:`~visuscript.drawable.Drawable` instances from the display."""
        self._drawables = []

    def add_drawable(self, drawable: CanBeDrawn) -> Self:
        """Adds an object that :class:`~visuscript.primatives.protocols.CanBeDrawn` to the display."""
        self._drawables.append(drawable)
        return self

    def add_drawables(self, *drawables: CanBeDrawn) -> Self:
        """Adds multiple objects that :class:`~visuscript.primatives.protocols.CanBeDrawn` to the display."""
        self._drawables.extend(drawables)
        return self

    def remove_drawable(self, drawable: CanBeDrawn) -> Self:
        """Removes an object that :class:`~visuscript.primatives.protocols.CanBeDrawn` from the display."""
        self._drawables.remove(drawable)
        return self

    def remove_drawables(self, drawables: list[CanBeDrawn]) -> Self:
        """Removes multiple objects that :class:`~visuscript.primatives.protocols.CanBeDrawn` from the display."""
        for drawable in drawables:
            self._drawables.remove(drawable)
        return self

    def __lshift__(self, other: CanBeDrawn | Iterable[CanBeDrawn] | None):
        if other is None:
            return

        if isinstance(other, CanBeDrawn):
            self.add_drawable(other)
        elif isinstance(other, Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for drawable in other:
                self << drawable  # type: ignore[reportUnusedExpression]
        else:
            raise TypeError(
                f"'<<' is not implemented for {type(other)}, only for types Drawable and Iterable[Drawable]"
            )

    def a(self, percentage: float) -> float:
        """
        Returns a percentage of the total logical area of this :class:`Scene`.
        """
        return percentage * self._logical_width * self._logical_height

    def x(self, x_percentage: float) -> float:
        """Returns the logical x-position for the display that is at a percentage across the horizontal dimension from left to right."""
        return self._logical_width * x_percentage + self.anchor_offset.x

    def y(self, y_percentage: float) -> float:
        """Returns the logical y-position for the display that is at a percentage across the vertical dimension from top to bottom."""
        return self._logical_height * y_percentage + self.anchor_offset.y

    def xy(self, x_percentage: float, y_percentage: float) -> Vec2:
        """Returns both the logical x- and y-positions that are at each at a respective percentage across the
        horizontal/vertical dimension from left to right/top to bottom."""
        return Vec2(self.x(x_percentage), self.y(y_percentage))

    def calculate_top_left(self) -> Vec2:
        return Vec2(0, 0)

    def calculate_width(self) -> float:
        return self._logical_width

    def calculate_height(self) -> float:
        return self._logical_height

    @property
    def logical_scaling(self):
        return self._logical_scaling

    def draw(self) -> str:
        inv_rotation = Transform(rotation=-self.transform.rotation)

        transform = Transform(
            translation=-inv_rotation(
                self.transform.translation * self.logical_scaling / self.transform.scale
            )
            - self.anchor_offset * self.logical_scaling,
            scale=self.logical_scaling / self.transform.scale,
            rotation=-self.transform.rotation,
        )

        background = (
            Rect(
                width=self.ushape.width * self.logical_scaling,
                height=self.ushape.height * self.logical_scaling,
            )
            .set_fill(self.fill)
            .set_stroke(self.fill)
            .set_anchor(Anchor.TOP_LEFT)
        )
        view_width = self.ushape.width * self.logical_scaling
        view_height = self.ushape.height * self.logical_scaling
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}">\
{background.draw()}\
<g transform="{transform.svg_transform}">\
{" ".join([drawable.draw() for drawable in sorted(self._drawables, key=lambda d: d.extrusion)])}\
</g></svg>"""

    def print(self):
        """Prints one frame with the current state hereof."""
        if self._output_format == OutputFormat.SVG:
            _print_svg(self, file=self._output_stream)
        else:
            raise ValueError("Invalid image output format")

    @property
    def _embed_level(self):
        return len(self._original_drawables)

    @property
    def animations(self) -> "_AnimationManager":
        """The :class:`~visuscript.animation.Animation` instances stored herein to be run
        the next time this :class:`Scene`'s frames are printed."""
        if self._embed_level == 0:
            raise ValueError(
                "Cannot use Scene.animations unless in a context manager. Use Scene.player instead."
            )
        if self._embed_level > 1:
            raise ValueError(
                "Cannot use Scene.animations in an embedded context manager."
            )
        return _AnimationManager(self._animation_bundle, self._updater_bundle)

    @property
    def updaters(self):
        """The :class:`~visuscript.updater.Updater` instances stored herein to be run
        before each of this :class:`Scene`'s frames is printed."""
        if self._embed_level == 0:
            # Outside context manager - return a wrapper that checks for conflicts
            return _UpdaterManager(self._updater_bundle, self._animation_bundle)
        else:
            # Inside context manager - return a wrapper that checks for conflicts
            return _UpdaterManager(self._updater_bundle, self._animation_bundle)

    @property
    def player(self) -> "_Player":
        """Any :class:`~visuscript.animation.Animation` pushed via :code:`<<` into here will be run through instantly with the frames being printed."""
        if self._embed_level > 0:
            raise ValueError(
                "Cannot use Scene.player inside a context manager. Use Scene.animations instead."
            )
        return self._player

    def iter_frames(self, animation: Animation | None = None) -> Iterator[Self]:
        """Iterates over and consumes all frames generated by the :class:`~visuscript.animation.Animation` instances stored herien.

        The behavior is not defined if the iterator does not complete.
        """
        if animation:
            animation_to_use = animation
        else:
            animation_to_use = self._animation_bundle

        while animation_to_use.next_frame():
            self._updater_bundle.update_for_frame()
            self._number_of_frames_animated += 1
            yield self

        if animation is None:
            self._animation_bundle = AnimationBundle()

    def print_frames(self, animation: Animation | None = None):
        """Runs through all :class:`~visuscript.animation.Animation` instances herein and prints the frames to the output stream."""
        if self._print_initial:
            self.print()
            self._print_initial = False
        for _ in self.iter_frames(animation):
            self.print()

    def __enter__(self) -> Self:
        self._original_drawables.append(copy(self._drawables))
        self._original_updater_bundles.append(copy(self._updater_bundle._updaters))  # type: ignore[reportPrivateUsage]
        return self

    def __exit__(self, *_: Any):
        self.print_frames()
        self._drawables = self._original_drawables.pop()
        if self._original_updater_bundles:
            original_updaters = self._original_updater_bundles.pop()
            self._updater_bundle.clear()
            for updater in original_updaters:
                self._updater_bundle.push(updater)


def _check_conflicts(
    updater_or_animation1: Updater | Animation,
    updater_or_animation2: Updater | Animation,
):
    """Check if updater conflicts with existing animations."""
    from visuscript.property_locker import LockedPropertyError

    # Check if any properties locked by the updater are also locked by animations
    for obj in updater_or_animation1.locker._map:  # type: ignore[reportPrivateUsage]
        for prop in updater_or_animation1.locker._map[obj]:  # type: ignore[reportPrivateUsage]
            if updater_or_animation2.locker.locks(obj, prop):
                raise LockedPropertyError(obj, prop)


class _Player:
    def __init__(self, scene: "Scene"):
        self._scene = scene

    def __lshift__(self, animation: Animation):
        _check_conflicts(animation, self._scene._updater_bundle)  # type: ignore[reportPrivateUsage]
        self._scene.print_frames(animation)  # type: ignore[reportPrivateUsage]


class _AnimationManager:
    """Wrapper for AnimationBundle that checks for conflicts with updaters."""

    def __init__(
        self, animation_bundle: AnimationBundle, updater_bundle: UpdaterBundle
    ):
        self._animation_bundle = animation_bundle
        self._updater_bundle = updater_bundle

    def push(
        self,
        animation: Animation | Iterable[Animation] | None,
        _call_method: str = "push",
    ):
        """Adds an animation after checking for conflicts with updaters."""
        if animation is None:
            return

        if isinstance(animation, Animation):
            _check_conflicts(animation, self._updater_bundle)
            self._animation_bundle.push(animation, _call_method)
        elif isinstance(animation, Iterable):  # type: ignore[reportUnnecessaryIsInstance]
            for a in animation:
                self.push(a, _call_method)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Animation and Iterable[Animation], not for '{type(animation)}'"
            )

    def __lshift__(self, other: Animation | Iterable[Animation]):
        """See :func:_AnimationManager.push"""
        self.push(other, _call_method="<<")

    def __getattr__(self, name: str):
        """Delegate other attributes to the underlying AnimationBundle."""
        return getattr(self._updater_bundle, name)


class _UpdaterManager:
    """Wrapper for UpdaterBundle that checks for conflicts with animations."""

    def __init__(
        self, updater_bundle: UpdaterBundle, animation_bundle: AnimationBundle
    ):
        self._updater_bundle = updater_bundle
        self._animation_bundle = animation_bundle

    def push(
        self, updater: Updater | Iterable[Updater] | None, _call_method: str = "push"
    ):
        """Adds an updater after checking for conflicts with animations."""
        if updater is None:
            return

        if isinstance(updater, Updater):
            _check_conflicts(updater, self._animation_bundle)
            self._updater_bundle.push(updater, _call_method)
        else:
            for u in updater:
                self.push(u, _call_method)

    def __lshift__(self, other: Updater | Iterable[Updater]):
        """See :func:_UpdaterManager.push"""
        self.push(other, _call_method="<<")

    def __getattr__(self, name: str):
        """Delegate other attributes to the underlying UpdaterBundle."""
        return getattr(self._updater_bundle, name)


@no_type_check
def _print_svg(scene: Scene, file=None) -> None:
    """
    Prints `scene` to the standard output as an SVG file.
    """
    print(scene.draw(), file=file)
