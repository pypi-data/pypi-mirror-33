import dill as pickle
import numpy as np

class testdill(object):
   def __init__(self, data):
       self.data =data

personType = [('name', 'a32'), ('age', '<i2')] 

person = np.zeros(2, dtype=personType, order='F')
d = np.random.randn(5)
d1 = testdill(d)

with open('testdill.dat', 'wb') as f:
  pickle.dump(person, f) 
  pickle.dump(d1, f)

with open('testdill.dat', 'rb') as f:
  person2 = pickle.load(f)
  d11 = pickle.load(f)

