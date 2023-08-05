import sympy as sp
import dill
from sympy.physics.mechanics import dynamicsymbols

q = dynamicsymbols('q')
t = sp.symbols('t')
### FIX ###
q.__class__.__module__ = '__main__'
##########
_q = dill.dumps(q)
q_ = dill.loads(_q)
assert q_ == q

