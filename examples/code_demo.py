from visuscript import *
from visuscript.code import PythonText
with open(__file__, 'r') as f:
    code = f.read()
with Scene() as s:
    s << (PythonText(code, font_size=16)
          .set_anchor(Anchor.TOP_LEFT)
          .translate(*s.shape.top_left))