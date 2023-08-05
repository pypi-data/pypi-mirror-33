import cloudpickle


class A(object):
    pass


class B(A):
    def foo(self):
        super()


NewB = cloudpickle.loads(cloudpickle.dumps(B))
b = NewB()

import dill
dill.dumps(b)

"""
The error does not happen in either of the following cases:

    the classes are imported from a module;
    class B doesn't use super(), i.e. if it's defined like this:

class B(A):
    def foo(self):
        A()
        B()
"""
