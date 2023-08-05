#!/usr/bin/env python3
#
from pathos.parallel import stats
from pathos.parallel import ParallelPool as Pool
import time

pool = Pool()

def host(id ):
    print("my info message")
    return 'jedna,dva,tri'
pool.ncpus = 1  # when nodes replaced by 1
totalchunks=1
res5 = pool.amap( host, range(totalchunks)  )
while not res5.ready():
         time.sleep(1)
         print(stats()  )
pool.close()
pool.join()
print( "=========Printout:")
aaa=res5.get()
csvheader="chunk,host,result\n"
csv=csvheader+"\n".join(res5.get()) 
print( '\n==REAL PRINT==\n',csv)

'''
I realized - when there is a print() inside the function called by amap(),
only the last result is retrieved from res5.get()
'''

