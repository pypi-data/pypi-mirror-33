from importable import *

def add(x,y):
  return x+y

squared = lambda x:x**2

class Foo(object):
  def bar(self, x):
    return x*x+x

from numpy import array
x = array([1,2,3])

assert getimportable(add) == 'from %s import add\n' % __name__
assert getimportable(squared) == 'from %s import squared\n' % __name__
assert getimportable(Foo) == 'from %s import Foo\n' % __name__
assert getimportable(Foo.bar) == 'from %s import bar\n' % __name__
assert getimportable(x) == 'from numpy import array\narray([1, 2, 3])\n'
assert getimportable(array) == 'from numpy.core.multiarray import array\n'
assert getimportable(None) == 'None\n'
assert getimportable(100) == '100\n'

f = Foo()
# getimportable(f)
#Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
#  File "./importable.py", line 31, in getimportable
#    raise AttributeError("object has no atribute '__name__'")
#AttributeError: object has no atribute '__name__'
assert getimportable(f.bar) == 'from %s import bar\n' % __name__

assert getimportable(add, byname=False) == 'def add(x,y):\n  return x+y\n'
assert getimportable(squared, byname=False) == 'squared = lambda x:x**2\n'
assert getimportable(x, byname=False) == 'from numpy import array\narray([1, 2, 3])\n'
assert getimportable(array, byname=False) == 'from numpy.core.multiarray import array\n'
assert getimportable(None, byname=False) == 'None\n'
# getimportable(Foo, byname=False)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "./importable.py", line 31, in getimportable
#     raise AttributeError("object has no atribute '__name__'")
# AttributeError: object has no atribute '__name__'
assert getimportable(Foo.bar, byname=False) == 'def bar(self, x):\n    return x*x+x\n'
assert getimportable(Foo.bar, byname=True) == 'from %s import bar\n' % __name__
assert getimportable(Foo.bar, alias='memo', byname=True) == 'from %s import bar\nmemo = bar\n' % __name__
assert getimportable(Foo, alias='memo', byname=True) == 'from %s import Foo\nmemo = Foo\n' % __name__
assert getimportable(squared, alias='memo', byname=True) == 'from %s import squared\nmemo = squared\n' % __name__
assert getimportable(squared, alias='memo', byname=False) == 'memo = squared = lambda x:x**2\n'
assert getimportable(add, alias='memo', byname=False) == 'def add(x,y):\n  return x+y\n\nmemo = add\n'
assert getimportable(None, alias='memo', byname=False) == 'memo = None\n'
assert getimportable(100, alias='memo', byname=False) == 'memo = 100\n'


# EOF
