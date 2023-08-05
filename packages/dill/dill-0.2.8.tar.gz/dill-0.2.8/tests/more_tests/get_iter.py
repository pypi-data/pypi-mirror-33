### BusError in python2.5... use python2.7
import ctypes

ctypes.pythonapi.PyCallIter_New.restype = ctypes.py_object
ctypes.pythonapi.PyCallIter_New.argtypes = [ctypes.py_object, ctypes.py_object]
def PyCallIter_New(callable, sentinel):
    """build a callable-iterator... iter(callable, sentinel)"""
    # a = 0
    # def incr_a():
    #     global a
    #     a += 1
    #     return a
    # it = iter(incr_a, 4)
    # list(it)
    # a = 0
    return ctypes.pythonapi.PyCallIter_New(callable, sentinel)

ctypes.pythonapi.PySeqIter_New.restype = ctypes.py_object
ctypes.pythonapi.PySeqIter_New.argtypes = [ctypes.py_object]
def PySeqIter_New(sequence):
    """build an iterator... same as iter(sequence)"""
    # it = iter([1,2,3])
    # list(it)
    return ctypes.pythonapi.PySeqIter_New(sequence)

def PyIter_GetBuiltin():#_iter=True):
    "get a reference to 'iter'... same as id(iter)"
    _iter = True
    if _iter: _iter='iter'
    else: _iter = 'reversed'
    mod = ctypes.pythonapi.PyImport_ImportModule('__builtin__')
    _iter = ctypes.pythonapi.PyObject_GetAttrString(mod, _iter)
    return _iter  #XXX: return reference or <object>?

# NOTES:
# i = iter([1,2,3])
# it = PySeqIter_New([1,2,3])
# i.__class__  # <type 'listiterator'>
# it.__class__ # <type 'iterator'>



# EOF
