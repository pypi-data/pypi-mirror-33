"""
import multiprocessing as mp
print(mp.Pool())

import multiprocess as mp
print(mp.Pool())
import pathos as pa
print(pa.pools._ProcessPool())
print(pa.multiprocessing.Pool())

print(pa.pools.ProcessPool())
print(pa.pools.ParallelPool())

f = lambda x:x
p = pa.pools.ParallelPool()
print(p.map(f, [1,2,3]))
p.close()
p.join()
p.restart()
print(p.map(f, [1,2,3]))
p.close()
p.join()
p.clear()

"""

import multiprocessing as mp
from pathos.multiprocessing import Pool as Pool1
from pathos.pools import ParallelPool as Pool2
from pathos.parallel import ParallelPool as Pool3
import time

def square(x):  
    # calculate the square of the value of x
    return x*x

if __name__ == '__main__':

    dataset = range(0,10000)

    start_time = time.time()
    for d in dataset:
        square(d)
    print('test with no cores: %s seconds' %(time.time() - start_time))

    nCores = 3
    print('number of cores used: %s' %(nCores))  


    start_time = time.time()

    p = mp.Pool(nCores)
    p.map(square, dataset)

    # Close
    p.close()
    p.join()

    print('test with multiprocessing: %s seconds' %(time.time() - start_time))
    print(p)


    start_time = time.time()

    p = Pool1(nCores)
    p.map(square, dataset)

    # Close
    p.close()
    p.join()

    print('test with pathos multiprocessing: %s seconds' %(time.time() - start_time))
    print(p)


    start_time = time.time()

    p = Pool2(nCores)
    p.map(square, dataset)

    # Close
    p.close()
    p.join()

    print('test with pathos pools: %s seconds' %(time.time() - start_time))
    print(p)
    p.restart()


    start_time = time.time()

    p = Pool3()
    p.ncpus = nCores
    p.map(square, dataset)

    # Close
    p.close()
    p.join()

    print('test with pathos parallel: %s seconds' %(time.time() - start_time))
    print(p)
"""
