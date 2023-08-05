import pickle as dill
#import dill
g = (x for x in range(3))
print(g.__reduce_ex__(3))
next(g)
pickled = dill.dumps(g)
dill.loads(pickled)
