funcs = """
def func(x):
    return func_inner(x) + 1

def func_inner(x):
    return x + 1
"""

import multiprocess

if __name__ == "__main__":
    symbols = dict()
    exec(funcs, symbols)
    func = symbols["func"]
    print(func(1))  # this is evaluated correctly as 3 so nesting functions work fine!
    data = [1, 2, 3]
    pool = multiprocess.Pool()
    print(pool.map(func, data))  # this fails with NameError: name 'func_inner' is not defined!

'''
funcs=compile("""
def func(x):
    return func_inner(x) + 1

def func_inner(x):
    return x + 1
""", '<string>', 'exec')

if __name__ == "__main__":
   import multiprocess

   symbols = dict()
   exec(funcs, symbols)
   func = symbols["func"]
   print(func(1))
   data = [1, 2, 3]
   pool = multiprocess.Pool()
   print(pool.map(func, data))
'''

'''
import multiprocess

code_globals = {}
code_locals = {}
exec funcs in code_globals, code_locals
print code_locals
# {'func_inner': <function func_inner at 0x10aa607d0>, 'func': <function func at 0x10a97dde8>}

code_globals['func_inner']=code_locals['func_inner']

print code_globals['func_inner']
#<function func_inner at 0x10a1427d0>

func = code_locals['func']
print(func(1))
data = [1, 2, 3]
pool = multiprocess.Pool()
print(pool.map(func, data))
'''

