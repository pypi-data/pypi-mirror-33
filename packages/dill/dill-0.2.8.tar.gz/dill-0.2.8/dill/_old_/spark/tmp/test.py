from __future__ import with_statement
import dis
from temp import capture

from dill.dill import PY3
from inspect import ismethod, isfunction, istraceback, isframe, iscode
from dill.pointers import parent, reference, at, parents, children

from dill.detect import code as ascode

def nestedglobals(code, shallow=False):
    """get the names of any globals found within func"""
    names = set()
    code = ascode(code)
    if code is None: return names
    with capture('stdout') as out:
        dis.dis(code) #XXX: dis.dis(None) disassembles last traceback
    for line in out.getvalue().splitlines():
        if '_GLOBAL' in line:
            name = line.split('(')[-1].split(')')[0]
            names.add(name)
    for co in getattr(code, 'co_consts', tuple()):
        if co and not shallow and iscode(co):
            names |= nestedglobals(co)
    return names

def referredglobals(func, shallow=True):
    """get the names of objects in the global scope referred to by func"""
    return globalvars(func, shallow).keys()

#NOTE: 'globalvars' is consistent when finding all globalvars in local scope
#      however, what pickling a function needs is *all* global references
#      'nestedglobals' provides a means for only getting the globals used
#      however, does not recurse into global functions (see test_test)
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
            func = nestedglobals(getattr(func, func_code)) #, depth=None)
            # find globals for all entries of func
            for key in func.copy(): #XXX: unnecessary...? bad idea...?
                func.update(globalvars(globs.get(key), shallow=False).keys())
    else:
        return {}
    #NOTE: if name not in func_globals, then we skip it...
    return dict((name,globs[name]) for name in func if name in globs)


