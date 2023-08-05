def n(a):
  return a*2

import dill
#dill.settings['recurse'] = True
p = dill.dumps(n)
dill.loads(p)

import pickle
pickle.loads(p)

