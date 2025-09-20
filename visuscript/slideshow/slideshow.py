from typing import overload, TypeAlias, Self, Generator
import json

from visuscript.primatives.protocols import CanBeDrawn
from visuscript.animation import AnimationBundle
from visuscript.primatives import Color
from visuscript.drawable import Scene
from visuscript.config import config


class SlideTemplate:
    def __init__(self):
        self._drawables: list[CanBeDrawn] = []
        self._background: Color = Color.construct(config.scene_color)

    @property
    def drawables(self) -> list[CanBeDrawn]:
        return self._drawables

    def set_background(self, color: Color.ColorLike) -> Self:
        self.background = Color.construct(color)
        return self

    def add_drawables(self, *drawables: CanBeDrawn) -> Self:
        self._drawables.extend(drawables)
        return self

    def remove_drawables(self, *drawables: CanBeDrawn) -> Self:
        for drawable in drawables:
            self._drawables.remove(drawable)
        return self


class Slide:
    def __init__(self, template: SlideTemplate = SlideTemplate()):
        self._drawables: list[CanBeDrawn] = []
        self._animations: AnimationBundle = AnimationBundle()

        self.template: SlideTemplate = template

    def __lshift__(self, other: CanBeDrawn):
        self.push(other)

    def push(self, slide_item: CanBeDrawn) -> Self:
        self._drawables.append(slide_item)
        return self

    @property
    def animations(self):
        return self._animations

    @property
    def drawables(self):
        return self.template.drawables + self._drawables


class Slideshow:
    """Manages the creation of a slide presentation.
    Wraps around :class:`~visuscript.Scene`.
    """

    SlideTemplateName: TypeAlias = str

    def __init__(self):
        self._slides: list[Slide] = []
        self._templates: dict[str, SlideTemplate] = {"default": SlideTemplate()}
        self._scene = Scene(print_initial=False)

    @property
    def templates(self) -> dict[str, SlideTemplate]:
        return self._templates

    @overload
    def __getitem__(self, index: int) -> Slide: ...
    @overload
    def __getitem__(self, index: slice) -> list[Slide]: ...
    def __getitem__(self, index: int | slice) -> Slide | list[Slide]:
        return self._slides[index]

    def create_slide(self, template: str | SlideTemplate = "default") -> Slide:
        slide = Slide()

        if isinstance(template, str):
            slide.template = self._templates[template]
        else:
            slide.template = template

        self._slides.append(slide)
        return slide

    def print_frames(self) -> list[int]:
        """Prints all of the frames of this slideshow and returns a list containing the first frame of each slide."""

        count = 0
        frame_counts: list[int] = []
        for slide in self:
            frame_counts.append(count)
            count += 1
            self._scene.add_drawables(*slide.drawables)
            self._scene.print()
            for frame in self._scene.iter_frames(slide.animations):
                count += 1
                frame.print()

            self._scene.clear()

        return frame_counts

    def export_slideshow(self):
        """Prints all of this :class:`Slideshow`'s frames followed by a JSON readout of the slideshow data.

        .. hint::
            This should be used at the end of a script to export the slideshow for processing via the Visuscript CLI.
        """

        frame_counts = self.print_frames()

        json.dump(
            {"slide_start_frames": frame_counts, "fps": config.fps},
            config.slideshow_metadata_output_stream,
        )

    def __iter__(self) -> Generator[Slide, None, None]:
        """Iterates over all slides"""
        yield from self._slides

    def __len__(self) -> int:
        """The number of slides in this Slideshow"""
        return len(self._slides)
