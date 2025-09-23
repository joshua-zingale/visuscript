"""Contains the :class:`Animation` type, constructors for :class:`Animation` types, and interpolation and easing modules."""
from .primatives import Animation

from .animation_store import AnimationBundle, AnimationSequence


from .property_animations import (
    animate_translation,
    animate_scale,
    animate_rotation,
    animate_rgb,
    animate_opacity,
)

from .animations import (
    wait,
    run,
    animate_path,
    animate_updater,
    quadratic_swap,
    fade_in,
    fade_out,
    flash,
    animate_transform,
)

from .constructors import (
    sequence,
    bundle,
    construct,
    laze,
)

from . import easing, interpolation

__all__ = [
    "Animation",
    "AnimationSequence",
    "AnimationBundle",
    "animate_translation",
    "animate_scale",
    "animate_rotation",
    "animate_transform",
    "animate_rgb",
    "animate_opacity",
    "animate_path",
    "animate_updater",
    "quadratic_swap",
    "fade_in",
    "fade_out",
    "flash",
    "wait",
    "run",
    "sequence",
    "bundle",
    "construct",
    "laze",
    "easing",
    "interpolation"
]
