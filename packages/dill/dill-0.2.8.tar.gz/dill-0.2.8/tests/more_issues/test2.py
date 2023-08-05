import dill
dill.detect.trace(True)
dill.settings['recurse'] = False

from math import sin

def foo(x):
  return sin(x)

dill.copy(foo)

