import dill
import sys
PY3 = (sys.hexversion >= 0x30000f0)
if PY3:
    import builtins
else:
    import __builtin__ as builtins
import re

def exec_copy(original_object):
    try:
        key = dill.source.getname(original_object, force=True)
        if re.match("[_A-Za-z][_a-zA-Z0-9]*$", key) is None:
            key = "dummy_key_qawedsfrtgvhuijiokopllmkoijniuhvgygftrdreswq"
    except AttributeError:
        key = "dummy_key_qawedsfrtgvhuijiokopllmkoijniuhvgygftrdreswq"
    dummy_dic = {'__builtins__': builtins}
    dict.__setitem__(dummy_dic, key, original_object)
    exec("__builtins__.{0} = {0}".format(key), dummy_dic)
    x = dill.dumps(original_object)
    y = dill.loads(x)
    exec("del __builtins__.{0}".format(key), dummy_dic)
    return y


local_env = {}
global_env = {}
x = "def test(x, y):\n  return x + y\n"
exec(x, global_env, local_env)

x = "class doit(object):\n  pass\n"
exec(x, global_env, local_env)

# dill.dumps(local_env['test'])
# dill.dumps(local_env['doit'])

print(exec_copy(local_env['test']))
print(exec_copy(local_env['doit']))

