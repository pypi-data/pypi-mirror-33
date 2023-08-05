def doit(x):
    import readline
    return x

import dill
dill.source.importable(doit)

import pathos
pool = pathos.pools.ParallelPool(2)
res = pool.imap(doit, range(2))
list(res)


# EOF
