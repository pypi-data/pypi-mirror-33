'''
Nested solvers can be built by either replacing f(x) with solve(f(x)), or more generically, do Step then an (inner) Solve (replacing the last values in the monitors, as necessary).
'''

'''
ensemble solvers should have Step available as a method, and to do so will probably need to be refactored to use serialization or reduce.
'''
