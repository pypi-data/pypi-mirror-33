import pathos
print pathos.__version__
# 0.2.0
from pathos.pp_map import pp_map
f = lambda i: i*2
print pp_map(f, [1, 2, 3, 4, 6, 7, 8])
