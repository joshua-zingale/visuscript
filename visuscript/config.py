class _AnimationConfig:
    def __init__(self):
        # Core animation settings
        self.fps = 30
        self.animation_duration = 0.5
        self.canvas_width = 480
        self.canvas_height = 270
        self.canvas_logical_width = 480
        self.canvas_logical_height = 270


config: _AnimationConfig = _AnimationConfig()
"""
The singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
"""