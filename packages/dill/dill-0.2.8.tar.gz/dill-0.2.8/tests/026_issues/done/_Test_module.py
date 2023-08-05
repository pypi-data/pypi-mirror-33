'''
At dill.py:1367, this new line breaks things for us:
if not IS_PYPY: pickler.clear_memo()

Comment it out and everything is okay
'''

'''
  File "/home/stultsd/py/lib/python3.6/site-packages/dill-0.2.8.dev0-py3.6.egg/dill/dill.py", line 297, in loads
    return load(file)
  File "/home/stultsd/py/lib/python3.6/site-packages/dill-0.2.8.dev0-py3.6.egg/dill/dill.py", line 286, in load
    obj = pik.load()
  File "/home/stultsd/py/lib/python3.6/site-packages/dill-0.2.8.dev0-py3.6.egg/dill/dill.py", line 444, in find_class
    return StockUnpickler.find_class(self, module, name)
ModuleNotFoundError: No module named 'CodeType'
'''


from osbrain import run_nameserver
from osbrain import run_agent


def set_method():
    """
    Set new methods for the agent.
    """
    def one(agent):
        return 1

    def two(agent):
        return 2

    ns = run_nameserver()

    a0 = run_agent('a0')

    a0.set_method(one, two)
    assert a0.one() == 1
    assert a0.two() == 2

    ns.shutdown()


if __name__ == '__main__':
    set_method()

'''
Traceback (most recent call last):
  File "dillbug.py", line 43, in <module>
    set_method()
  File "dillbug.py", line 21, in set_method
    a0.set_method(one, two)
  File "/cache/miniconda/envs/dillbug/lib/python3.6/site-packages/Pyro4/core.py", line 186, in __call__
    return self.__send(self.__name, args, kwargs)
  File "/cache/src/osbrain/osbrain/proxy.py", line 159, in _pyroInvoke
    methodname, args, kwargs, flags, objectId)
  File "/cache/src/osbrain/osbrain/proxy.py", line 204, in _remote_call
    flags=flags, objectId=objectId)
  File "/cache/miniconda/envs/dillbug/lib/python3.6/site-packages/Pyro4/core.py", line 470, in _pyroInvoke
    raise data
ModuleNotFoundError: No module named 'obj_72beac03721e4240af1fcc431c5af57d'
'''

'''
Note that it will fail only when calling .set_method() with two parameters. If I call .set_method(one) or .set_method(two), it will work just fine.

Bisecting the problem, Git tells me the error was introduced in (don't apply super workaround in pypy), which might coincide with what @davidstults is mentioning.
'''
