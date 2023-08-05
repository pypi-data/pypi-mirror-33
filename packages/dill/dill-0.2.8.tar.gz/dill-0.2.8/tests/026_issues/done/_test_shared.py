# NOTE: shared memory is accessbible from multiprocess

>>> from pathos.helpers import mp as multiprocess
>>> a = multiprocess.Array('i', 2)
>>> a[:] = 1,2
>>> a
<SynchronizedArray wrapper for <multiprocess.sharedctypes.c_int_Array_2 object at 0x10e6cacb0>>
>>> 
