import dill

def foo():
  def _foo():
    if not hasattr(_foo, '_counter'):
      _foo._counter = 0
    _foo._counter += 1
    return _foo._counter
  return _foo

f = foo()
print(f())
print(f())
#dill.detect.trace(True)
print(dill.detect.errors(f))

#g = dill.copy(f)
#print(g())
