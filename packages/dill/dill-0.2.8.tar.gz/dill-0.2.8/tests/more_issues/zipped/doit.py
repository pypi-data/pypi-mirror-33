#doit.py
import test
import dill
import os
import shutil
import gzip

env = test.Environment()
print "init add result: ", env.my_vector_add()
pkl_path = "test.pkl"

with open(pkl_path, 'w') as f:
    dill.dump(env, f)

compressed_path = "test.zip"

with open(pkl_path, 'r') as f_in, gzip.open(compressed_path, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)

os.remove(pkl_path)

stored_env = None
with gzip.open(compressed_path, 'r') as f_in:
    stored_env = dill.load(f_in)
    print "loaded add result: ", stored_env.my_vector_add()

