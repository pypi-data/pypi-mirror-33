import pathos
import dill

class Squared(object):
  def calculate(number):
    return number**2

def get_squared_class(base_class):
  class NewSquared(base_class):
    pass
  return NewSquared

class Main(object):
  def __init__(self, squared):
    self.squared = squared
  def call_squared(self, number):
    return self.squared.calculate(number)
  def process(self):
    return multiprocessor(self.call_squared, [2,3])

def multiprocessor(worker, data):
  results = pathos.pools.ProcessPool(1).map(worker, data) #FIXME
  #results = pathos.pools.ParallelPool(1).map(worker, data)
  #results = pathos.pools.ThreadPool(1).map(worker, data)
  #results = pathos.pools.SerialPool(1).map(worker, data) #FIXME
  print("RESULTS: %s" % results)

sq = get_squared_class(Squared)

if __name__ == '__main__':
  #dill.detect.trace(True)
  #print(dill.copy(sq))
  m = Main(sq)
  #print(dill.copy(m.call_squared))
  m.process()
