import pathos

def foo(x):
    return x

def bar(x):
    return foo(x)

if __name__ == '__main__':
    pathos.helpers.freeze_support()
    pool = pathos.multiprocessing.Pool(processes=2)
    print(pool.map(bar, [0, 1]))

"""
NameError: global name 'foo' is not defined
"""

import pickle
import dill
import multiprocessing
import functools

def foo(x):
    return x

def bar(x):
    return foo(x)

def undill_run(dill_func, arg):
    return dill.loads(dill_func)(arg)

if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=2)
    print(pool.map(functools.partial(undill_run, dill.dumps(bar)), [0, 1]))

"""
NameError: global name 'foo' is not defined
"""
