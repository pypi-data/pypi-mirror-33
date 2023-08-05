import dill

class A(object):
  @classmethod
  def test(cls):
    pass


a = A()

res = dill.dumps(a)
new_obj = dill.loads(res)

new_obj.__class__.test()
