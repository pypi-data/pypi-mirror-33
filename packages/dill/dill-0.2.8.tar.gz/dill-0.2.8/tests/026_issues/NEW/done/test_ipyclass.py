import dill
# dill.settings['byref'] = True    # no effect
# dill.settings['recurse'] = True  # no effect
dill.settings['ignore'] = True  # no effect
 
class Foo(object):
  def bar(self, x):
    return x+self.y       
  y = 1
 
f = Foo()
_Foo = dill.dumps(Foo)
_f = dill.dumps(f)

class Foo(object):
  def bar(self, x):
    return x*self.z  
  z = -1

f_ = dill.loads(_f)
f_.y
 
"""
AttributeError                            Traceback (most recent call last)
<ipython-input-59-de94877455f9> in <module>()
     14   z = -1
     15 f_ = dill.loads(_f)
---> 16 f_.y

AttributeError: 'Foo' object has no attribute 'y'
"""
