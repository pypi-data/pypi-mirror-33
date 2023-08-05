>>> from test_source import *
>>> from test_source import _foo, _bar
>>> from test_mixins import *
>>> import _more_inspect as mi
>>> 
>>> print mi.getsource(quadratic)
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func

>>> print mi.getsource(quadratic, enclosing=True)
def quad_factory(a=1,b=1,c=0):
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func
  return dec

>>> mi._getfreevars(quadratic)
{'a': 1, 'c': 0, 'b': 1}
>>> mi._getglobalvars(quadratic)
{}
>>> mi._getvarnames(quadratic)
(('f', 'func'), ('f',))
>>> quadratic.__name__
'dec'
>>> 
>>> print mi.getsource(quadish, enclosing=True)
def quad_factory(a=1,b=1,c=0):
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func
  return dec

>>> print mi.getsource(quadish, enclosing=False)
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c

>>> mi._getfreevars(quadish)
{'a': 0, 'c': 0, 'b': 4, 'f': <function quadish at 0x1062a4410>}
>>> mi._getglobalvars(quadish)
{}
>>> mi._getvarnames(quadish)
(('args', 'kwds', 'fx'), ())
>>> 
>>> 
>>> ### NOTE: is decorated, so this plus enclosed source works
>>> print mi.getsource(mi._getfreevars(quadish)['f'])
@quad_factory(a=0,b=4,c=0)
def quadish(x):
  return x+1

>>> print mi.getsource(quadish, enclosing=True)
def quad_factory(a=1,b=1,c=0):
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func
  return dec

>>> #XXX#: WORKS
>>> dd.freevars(quadish)
{'a': 0, 'c': 0, 'b': 4, 'f': <function quadish at 0x10bb51500>}
>>> 
>>> free_vars = dd.freevars(quadish)
>>> ds.getimport(free_vars['f']) #XXX: isfunction
'from test_mixins import quadish\n'
>>> 
>>> ### FIXME: was built quadratic = quad_factory()... how to discover this?
>>> print mi.getsource(quadratic, enclosing=True)
def quad_factory(a=1,b=1,c=0):
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func
  return dec

>>> mi._getfreevars(quadratic)
{'a': 1, 'c': 0, 'b': 1}
>>> mi._getglobalvars(quadratic)
{}
>>> mi._getvarnames(quadratic)
(('f', 'func'), ('f',))
>>>                 
>>> ### SOLVED: if no function in freevars, we use enclosing=False
>>> print mi.getsource(quadratic, enclosing=False, lstrip=True)
def dec(f):
  def func(*args,**kwds):
    fx = f(*args,**kwds)
    return a*fx**2 + b*fx + c
  return func

>>> mi._getfreevars(quadratic)
{'a': 1, 'c': 0, 'b': 1}
>>> 
>>> #XXX#: SOLVED
>>> _x = dd.outermost(quadratic)
>>> lines, lnum = ds.findsource(_x)
>>> candidate = [line for line in lines if getname(_x) in line]
>>> candidate = [line for line in candidate if re.match('.*[\w\s]=\s*'+getname(_x)+'\(', line)]
>>> candidate = None if not len(candidate) else candidate[-1]
>>> candidate.split('=',1)[0].split()[-1].strip()
'quadratic'
>>>
>>> 
>>> print mi.getsource(quadruple, enclosing=True)
def doubler(f):
  def inner(*args, **kwds):
    fx = f(*args, **kwds)
    return 2*fx
  return inner

>>> mi._getfreevars(quadruple)
{'f': <function quadruple at 0x1062a4578>}
>>> mi._getglobalvars(quadruple)
{}
>>> mi._getvarnames(quadruple)
(('args', 'kwds', 'fx'), ())
>>> print mi.getsource(mi._getfreevars(quadruple)['f'])
@doubler
def quadruple(x):
  return 2*x

>>> print mi.getsource(quadratic)
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func

>>> print mi.getsource(quadratic)
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func

>>> print mi.getsource(quadratic, enclosing=True)
def quad_factory(a=1,b=1,c=0):
  def dec(f):
    def func(*args,**kwds):
      fx = f(*args,**kwds)
      return a*fx**2 + b*fx + c
    return func
  return dec

>>> mi._getfreevars(quadratic)
{'a': 1, 'c': 0, 'b': 1}
>>> mi._getglobalvars(quadratic)
{}
>>> mi._getvarnames(quadratic)
(('f', 'func'), ('f',))
>>> 
>>> mi._getfreevars(quadruple)
{'f': <function quadruple at 0x1062a4578>}
>>> mi._getglobalvars(quadruple)
{}
>>> mi._getvarnames(quadruple)
(('args', 'kwds', 'fx'), ())
>>> 
>>> 
>>> def double(x):
...   return 2*x
... 
>>> _quadrupler = doubler(double)
>>> 
>>> _quadrupler(3)
12
>>> 
>>> print mi.getsource(_quadrupler, enclosing=True)
def doubler(f):
  def inner(*args, **kwds):
    fx = f(*args, **kwds)
    return 2*fx
  return inner

>>> mi._getfreevars(_quadrupler)
{'f': <function double at 0x1062ae6e0>}
>>> mi._getglobalvars(_quadrupler)
{}
>>> mi._getvarnames(_quadrupler)
(('args', 'kwds', 'fx'), ())
>>> 
>>> mi._getfreevars(quadruple)
{'f': <function quadruple at 0x1062a4578>}
>>> mi._getglobalvars(quadruple)
{}
>>> mi._getvarnames(quadruple)
(('args', 'kwds', 'fx'), ())
>>> 
>>> print mi.getsource(mi._getfreevars(quadruple)['f'])
@doubler
def quadruple(x):
  return 2*x

>>> print mi.getsource(mi._getfreevars(_quadrupler)['f'])
def double(x):
  return 2*x

>>> ### FIXME: was built _quadrupler = doubler(double)... how to discover this?
>>> print mi.getsource(_quadrupler, enclosing=True)
def doubler(f):
  def inner(*args, **kwds):
    fx = f(*args, **kwds)
    return 2*fx
  return inner

>>> print mi.getsource(mi._getfreevars(_quadrupler)['f'])
def double(x):
  return 2*x

>>> ### SOLVED: if no decorator found, we use an alias, and enclosing=False
>>> print mi.getsource(_quadrupler, enclosing=False, lstrip=True)
def inner(*args, **kwds):
  fx = f(*args, **kwds)
  return 2*fx

>>> mi._getfreevars(_quadrupler)
{'f': <function double at 0x1062ae6e0>}
>>> print mi.getsource(mi._getfreevars(_quadrupler)['f'], alias='f')
def double(x):
  return 2*x

f = double

>>> 
>>> #XXX#: SOLVED
>>> _x = dd.outermost(_quadrupler)
>>> _y = dd.freevars(_quadruple)['f']
>>> xlines, lnum = ds.findsource(_x)
>>> ylines, lnum = ds.findsource(_y)
>>> candidate = [line for line in xlines if getname(_x) in line]
>>> candidate = [line for line in candidate if re.match('.*[\w\s]=\s*'+getname(_x)+'\(', line)]
>>> #XXX: if not candidate:
>>> candidate = [line for line in ylines if getname(_y) in line]
>>> candidate = [line for line in candidate if re.match('.*[\w\s]=\s*'+getname(_y)+'\(', line)]
>>> candidate = None if not len(candidate) else candidate[-1]
>>> candidate.split('=',1)[0].split()[-1].strip()
'_quadruple'
>>>
>>> 
>>> ### NOTE: this works fine; was built with a decorator (not by assignment)
>>> print mi.getsource(quadruple, enclosing=True)
def doubler(f):
  def inner(*args, **kwds):
    fx = f(*args, **kwds)
    return 2*fx
  return inner

>>> print mi.getsource(mi._getfreevars(quadruple)['f'])
@doubler
def quadruple(x):
  return 2*x

>>> #XXX#: WORKS
>>> dd.freevars(quadruple)
{'f': <function quadruple at 0x10bb51668>}
>>> 
>>> free_vars = dd.freevars(quadruple)
>>> ds.getimport(free_vars['f']) #XXX: isfunction
'from test_mixins import quadruple\n'
>>> 


###############

                    if name in line: break
                    if pat2.match(line): # however it might have a decorator...
                        code = getblock(lines[lnum:])
                        for _line in code[1:]:
                            isdecorated = name in _line
                            if not pat2.match(_line): break
                        if code[1:] and isdecorated: break

