import numpy as np
import dill
dill.detect.trace(True)

class CustomNDArray(np.ndarray):
    def __new__(cls, inputarr, custom):
        obj = np.asarray(inputarr).view(cls)
        obj.custom = custom
        return obj
    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.custom = getattr(obj, 'custom', None)

class Foo(object):
    def __init__(self, custom_attr):
        self.a = CustomNDArray(np.arange(10), custom_attr)
        self.a.__array_finalize__(self.a)

"""

x = CustomNDArray(np.arange(10), 'bar')
y = dill.dumps(x)
z = dill.loads(y)
print(z.custom)

"""

f = Foo('bar')
print('Custom: ',f.a.custom)

p = dill.dumps(f)
p1 = dill.loads(p)
print(hasattr(p1.a, 'custom'))

#"""

# EOF
