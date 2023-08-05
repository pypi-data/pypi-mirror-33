# instance fails to use pickled class when class already exists in __main__
"""
In [1]: import dill

In [2]: class Foo(object):
   ...:     def bar(self, x):
   ...:         return x+self.y
   ...:     y = 1
   ...: 

In [3]: f = Foo()

In [4]: _Foo = dill.dumps(Foo)

In [5]: _f = dill.dumps(f)

In [6]: del Foo, f

In [7]: class Foo(object):
   ...:     def bar(self, x):
   ...:         return x+self.z
   ...:     z = -1
   ...: 

In [8]: f_ = dill.loads(_f)

In [9]: f_.__class__ == Foo
Out[9]: True

In [10]: f_.y
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
<ipython-input-10-c57fc71c226a> in <module>()
----> 1 f_.y

AttributeError: 'Foo' object has no attribute 'y'

In [11]: _f
Out[11]: b'\x80\x03cdill.dill\n_create_type\nq\x00(cdill.dill\n_load_type\nq\x01X\x04\x00\x00\x00typeq\x02\x85q\x03Rq\x04X\x03\x00\x00\x00Fooq\x05h\x01X\x06\x00\x00\x00objectq\x06\x85q\x07Rq\x08\x85q\t}q\n(X\n\x00\x00\x00__module__q\x0bX\x08\x00\x00\x00__main__q\x0cX\x03\x00\x00\x00barq\rcdill.dill\n_create_function\nq\x0e(h\x01X\x08\x00\x00\x00CodeTypeq\x0f\x85q\x10Rq\x11(K\x02K\x00K\x02K\x02KCC\n|\x01|\x00j\x00\x17\x00S\x00q\x12N\x85q\x13X\x01\x00\x00\x00yq\x14\x85q\x15X\x04\x00\x00\x00selfq\x16X\x01\x00\x00\x00xq\x17\x86q\x18X\x1e\x00\x00\x00<ipython-input-2-8e4875db3fbc>q\x19h\rK\x02C\x02\x00\x01q\x1a))tq\x1bRq\x1cc__builtin__\n__main__\nh\rNN}q\x1dtq\x1eRq\x1fh\x14K\x01X\x07\x00\x00\x00__doc__q NX\r\x00\x00\x00__slotnames__q!]q"utq#Rq$)\x81q%.'

In [12]: f_.z
Out[12]: -1

In [13]: del Foo

In [14]: f_.y
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
<ipython-input-14-c57fc71c226a> in <module>()
----> 1 f_.y

AttributeError: 'Foo' object has no attribute 'y'

In [15]: f_ = dill.loads(_f)

In [16]: f_.y
Out[16]: 1
"""
