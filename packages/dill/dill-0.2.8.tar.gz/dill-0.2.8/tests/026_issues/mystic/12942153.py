'''
I am trying to find the optimal solution to the follow system of equations in Python:

(x-x1)^2 + (y-y1)^2 - r1^2 = 0
(x-x2)^2 + (y-y2)^2 - r2^2 = 0
(x-x3)^2 + (y-y3)^2 - r3^2 = 0
Given the values a point(x,y) and a radius (r):

x1, y1, r1 = (0, 0, 0.88)
x2, y2, r2 = (2, 0, 1)
x3, y3, r3 = (0, 2, 0.75)
What is the best way to find the optimal solution for the point (x,y) Using the above example it would be:
~ (1, 1)
'''

'''
from mystic import reduced

@reduced(lambda x,y: abs(x)+abs(y)) #choice changes answer
def objective(x, a, b, c):
  x,y = x
  eqns = (\
    (x - a[0])**2 + (y - b[0])**2 - c[0]**2,
    (x - a[1])**2 + (y - b[1])**2 - c[1]**2,
    (x - a[2])**2 + (y - b[2])**2 - c[2]**2)
  return eqns

bounds = [(None,None),(None,None)] #unnecessary

a = (0,2,0)
b = (0,0,2)
c = (.88,1,.75)
args = a,b,c

from mystic.solvers import diffev2
from mystic.monitors import VerboseMonitor
mon = VerboseMonitor(10)

result = diffev2(objective, args=args, x0=bounds, bounds=bounds, npop=40,     ftol=1e-8, disp=False, full_output=True, itermon=mon)

print result[0]
print result[1]
'''

#'''
def objective(x):
    return 0.0

equations = """
(x0 - 0)**2 + (x1 - 0)**2 - .88**2 == 0
(x0 - 2)**2 + (x1 - 0)**2 - 1**2 == 0
(x0 - 0)**2 + (x1 - 2)**2 - .75**2 == 0
"""

bounds = [(None,None),(None,None)] #unnecessary

from mystic.symbolic import generate_constraint, generate_solvers, simplify
from mystic.symbolic import generate_penalty, generate_conditions

cf = generate_constraint(generate_solvers(simplify(equations)))
pf = generate_penalty(generate_conditions(equations), k=1e12)

from mystic.solvers import diffev2

result = diffev2(objective, x0=bounds, bounds=bounds, \
                #constraints=cf, \
                 penalty=pf, \
                 npop=40, gtol=50, disp=False, full_output=True)

print result[0]
print result[1]
#'''


