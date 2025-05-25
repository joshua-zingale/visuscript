from visuscript import *
from visuscript.config import config
from data_structures import TwoPointerArray
from utility import self_string
from visuscript.text import Text, get_multiline_texts

config.canvas_output_format = OutputFormat.PNG

s = Scene()

s << Text(text="Bubble Sort", font_size=25).set_transform(Transform([120,-100], rotation=10))
s << get_multiline_texts(text=self_string(), font_size=50, anchor=Anchor.TOP_LEFT).set_transform(Transform([s.x(0) + 5, s.y(0)], scale=1/10))

arr = TwoPointerArray([6,2,3,5,1], s)

changed = True
while changed:
    changed = False
    arr.i = 1
    arr.j = 0
    while arr.i < len(arr):
        if arr[arr.j] > arr[arr.i]:
            arr.swap(arr.j, arr.i)
            changed = True
        arr.i += 1
        arr.j += 1