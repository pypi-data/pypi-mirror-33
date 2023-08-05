import dis

from dill.dill import PY3
from inspect import ismethod, isfunction, istraceback, isframe, iscode
from dill.pointers import parent, reference, at, parents, children

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO


def to_int(x):
    if not isinstance(x, int):
        return ord(x)
    return x

def find_globals(co):
    globs = set()
    code = co.co_code
    n = len(code)
    i = 0
    extended_arg = 0
    while i < n:
        op = to_int(code[i])
        i = i+1
        if op >= dis.HAVE_ARGUMENT:
            oparg = to_int(code[i]) + to_int(code[i+1]) * 256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == dis.EXTENDED_ARG:
                extended_arg = oparg * 65536
            if op in dis.hasname and dis.opname[op].endswith("_GLOBAL"):
                globs.add(co.co_names[oparg])
    return globs

def globalvars(func, shallow=True):
    """get objects defined in global scope that are referred to by func

    return a dict of {name:object}"""
    if PY3:
        im_func = '__func__'
        func_code = '__code__'
        func_globals = '__globals__'
    else:
        im_func = 'im_func'
        func_code = 'func_code'
        func_globals = 'func_globals'
    if ismethod(func): func = getattr(func, im_func)
    if isfunction(func):
        globs = getattr(func, func_globals) or {}
        if shallow: #XXX: depth = 0  (faster)
            func = getattr(func, func_code).co_names # get names
        else: #XXX: depth >= 1 (slower)
            func = find_globals(getattr(func, func_code)) #, depth=None)
    else:
        return {}
    #NOTE: if name not in func_globals, then we skip it...
    return dict((name,globs[name]) for name in func if name in globs)


