from klepto import inf_cache as memoized
from klepto.archives import *
from klepto.keymaps import *

import numpy as np
data = np.arange(3)

arxiv = dir_archive('memo1',serialized=True,cached=True)
pik = picklemap(serializer='dill')
memo1 = memoized(cache=arxiv,keymap=pik)

@memo1
def testme1(x):
  return x

print(testme1(data))
print(testme1(data))

testme1.dump()

# THROWS  ValueError: I/O operation on closed file
print(testme1(data))
