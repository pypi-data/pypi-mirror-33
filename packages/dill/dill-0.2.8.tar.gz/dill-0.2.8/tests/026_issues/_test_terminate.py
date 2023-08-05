'''
after a dill.copy, a termination condition has it's __doc__ set to None. This is not good, as the __doc__ is used to get the state of the termination condition (for collapse, etc).
'''
'''
>>> import mystic.termination as mt      
>>> stop = mt.ChangeOverGeneration()
>>> stop.__doc__
"ChangeOverGeneration with {'tolerance': 1e-06, 'generations': 30}"
>>> import dill
>>> _stop = dill.copy(stop)
>>> _stop.__doc__
'''
