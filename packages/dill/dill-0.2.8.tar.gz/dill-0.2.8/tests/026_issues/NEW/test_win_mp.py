"""
ON WINDOWS 10 (apparently):

Traceback (most recent call last):
File "D:\Scripts\Thirdparty\Pathos\mp_class_example.py", line 64, in
parcompute_example()
File "D:\Scripts\Thirdparty\Pathos\mp_class_example.py", line 46, in parcompute_example
r2 = dc2.processcompute(inp_data)
File "D:\Scripts\Thirdparty\Pathos\mp_class_example.py", line 32, in processcompute
results = pool.map(self.compute, xs)
File "c:\python\anac2\lib\site-packages\pathos\multiprocessing.py", line 137, in map
return _pool.map(star(f), zip(*args)) # chunksize
File "c:\python\anac2\lib\site-packages\multiprocess\pool.py", line 251, in map
return self.map_async(func, iterable, chunksize).get()
File "c:\python\anac2\lib\site-packages\multiprocess\pool.py", line 567, in get
raise self._value
cPickle.PicklingError: Can't pickle <type 'function'>: attribute lookup builtin.function failed
"""

import dill
import pickle
import multiprocessing
from pathos.pools import ProcessPool, ThreadPool
import pathos.helpers
from multiprocessing import freeze_support
import logging
log = logging.getLogger(__name__)

class PMPExample(object):
    def __init__(self):
        self.cache = {}

    def compute(self, x):
        self.cache[x] = x ** 3
        return self.cache[x]

    def threadcompute(self, xs):
        pool = ThreadPool(4)
        results = pool.map(self.compute, xs)
        return results

    def processcompute(self, xs):
        pool = ProcessPool(4)
        results = pool.map(self.compute, xs)
        return results

def parcompute_example():
    dc = PMPExample()
    dc2 = PMPExample()
    dc3 = PMPExample()
    dc4 = PMPExample()

    n_datapoints = 100
    inp_data = range(n_datapoints)
    r1 = dc.threadcompute(inp_data)
    assert(len(dc.cache) == n_datapoints)

    r2 = dc2.processcompute(inp_data)
    assert(len(dc2.cache) == 0)
    assert(r1 == r2)

    r3 = ProcessPool(4).map(dc3.compute, inp_data)
    r4 = ThreadPool(4).map(dc4.compute, inp_data)
    assert(r4 == r3 == r2)
    assert(len(dc3.cache) == 0)
    assert(len(dc4.cache) == n_datapoints)

    log.info("Size of threadpooled class caches: {0}, {1}".format(len(dc.cache), len(dc4.cache)))
    log.info("Size of processpooled class caches: {0}, {1}".format(len(dc2.cache), len(dc3.cache)))

if __name__ == '__main__':
    pathos.helpers.freeze_support()
    logging.basicConfig()
    log.setLevel(logging.INFO)

    parcompute_example()

