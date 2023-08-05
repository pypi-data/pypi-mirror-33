#test.py
import numba as nb
import numpy as np

@nb.jit(nopython=True)
def my_fast_vector_add(x, y):
    num_elements = x.shape[0]
    z = np.zeros(num_elements, dtype=np.float64)

    for i in range(num_elements):
        z[i] = x[i] + y[i]

    return z  

class Environment():
    def __init__(self):
        self.x = np.random.rand(10)
        self.y = np.random.rand(10)

    def my_vector_add(self):
        return my_fast_vector_add(self.x, self.y)


