import copy_reg
import pickle

class A(object):
  def f(self):
    pass
  @classmethod
  def g(cls):
    pass

def f(self):
  pass

ClassMethodDescriptorType = type(A.g)
BuiltinFunctionType = type(len)
FunctionType = type(f)
MethodType = type(A().f)
MethodDescriptorType = type(list.append)
WrapperDescriptorType = type(list.__add__)
MethodWrapperType = type([].__add__)

obj_list = [A.g, len, f, A().f, list.append, list.__add__, [].__add__]

assert ClassMethodDescriptorType is MethodType
  
def reduce_self(self):
  return getattr, (self.__self__, self.__name__)

def reduce_objclass(self):
  return getattr, (self.__objclass__, self.__name__)

copy_reg.pickle(MethodType, reduce_self)
copy_reg.pickle(BuiltinFunctionType, reduce_self)
copy_reg.pickle(MethodWrapperType, reduce_self)
copy_reg.pickle(MethodDescriptorType, reduce_objclass)
copy_reg.pickle(WrapperDescriptorType, reduce_objclass)

for obj in obj_list:
  try:
    data = pickle.dumps(obj)
    new_obj = pickle.loads(data)
    print('%s\n%s\n' % (obj,new_obj))
  except:
    print('FAILED: %s\n' % (obj,))

# EOF
