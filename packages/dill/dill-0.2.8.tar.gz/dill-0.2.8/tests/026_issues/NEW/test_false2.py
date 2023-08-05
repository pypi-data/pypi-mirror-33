import multiprocess
import dill
dill.detect.trace(True)
# dill.settings['byref'] = True

class Drive(object):
  def __init__(self, x):
    self.x = x

def test0a():
  return [Drive(1)]

def test0b():
  return Drive(1)

def test1a(x):
  return [Drive(x)]

def test1b(x):
  return Drive(x)


pool = multiprocess.Pool()
"""
res = pool.apply(test0a)
print(type(res[0]) is Drive)
res = pool.apply(test0b)
print(type(res) is Drive)
res = pool.apply(test1a,[1])
print(type(res[0]) is Drive)
"""
res = pool.apply(test1b,[1])
print(type(res) is Drive)
pool.close()

# print(type(dill.copy(test0b())) is Drive)


