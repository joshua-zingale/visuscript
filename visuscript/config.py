# class _Config:
#     def __init__(self):
#         self._data = {}

#     def __getattr__(self, name):
#         if name not in self._data:
#             self._data[name] = _Config()
#         return self._data[name]

#     def __setattr__(self, name, value):
#         if name == '_data':
#             super().__setattr__(name, value)
#         else:
#             self._data[name] = value

#     def __delattr__(self, name):
#         if name in self._data:
#             del self._data[name]

#     def __repr__(self):
#         return f"<Config {self._data}>"

# config: _Config
# """
# The singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
# """

class _AnimationConfig:
    def __init__(self):
        # Core animation settings
        self.fps = 30
        self.animation_duration = 0.5
        self.canvas_width = 480
        self.canvas_height = 270
        self.canvas_logical_width = 480
        self.canvas_logical_height = 270
        self.canvas_output = 0


config: _AnimationConfig = _AnimationConfig()
"""
The singleton configuration object for Visuscript, which sets defaults for various Visuscript features.
"""