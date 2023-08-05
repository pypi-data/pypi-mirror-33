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
