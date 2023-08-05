# code works, but inside docker container, throws an error
'''
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/lib/python2.7/dist-packages/dill/dill.py", line 250, in load
    obj = pik.load()
  File "/usr/lib/python2.7/pickle.py", line 858, in load
    dispatch[key](self)
  File "/usr/lib/python2.7/pickle.py", line 1246, in load_build
    for k, v in slotstate.items():
AttributeError: 'mtrand.RandomState' object has no attribute 'items'
'''
