"""Visuscript is a vector-graphics-based Animation library for Python.

The core class that drives Visuscript's functionality is :class:`~visuscript.canvas.Scene`.
Refer to the documentation for :class:`~visuscript.canvas.Scene` to see how to create Python scripts from which Visuscript can generate a movie.

To create an video with Visuscript, use the command-line utility, :mod:`~visuscript.cli.visuscript_cli`.
If Visuscript was installed using pip,
this utility should have been added to the environment's PATH with the name :code:`visuscript`.
Thus, after having created a Python script, use the following to generate a movie and output it as `output.mp4`:

.. code-block:: bash

    visuscript path/to/script.py

If the utility is not added to your PATH, the following works as well:

.. code-block:: bash

    python3 /path/to/visuscript-root-directory/visuscript/cli/visuscript_cli.py path/to/script.py

"""

from .element import Circle, Rect, Image, Pivot, Drawing
from .primatives import Transform, Color, Vec2, Vec3, Rgb
from .canvas import Canvas, Scene
from .organizer import GridOrganizer
from .text import Text
from .segment import Path
from .constants import (
    Anchor,
    OutputFormat,
    UP, RIGHT, DOWN, LEFT, FORWARD, BACKWARD, 
    )
from .updater import UpdaterBundle, TranslationUpdater, FunctionUpdater, run_updater
from .animation import (
    AnimationBundle,
    AnimationSequence,
    TransformAnimation,
    TranslationAnimation,
    ScaleAnimation,
    RotationAnimation,
    PathAnimation,
    OpacityAnimation,
    NoAnimation,
    RunFunction,
    RgbAnimation,
    UpdaterAnimation,
    fade_in,
    fade_out,
    flash
    )