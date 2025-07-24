from visuscript import *
from visuscript.drawable.code import PythonText, get_all_code_blocks

code_blocks = get_all_code_blocks(__file__)

##1
with Scene() as s:
    s << (
        PythonText(code_blocks[1], font_size=16)
        .set_anchor(Anchor.TOP_LEFT)
        .translate(*s.shape.top_left)
    )
##
