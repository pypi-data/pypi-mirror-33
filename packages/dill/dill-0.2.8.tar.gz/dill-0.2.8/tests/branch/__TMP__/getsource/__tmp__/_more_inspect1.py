from _inspect import _importable, _getimport
from _inspect import *
from dill.detect import *
from inspect import ismethod, isfunction, istraceback, isframe, iscode
from inspect import getmodule


#def getrequired(func):
#    """get the dict of objects required by func: {name:object}"""
#    required = globalvars(func)
#    required.update(freevars(func))
#    return required

# def _getclosurecode(func, *args, **kwds):
#     """get source code of closured objects"""
#     func = freevars(func)
#     if not func: return ''
#     # _importable: not recursive; getcode: recursive introspection
#     func = (getcode(obj, name, *args, **kwds) for (name,obj) in func.items())
#     return '\n'.join(func)

def _getclosuredimport(func):
    '''get import for closured objects'''
    import re
    free_vars = freevars(func)
    func_vars = {}
    # split into 'funcs' and 'non-funcs'
    for name,obj in list(free_vars.items()): 
        if not isfunction(obj): continue
        # get import for 'funcs'
        fobj = free_vars.pop(name)
        src = getsource(fobj)
        if src.lstrip().startswith('@'): # we have a decorator
            src = getimport(fobj)
        else: # we have to "hack" a bit... and maybe be lucky
            encl = outermost(func)
            # pattern: 'func = enclosing(fobj'
            pat = '.*[\w\s]=\s*'+getname(encl)+'\('+getname(fobj)
            mod = getname(getmodule(encl))
            #HACK: get file containing 'outer' function; is func there?
            lines,_ = findsource(encl)
            candidate = [line for line in lines if getname(encl) in line and \
                         re.match(pat, line)]
            if not candidate:
                mod = getname(getmodule(fobj))
                #HACK: get file containing 'inner' function; is func there? 
                lines,_ = findsource(fobj)
                candidate = [line for line in lines \
                             if getname(fobj) in line and re.match(pat, line)]
            if not len(candidate): raise TypeError('import could not be found')
            candidate = candidate[-1]
            name = candidate.split('=',1)[0].split()[-1].strip()
            src = _getimport(mod, name)
        func_vars[name] = src
    if not func_vars:
        name = outermost(func)
        mod = getname(getmodule(name))
        lines,_ = findsource(name)
        # pattern: 'func = enclosing('
        candidate = [line for line in lines if getname(name) in line and \
                     re.match('.*[\w\s]=\s*'+getname(name)+'\(', line)]
        if not len(candidate): raise TypeError('import could not be found')
        candidate = candidate[-1]
        name = candidate.split('=',1)[0].split()[-1].strip()
        src = _getimport(mod, name)
        func_vars[name] = src
    return func_vars
        

#XXX: should be able to use __qualname__
def _getclosuredsource(func):
    '''get source code for closured objects'''
    free_vars = freevars(func)
    func_vars = {}
    # split into 'funcs' and 'non-funcs'
    for name,obj in list(free_vars.items()): 
        if not isfunction(obj):
            # get source for 'non-funcs'
            free_vars[name] = getsource(obj, force=True, alias=name)
            continue
        # get source for 'funcs'
        fobj = free_vars.pop(name)
        src = getsource(fobj)
        # if source doesn't start with '@', use an alias
        if not src.lstrip().startswith('@'): #FIXME: 'enclose' in dummy;
            src = getsource(fobj, alias=name)#        wrong ref 'name'
            org = getsource(func, enclosing=False, lstrip=True)
            src = (src, org) # undecorated first, then target
        else: #NOTE: reproduces the code!
            org = getsource(func, enclosing=True, lstrip=False)
            src = (org, src) # target first, then decorated
        func_vars[name] = src
    if not func_vars: #FIXME: 'enclose' in dummy; wrong ref 'name'
        src = ''.join(free_vars.values())
        org = getsource(func, force=True, enclosing=False, lstrip=True)
        src = (src, org) # variables first, then target
        func_vars[None] = src
    return func_vars

#FIXME: needs alias, enclosing (and maybe: force, builtin, lstrip)
#FIXME: sometimes has an additional leading '\n' or unnecessary '\n' in middle
def getimportable(func, source=True): #, alias='', enclosing=False):
    '''get an importable string, including any required objects from the 
    enclosing and global scope'''
    if not source: # we want an import
        src = _getclosuredimport(func)
        if len(src) == 0:
            raise NotImplementedError('not implemented')
        if len(src) > 1:
            raise NotImplementedError('not implemented')
        return src.values()[0]
    # we want the source
    src = _getclosuredsource(func)
    if len(src) == 0:
        raise NotImplementedError('not implemented')
    if len(src) > 1:
        raise NotImplementedError('not implemented')
    src = '\n'.join(src.values()[0])
    # get source code of objects referred to by func in global scope
    func = globalvars(func)
    func = (getsource(obj, name) for (name,obj) in func.items())
    func = '\n'.join(func)
    # combine all referred-to source (global then enclosing)
    if not func: return src
    if not src: return func
    return func + src

# def getreferredcode(func):
#     """get source code of objects referred to by func"""
#     func = globalvars(func)
#     func = (getsource(obj, name) for (name,obj) in func.items())
#     return '\n'.join(func)

# def _getreferredcode(func, *args, **kwds):
#     """get source code of objects referred to by func"""
#     func = globalvars(func)
#     if not func: return ''
#     # _importable: not recursive; getcode: recursive introspection
#     func = (getcode(obj, name, *args, **kwds) for (name,obj) in func.items())
#     return '\n'.join(func)

# def _getrequiredcode(func, *args, **kwds):
#     """get source code of objects required by func"""
#     #FIXME: order can be very important, the following is 'randomly ordered'
#     ref = _getreferredcode(func, *args, **kwds)
#     src = getclosuredsource(func)
#     if not ref: return src
#     if not src: return ref
#     return '\n'.join([ref,src])

# def getcode(obj, alias='', builtin=True, enclosing=True, **kwds):
#     """get source code for importable obj, if possible; otherwise get import"""
#     source = kwds.get('source', True) #XXX: remove ability to set source=False ?
#     return getimportable(obj, alias=alias, builtin=builtin, \
#                          enclosing=enclosing, source=source)

#NOTE: broke backward compatibility 4/17/14 (was byname=True, explicit=False)
# def getimportable(obj, alias='', builtin=False, enclosing=True, **kwds):
#     """attempt to get an importable string that captures the state of obj
# 
# For simple objects, this function will discover the name of the object, or the
# repr of the object, or the source code for the object. To attempt to force
# discovery of the source code, use source=True. The intent is to build a
# string that can be imported from a python file. Use builtin=True if imports
# from builtins need to be included.
#     """
#     #XXX: enable code 'source=False' and enclosing 'source=True' ?
#     source = kwds.get('source', False)
#     if not enclosing: ref = ''
#     else: ref = _getrequiredcode(obj, source=source, builtin=builtin)
#     src = _importable(obj, alias, source=source, builtin=builtin)
#     if not ref: return src
#     if not src: return ref
#     return '\n'.join([ref,src])


# EOF
