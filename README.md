# Visuscript

Visuscript is an animation library for Python.

## ⚠️ STABILITY WARNING ⚠️

This library is currently in **early development** and is subject to rapid, breaking changes.
APIs, features, and internal structures may change without prior notice.
It is not yet recommended for production use.
Please use with caution and expect frequent updates that may require adjustments to your code.


## Getting Started

Since Visuscript is still in development and the API is changing, the documentation is incomplete as of now.
I will try my best to keep a small set of working examples through these changes in `examples/`.

I shall now walk you through setup/installation and the creation of a very basic animation.

### External Dependencies

[ffmpeg](https://ffmpeg.org/) and [librsvg](https://gitlab.gnome.org/GNOME/librsvg) must be installed. You should be able to download these through a package manager. To download with Homebrew, use

```bash
brew install ffmpeg
brew install librsvg
```

Both of these utilities' executables must be in PATH and have names `ffmpeg` and `rsvg-convert`.


### Package Installation

To install Visuscript, run the following in the root directory of this repository:
```bash
pip install -e . 
```