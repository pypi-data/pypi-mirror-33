from pathos.pools import ProcessPool, ThreadPool
import logging
from pymongo import MongoClient

class PMPExample(object):
    def __init__(self):
        self.cache = {}
        self.db_userinfo_table  = MongoClient('localhost',27017).collection.example
    def compute(self, x):
        self.cache[x] = x ** 3
        return self.cache[x]

if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    r = PMPExample()
    #result = ThreadPool(4).map(r.compute, range(100))
    result = ProcessPool(4).map(r.compute, range(100))
    log.info("result processpooled caches: {}".format(result))

# FAILS: pickle.PicklingError: Can't pickle 'poll' object: <select.poll object at 0x10a9efa20>

import select
import dill
dill.copy(select.poll())

'''
# Nope, TypeError: 'NoneType' object is not callable

from pathos.multiprocessing import ProcessingPool
p = ProcessingPool(4)
...
    temp = p.map(vgg.predict, temp)

# Emphasis on temp = p.map(vgg.predict, temp)


# Start of the traceback:

Traceback (most recent call last):
  File "vgg16-extract.py", line 33, in <module>
    temp = p.map(vgg.predict, temp)
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/pathos/multiprocessing.py", line 136, in map
    return _pool.map(star(f), zip(*args)) # chunksize
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/multiprocess/pool.py", line 260, in map
    return self._map_async(func, iterable, mapstar, chunksize).get()
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/multiprocess/pool.py", line 608, in get
    raise self._value
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/multiprocess/pool.py", line 385, in _handle_tasks
    put(task)
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/multiprocess/connection.py", line 209, in send
    self._send_bytes(ForkingPickler.dumps(obj))
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/multiprocess/reduction.py", line 53, in dumps

...

# Didn't post full traceback, because is just repetitions, and in the end I got this:

...

  File "/home/bh/anaconda3/envs/keras/lib/python3.5/pickle.py", line 475, in save
    f(self, obj) # Call unbound method with explicit self
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/pickle.py", line 774, in save_list
    self._batch_appends(obj)
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/pickle.py", line 798, in _batch_appends
    save(x)
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/pickle.py", line 473, in save
    f = self.dispatch.get(t)
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/dill/dill.py", line 376, in get
    return self[key]
RecursionError: maximum recursion depth exceeded while calling a Python object
Exception ignored in: <bound method BaseSession.__del__ of <tensorflow.python.client.session.Session object at 0x7fe1da174eb8>>
Traceback (most recent call last):
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/tensorflow/python/client/session.py", line 178, in __del__
  File "/home/bh/anaconda3/envs/keras/lib/python3.5/site-packages/tensorflow/python/client/session.py", line 174, in close
TypeError: 'NoneType' object is not callable
'''



