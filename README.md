# Visuscript

Visuscript is a two-dimensional vector-graphics-based animation library for Python, inspired by [manim](https://www.manim.community).
Visuscript is designed to facilitate the creation of didactic animations for computer-science principles.

## ⚠️ STABILITY WARNING ⚠️

This library is currently in **early development** and is subject to rapid, breaking changes.
APIs, features, and internal structures may change without prior notice.
It is not yet recommended for production use.
Please use with caution and expect frequent updates that may require adjustments to your code.


## Features
- Create arbitrary 2D graphics with Drawing and Path.
- Create arbitrary animations by composing primative Animation objects with AnimationBundle and AnimationSequence.
- Represent and animate datastructures with AnimatedCollection inheritors.
- Runtime checks for conflicting animations or updaters with PropertyLocker.
- (In my opinion) A cleaner API than [manim](https://www.manim.community).

## Getting Started

Since Visuscript is still in development and the API is changing, the documentation is incomplete as of now.
I will try my best to keep a small set of working examples through these changes in `examples/`.

I shall now walk you through setup/installation and the creation of a very basic animation.

I have tested this package with `Python 3.13.3`.

### External Dependencies

[ffmpeg](https://ffmpeg.org/) and [librsvg](https://gitlab.gnome.org/GNOME/librsvg) must be installed. You should be able to download these through a package manager. To download with Homebrew, use

```bash
brew install ffmpeg
brew install librsvg
```

Both of these utilities' executables must be in PATH and have names `ffmpeg` and `rsvg-convert`.


### Package Installation

To install Visuscript, run the following in the root directory of this repository, the directory with `setup.py` therein:
```bash
pip install -e . 
```
This will install the Visuscript package alongisde its dependencies and the `visuscript` CLI utility.
The utility should be added to PATH automatically when the package is installed.
If not, you can find the script for the CLI at root/visuscript/cli/visuscript_cli.py.

### Hello, World!

For your first visuscript, create a file called `hello_world.py` and place the following in it:
```python
from visuscript import *
with Scene() as s:
    s << Text("Hello, World!")
```

To run this visuscript, run
```bash
visuscript hello_world.py
```
This will create a new mp4 file called `output.mp4`,
which should be a very boring one frame video with a dark background and text in Arial typeface
displaying one of the ancientmost of coding rituals of initiation.


Let us now modify this visuscript to include some animation.
Update the file to contain the following and you will get color-changing, rotating, and moving text:
```python
from visuscript import *
with Scene() as s:
    text = Text("Hello, World!")
    s << text
    s.animations << AnimationSequence(
        RgbAnimation(text.fill, 'red'),
        RgbAnimation.lazy(text.fill, 'white'),
        RgbAnimation.lazy(text.fill, 'blue'),
        )
    s.animations << TransformAnimation(text.transform, Transform(
        translation=[100,-30],
        rotation=360,
        scale=2,
    ), duration = 3)
```

### What next?
Pending the stability of the API and thus the documentation, please refer to the provided examples for further learning.

## Future
I plan on seeing this project through to something useful for creating didactic animations.
I want to have a library with comparable expressiveness to [manim](https://www.manim.community)
for two-dimensional use-cases. Specifically, Visuscript is planned to have, as time may permit,
- Robust error checking.
- Clear and complete documentation.
- Base classes for common datastructures to facilitate the animation thereof.
- Abstractions for mathematical objects like cartesian planes.
