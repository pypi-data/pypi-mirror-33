# this is the file that does the extending?

#from xxx import extend as __extend
#__extend()
#del __extend

import sys
#if 'xxx.doit' in sys.modules:
#  print 'doit @doit'
#if 'xxx.dont' in sys.modules:
#  print 'dont @doit'

# trigger print in __init__
reload(sys.modules['xxx'])
del sys


# EOF
