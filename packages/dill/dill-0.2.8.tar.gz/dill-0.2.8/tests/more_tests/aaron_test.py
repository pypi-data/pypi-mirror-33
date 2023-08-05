class _sentinel:
  pass

import dill

class Test:
  def __new__(cls, name):
    if name == _sentinel:
      obj = object.__new__(cls)
    else:
      obj = type(name.capitalize() + cls.__name__, (cls,), {})(_sentinel)
    obj.name = name
    return obj
  def __getnewargs__(self):
    return (self.name,)

t = Test("Aaron")
dill.detect.errors(t)
# RuntimeError('uninitialized staticmethod object',)
_t = dill.dumps(t, byref=True)
# print (_t)
#b'\x80\x03cdill.dill\n_create_type\nq\x00(cdill.dill\n_load_type\nq\x01X\x04\x00\x00\x00typeq\x02\x85q\x03Rq\x04X\t\x00\x00\x00AaronTestq\x05h\x00(h\x04X\x04\x00\x00\x00Testq\x06h\x01X\x06\x00\x00\x00objectq\x07\x85q\x08Rq\t\x85q\n}q\x0b(X\x07\x00\x00\x00__new__q\x0ch\x01X\x0c\x00\x00\x00staticmethodq\r\x85q\x0eRq\x0f)\x81q\x10X\n\x00\x00\x00__module__q\x11X\x08\x00\x00\x00__main__q\x12X\x07\x00\x00\x00__doc__q\x13Nutq\x14Rq\x15\x85q\x16}q\x17(h\x13NX\r\x00\x00\x00__slotnames__q\x18]q\x19h\x11h\x12utq\x1aRq\x1b)\x81q\x1c}q\x1dX\x04\x00\x00\x00nameq\x1eX\x05\x00\x00\x00Aaronq\x1fsb.'
pt = dill.loads(_t)
'''
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/mmckerns/lib/python3.3/site-packages/dill/dill.py", line 135, in loads
    return load(file)
  File "/Users/mmckerns/lib/python3.3/site-packages/dill/dill.py", line 128, in load
    obj = pik.load()
  File "/opt/local/Library/Frameworks/Python.framework/Versions/3.3/lib/python3.3/pickle.py", line 840, in load
    dispatch[key[0]](self)
  File "/opt/local/Library/Frameworks/Python.framework/Versions/3.3/lib/python3.3/pickle.py", line 1085, in load_newobj
    obj = cls.__new__(cls, *args)
RuntimeError: uninitialized staticmethod object
'''
