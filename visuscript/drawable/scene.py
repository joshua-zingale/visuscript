"""This module contains Scene, which allows display of Drawable and animation thereof."""

from visuscript.drawable.drawable import Drawable
from visuscript.constants import Anchor, OutputFormat
from visuscript.drawable.element import Rect
from visuscript.updater import UpdaterBundle
from visuscript.primatives import *
from visuscript.config import config, ConfigurationDeference, DEFER_TO_CONFIG
from typing import Iterable, Iterator
from copy import copy
import svg

from visuscript.animation import AnimationBundle, Animation
from visuscript.updater import Updater


class Scene(Drawable):
    """A Scene can display Drawable objects under various Animations and Updaters and provides functionality to output the composite image(s).

    A Scene can receive:

    * :class:`~visuscript.drawable.Drawable` objects with :code:`scene << element`
    * :class:`~visuscript.animation.Animation` objects with :code:`scene.animations << animation`
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
        print_initial=True,
        drawables: list[Drawable] | None = None,
        width: int | ConfigurationDeference = DEFER_TO_CONFIG,
        height: int | ConfigurationDeference = DEFER_TO_CONFIG,
        logical_width: int | ConfigurationDeference = DEFER_TO_CONFIG,
        logical_height: int | ConfigurationDeference = DEFER_TO_CONFIG,
        color: str | Color | ConfigurationDeference = DEFER_TO_CONFIG,
        output_format: OutputFormat | ConfigurationDeference = DEFER_TO_CONFIG,
        output_stream: ConfigurationDeference = DEFER_TO_CONFIG,
        **kwargs,
    ):
        width = config.scene_width if width is DEFER_TO_CONFIG else width
        height = config.scene_height if height is DEFER_TO_CONFIG else height
        logical_width = (
            config.scene_logical_width
            if logical_width is DEFER_TO_CONFIG
            else logical_width
        )
        logical_height = (
            config.scene_logical_height
            if logical_height is DEFER_TO_CONFIG
            else logical_height
        )
        color = config.scene_color if color is DEFER_TO_CONFIG else color
        output_format = (
            config.scene_output_format
            if output_format is DEFER_TO_CONFIG
            else output_format
        )
        output_stream = (
            config.scene_output_stream
            if output_stream is DEFER_TO_CONFIG
            else output_stream
        )

        assert (
            width / height == logical_width / logical_height
            and width / logical_width == height / logical_height
        )

        super().__init__(**kwargs)
        self._width = width
        self._height = height
        self._logical_width = logical_width
        self._logical_height = logical_height
        self._logical_scaling = width / logical_width

        self._drawables: list[Drawable] = [] if drawables is None else list(drawables)
        self.color: Color = Color(color)

        self._output_format = output_format
        self._output_stream = output_stream
        self._print_initial = print_initial
        self._animation_bundle: AnimationBundle = AnimationBundle()
        self._player = _Player(self)

        self._original_drawables = []
        self._original_updater_bundles = []  # Track updater bundles for context manager

        self._updater_bundle: UpdaterBundle = UpdaterBundle()
        self._number_of_frames_animated: int = 0

    def clear(self):
        """Removes all :class:`~visuscript.drawable.Drawable` instances from the display."""
        self._drawables = []

    def add_drawable(self, drawable: Drawable) -> Self:
        """Adds a :class:`~visuscript.drawable.Drawable` to the display."""
        self._drawables.append(drawable)
        return self

    def add_drawables(self, drawables: Iterable[Drawable]) -> Self:
        """Adds multiple :class:`~visuscript.drawable.Drawable` instances to the display."""
        self._drawables.extend(drawables)
        return self

    def remove_drawable(self, drawable: Drawable) -> Self:
        """Removes a :class:`~visuscript.drawable.Drawable` from the display."""
        self._drawables.remove(drawable)
        return self

    def remove_drawables(self, drawables: list[Drawable]) -> Self:
        """Removes multiple :class:`~visuscript.drawable.Drawable` instnaces from the display."""
        for drawable in drawables:
            self._drawables.remove(drawable)
        return self

    def __lshift__(self, other: Drawable | Iterable[Drawable]):
        if other is None:
            return

        if isinstance(other, Drawable):
            self.add_drawable(other)
        elif isinstance(other, Iterable):
            for drawable in other:
                self << drawable
        else:
            raise TypeError(
                f"'<<' is not implemented for {type(other)}, only for types Drawable and Iterable[Drawable]"
            )

    def a(self, percentage: float) -> float:
        """
        Returns a percentage of the total logical scene area.
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

    @property
    def top_left(self) -> Vec2:
        return Vec2(0, 0)

    @property
    def width(self) -> float:
        return self._logical_width

    @property
    def height(self) -> float:
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
            - self.anchor_offset.extend(0) * self.logical_scaling,
            scale=self.logical_scaling / self.transform.scale,
            rotation=-self.transform.rotation,
        )

        background = Rect(
            width=self.width * self.logical_scaling,
            height=self.height * self.logical_scaling,
            fill=self.color,
            stroke=self.color,
            anchor=Anchor.TOP_LEFT,
        )

        # # removed deleted drawables
        # self._drawables = list(filter(lambda x: not x.deleted, self._drawables))

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                0,
                0,
                self.width * self.logical_scaling,
                self.height * self.logical_scaling,
            ),
            elements=[
                background.draw(),
                svg.G(
                    elements=[drawable.draw() for drawable in self._drawables],
                    transform=transform.svg_transform,
                ),
            ],
        ).as_str()

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
    def animations(self) -> AnimationBundle:
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
        """Any :class:`~visuscript.animation.Animation` pushed via `<<` into here will be run through instantly with the frames being printed
        and without running any of the :class:`~visuscript.animation.Animation` instances stored in :attr:`Scene.animations`."""
        if self._embed_level > 0:
            raise ValueError(
                "Cannot use Scene.player inside a context manager. Use Scene.animations instead."
            )
        return self._player

    def iter_frames(self, animation=None) -> Iterator[Self]:
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

    def _print_frames(self, animation=None):
        """Runs through all :class:`~visuscript.animation.Animation` instances herein and prints the frames to the output stream."""
        if self._print_initial:
            self.print()
            self._print_initial = False
        for _ in self.iter_frames(animation):
            self.print()

    def __enter__(self) -> Self:
        self._original_drawables.append(copy(self._drawables))
        self._original_updater_bundles.append(copy(self._updater_bundle._updaters))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._print_frames()
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
    for obj in updater_or_animation1.locker._map:
        for prop in updater_or_animation1.locker._map[obj]:
            if updater_or_animation2.locker.locks(obj, prop):
                raise LockedPropertyError(obj, prop)


class _Player:
    def __init__(self, scene: "Scene"):
        self._scene = scene

    def __lshift__(self, animation: Animation):
        _check_conflicts(animation, self._scene._updater_bundle)
        self._scene._print_frames(animation)


class _AnimationManager:
    """Wrapper for AnimationBundle that checks for conflicts with updaters."""

    def __init__(
        self, animation_bundle: AnimationBundle, updater_bundle: UpdaterBundle
    ):
        self._animation_bundle = animation_bundle
        self._updater_bundle = updater_bundle

    def push(self, animation: Animation | Iterable[Updater], _call_method="push"):
        """Adds an animation after checking for conflicts with updaters."""
        if Animation is None:
            return

        if isinstance(animation, Animation):
            _check_conflicts(animation, self._updater_bundle)
            self._animation_bundle.push(animation, _call_method)
        elif isinstance(animation, Iterable):
            for a in animation:
                self.push(a, _call_method)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Updater and Iterable[Animation], not for '{type(animation)}'"
            )

    def __lshift__(self, other: Updater | Iterable[Updater]):
        """See :func:_AnimationManager.push"""
        self.push(other, _call_method="<<")

    def __getattr__(self, name):
        """Delegate other attributes to the underlying AnimationBundle."""
        return getattr(self._updater_bundle, name)


class _UpdaterManager:
    """Wrapper for UpdaterBundle that checks for conflicts with animations."""

    def __init__(
        self, updater_bundle: UpdaterBundle, animation_bundle: AnimationBundle
    ):
        self._updater_bundle = updater_bundle
        self._animation_bundle = animation_bundle

    def push(self, updater: Updater | Iterable[Updater], _call_method="push"):
        """Adds an updater after checking for conflicts with animations."""
        if updater is None:
            return

        if isinstance(updater, Updater):
            _check_conflicts(updater, self._animation_bundle)
            self._updater_bundle.push(updater, _call_method)
        elif isinstance(updater, Iterable):
            for u in updater:
                self.push(u, _call_method)
        else:
            raise TypeError(
                f"'{_call_method}' is only implemented for types Updater and Iterable[Updater], not for '{type(updater)}'"
            )

    def __lshift__(self, other: Updater | Iterable[Updater]):
        """See :func:_UpdaterManager.push"""
        self.push(other, _call_method="<<")

    def __getattr__(self, name):
        """Delegate other attributes to the underlying UpdaterBundle."""
        return getattr(self._updater_bundle, name)


def _print_svg(scene: Scene, file=None) -> None:
    """
    Prints `scene` to the standard output as an SVG file.
    """
    print(scene.draw(), file=file)
