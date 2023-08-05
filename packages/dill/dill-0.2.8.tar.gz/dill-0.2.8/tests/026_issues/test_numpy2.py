import dill
from sympy import Symbol, lambdify
x = Symbol("x")
H = lambdify(x, x, "numpy")
dill.dump_session()

# dump_session has 'recurse' mode hard-wired to be False
