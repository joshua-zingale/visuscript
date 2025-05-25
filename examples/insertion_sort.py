from data_structures import TwoPointerArray
from visuscript import *
from visuscript.config import config

config.canvas_output_format = OutputFormat.PNG

def main():
    s = Scene()
    s << Rect(width=30,height=30, transform=[-200, -100]).add_child(Text(text="unsorted", font_size = 20, transform=[20, -10], anchor=Anchor.TOP_LEFT))
    s << Rect(width=30,height=30, fill="blue", stroke="off_white", transform=[-200, -65]).add_child(Text(text="sorted", font_size = 20, transform=[20, -10], anchor=Anchor.TOP_LEFT))

    arr = TwoPointerArray([6,3,1,5,7,0], s, auto_print=True, mark_i_visited=True)
    
    arr.i = 1
    while arr.i < len(arr):
        arr.j = arr.i - 1
        while arr.j >= 0 and arr[arr.j] > arr[arr.i]:
            arr.j -= 1

        arr.j += 1

        if arr.i != arr.j:
            arr.storage = arr[arr.i]
            for i in range(arr.i, arr.j, -1):
                arr[i] = arr[i-1]

            arr[arr.j] = arr.storage
        arr.i += 1


if __name__ == "__main__":
    main()