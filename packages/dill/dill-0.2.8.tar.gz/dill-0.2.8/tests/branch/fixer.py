import functools

from math import sin
def foo(x):
  return x

#update_wrapper
foo.__orig__ = {}
[foo.__orig__.update({i:getattr(foo,i)}) for i in functools.WRAPPER_ASSIGNMENTS]
functools.update_wrapper(foo, sin)
print foo.__doc__
print foo.__name__
print foo.__module__

#revert_wrapper
##store current stuff
[setattr(foo,i,j) for (i,j) in foo.__orig__.items()]
##unpickle
##restore what was current stuff
