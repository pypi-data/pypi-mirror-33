import multiprocess as mp

class Foo(object):
  def bar(self, x):
    return x*x

_pool = mp.Pool()
res = _pool.map(Foo().bar, range(4))
print(res)
