### itemassign ###
Note that CustomNDArray pickles the 'custom' attribute when dilled.  
However, when CustomNDArray is built inside a class method,
it fails to preserver the custom attribute.

See tests/test_classdef.py for a similar test case.

### exec ###
needs refactoring into dump and load

### ppft ###
dill.source succeeds on `readline`, but pathos.pp.ProcessPool's map fails on:

def doit(x):
  import readline
  return x

### unpickler ###
maybe fails due to using dill.loads versus cPickle.loads?


### record ###
fails when record array is pickled first. Doesn't when it's last
