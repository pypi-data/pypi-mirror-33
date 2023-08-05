# this is the stub to *not* pull the trigger

import sys
#if 'xxx.doit' in sys.modules:
#  print 'doit @dont'
#if 'xxx.dont' in sys.modules:
#  print 'dont @dont'

# trigger print in __init__
reload(sys.modules['xxx'])
del sys


# EOF
