import pathos
p = pathos.pools.ParallelPool()
f = lambda i: i*2
print p.map(f, range(4))
# [0, 2, 4, 6]
f = lambda i: i**2
print p.map(f, range(4))
# [0, 1, 4, 9]
print p.map(lambda i:i, range(4))
# [0, 2, 4, 6] # NOTE: WRONG
# NOTE: if inline lambda is used first, a NameError is thrown
p.close()
p.clear()
