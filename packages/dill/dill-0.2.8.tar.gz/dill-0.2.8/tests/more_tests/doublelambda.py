doit = lambda f: lambda x: f(x)**2

@doit
def squared(x):
  return x

