from utility import ellipse_arc_length as f
from copy import deepcopy
import sys


class Test:

    def __init__(self, a,b,c):
        self.a = a
        self.b = [a,b,c]
        self.c = [a,[b,c]]

    def __repr__(self):
        return f"{self.a} {self.b} {self.c}"
    
t = Test(1,2,3)
t2 = deepcopy(t)
t2.b[1] = 9
print(t)

# c1 = Circle()
# c2 = Circle()
# animation = c1.interpolate(c2, 3)
# animation2 = c1.move(Path().L(c2.location), 3)


# for frame in animation(24):
#     draw frame
