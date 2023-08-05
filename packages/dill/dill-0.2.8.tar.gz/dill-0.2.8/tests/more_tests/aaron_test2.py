import dill

class Foo(object):
    def __new__(cls, x, y, z):
        obj = object.__new__(cls)
        obj.x, obj.y, obj.z = x,y,z
        return obj
    def __getnewargs__(self):
        return self.x, self.y, self.z
#   def __init__(self, x, y, z):
#       self.x, self.y, self.z = x,y,z
    def bar(self):
        return self.x, self.y, self.z

f = Foo(1,2,3)
assert f.x == 1

dill.detect.trace(True)
dill.copy(f, byref=True)

