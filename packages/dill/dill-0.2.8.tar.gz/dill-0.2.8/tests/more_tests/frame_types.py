import dill
def _function(x): yield x;

g = _function(1)
f = g.gi_frame
def _f():
  try: raise
  except:
    from sys import exc_info
    e, er, tb = exc_info()
    return er, tb

e,t = _f()

