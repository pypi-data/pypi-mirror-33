import dill as pickle
import numpy as np

class testdill:
   def __init__(self, data):
       self.data =data

# numpy record array type
personType = [('name', 'a32'), ('age', '<i2'), ('salary', '<i4'), ('weight','<f8')] 


person = np.zeros(2, dtype=personType, order='F')
d = np.random.randn(5)
d1 = testdill(d)

d = np.random.randn(5)
d2 = testdill(d)

d = np.random.randn(5)
d3 = testdill(d)


f= open('testdill.dat', 'wb')
pickle.dump(person, f) 
pickle.dump(d1, f)
pickle.dump(d2, f)
pickle.dump(d3, f)

f.close()

f= open('testdill.dat', 'rb')

person2 = pickle.load(f)
d11 = pickle.load(f)
d21 = pickle.load(f)
d31 = pickle.load(f)
