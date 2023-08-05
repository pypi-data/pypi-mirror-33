"""
import dill
import pandas as pd
from pathos.multiprocessing import ProcessingPool
pool = ProcessingPool(nodes=7)
# dfs is list of pandas dataframes  
f = pool.map(some_custom_function, dfs)

# And code generated the following error:
# 
# MaybeEncodingError                        Traceback (most recent call last)
# <ipython-input-9-f340253641ea> in <module>()
"""

import dill
my_string = 'a' * 2**31
dill.dumps(my_string, protocol=dill.HIGHEST_PROTOCOL)

