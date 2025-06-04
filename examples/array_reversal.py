from visuscript import *
from visuscript.animated_collection import *
WIDTH = 32
def main():
    vars = list(map(Var, [1,2,3,4,5,6,7,8]))
    arr = CellArray(vars, len(vars), transform=[-WIDTH*(len(vars) - 1)/2, 0])
    scene = Scene()
    scene << arr.collection_element
    scene.player << reverse_array(arr)

# Define the structure to animate
# Inherit from a base class that offers the types of animations we want
class CellArray(AnimatedList):
    def __init__(self, variables, max_length, *args, **kwargs):
        self.max_length = max_length
        super().__init__(variables, *args, **kwargs)
        for transform in self.organizer:
            self.add_auxiliary_element(Rect(WIDTH, WIDTH).translate(*self.transform(transform.translation)))
    def get_organizer(self):
        return GridOrganizer((1,self.max_length), (WIDTH, WIDTH))
    def new_element_for(self, var):
        return Text(f"{var.value}", font_size=WIDTH)
    
# The algorithm to be animated, which returns an animation sequence
def reverse_array(arr: CellArray):
    sequence = AnimationSequence()
    for i, j in zip(range(0,len(arr)//2), range(len(arr)-1, len(arr)//2-1, -1)):
        sequence << arr.quadratic_swap(i,j)
    return sequence

if __name__ == "__main__":
    main()