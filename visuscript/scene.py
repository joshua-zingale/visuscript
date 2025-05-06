from visuscript.canvas import Canvas
from visuscript.animation import AnimationBundle
from visuscript.output import print_frame
from typing import Generator, Self
class Scene(Canvas):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._animation_bundle: AnimationBundle = AnimationBundle()
    
    @property
    def animations(self):
        #TODO check if the elements to be animated are elements of this scene and not already being animated
        return self._animation_bundle
    
    def print_frames(self):
        for frame in self.frames:
            print_frame(frame)

    pf = print_frames
    
    @property
    def frames(self) -> Generator[Self]:
        while self._animation_bundle.advance():
            yield self

        self._animation_bundle.clear()
