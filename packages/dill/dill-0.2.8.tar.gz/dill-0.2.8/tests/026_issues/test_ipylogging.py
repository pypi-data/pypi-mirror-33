class foo:
   def __init__(self):
       self.logger = logging.getLogger("package.foo")

import dill
import logging

f = foo()
_f = dill.dumps(f)  
f_ = dill.loads(_f)
print('success')
