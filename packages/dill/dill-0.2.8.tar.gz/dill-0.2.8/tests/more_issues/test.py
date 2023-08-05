import dill
dill.detect.trace(True)
dill.settings['recurse'] = False

def foo(x):
  return sum(x)

dill.copy(foo)

