import dill
from test import *
#from _test import *

a = 1
def squared(x):
  return a+x**2

def foo(x):
  def bar(y):
    return squared(x)+y
  return bar

res = globalvars(foo, shallow=False)
#print res
assert set(res) == set(['squared', 'a']) #XXX: a ??
res = globalvars(foo, shallow=True)
assert res == {}


