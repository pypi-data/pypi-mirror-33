"""
I'm trying to call a function which uses a numpy function in its body, with Pool.map and Pool.map_async, however each time, I get an error saying 'name "numpy" is not defined. I then had a look at the Python 3.5 examples, which use the time module in the body of a function, but this also fails for me. The following are the lines of code I'm executing line by line in Spyder->IPython on Windows 7 x64:
"""

from multiprocess import Pool, TimeoutError
from multiprocess import cpu_count as cpuCount, current_process as currentProcess, freeze_support as freezeSupport, active_children as activeChildren

def calculate(func, args):
    result = func(*args)
    return '%s says that %s%s = %s' % \
        (currentProcess()._name, func.__name__, args, result)

def mul(a, b):
    import time, random
    time.sleep(0.5*random.random())
    return a * b

pool = Pool(4)
TASKS = [(mul, (i, 7)) for i in range(10)]
results = [pool.apply_async(calculate, t) for t in TASKS]

for r in results:
    print('\t', r.get())

"""
That last for loop gives me an error: NameError: name 'time' is not defined

I'm guessing this is because the function mul uses time.sleep, however, the time module is not being loaded in the child pseudo-fork process on Windows. However, this code is straight from the multiprocess github examples, so I'm not sure why this isn't working for me.

Could anyone please help me out? How can you use a function in Pool which uses external modules like time or numpy in that function's body?
"""
