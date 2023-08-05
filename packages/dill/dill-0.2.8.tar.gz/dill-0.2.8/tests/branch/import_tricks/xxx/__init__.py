# this is the __init__ file

from xxx import do_thing, do_more
from other import do_other
extend = False

import sys
if 'xxx.doit' in sys.modules:
  #print 'doit @__init__'
  extend = True
if 'xxx.dont' in sys.modules:
  #print 'dont @__init__'
  extend = False
del sys

if extend:
  from xxx import extend as __extend
  __extend()
  del __extend


# EOF
