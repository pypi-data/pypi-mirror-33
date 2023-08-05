class Decorator(object):
    def __init__(self, item):
        self.item = item
        self.func = None
    def __call__(self, func):
        self.func = func
        return self

@Decorator(42)
def fun_1():
    pass

@Decorator(lambda x: 42)
def fun_2():
    pass

@Decorator(fun_2.item)
def fun_3():
    pass

f = lambda x: 42
@Decorator(f)
def fun_4():
    pass

import inspect
print("Inspect results")
print(inspect.getsource(fun_1.func))
print(inspect.getsource(fun_2.func))
print(inspect.getsource(fun_3.func))
print(inspect.getsource(fun_4.func))

import dill
print("Dill results")
print(dill.source.getsource(fun_1.func))
print(dill.source.getsource(fun_2.func))
print(dill.source.getsource(fun_3.func))
print(dill.source.getsource(fun_4.func))

