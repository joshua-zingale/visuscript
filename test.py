
class A():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("__new__ A")

class B():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("__new__ B")


class C(A,B):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("__new__ C")

class D(C, A): pass

D()