import pathos.multiprocessing as mp
import pathos.profile as pr
import pathos.pools as pp

BUGGY = True

ppool = pp.ProcessPool(1)
mpool = mp.Pool(processes = 2)

def make_dict(i):
    if i == '0':
        dict = { 'a': 1, 'b': 2 }
    else:
        dict = { 'c': 3, 'd': 4 }
    return dict

if BUGGY:
    # use a 'profiled' version of make_dict
    results = [mpool.apply_async(lambda x:x, (pr.profile('cumulative', pipe=ppool.pipe)(make_dict, str(i)),)) for i in (0, 1)]
else:
    # use make_dict directly (no profiling)
    results = [mpool.apply_async(make_dict, args=(str(i),)) for i in (0, 1)]

for i in range(0, 2):
    print(results[i].get())
