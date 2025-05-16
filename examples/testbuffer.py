from ctypes import c_char_p
import sys
class B(sys.stdout.buffer):
    @property
    def mode(self, *args, **kwargs):
        print(args)
        print(kwargs)
        return super(self).mode
    

b = B()

print(b.mode)
    


    