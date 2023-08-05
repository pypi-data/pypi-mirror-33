#! /usr/bin/python
import multiprocess
import multiprocessing
import dill
# dill.settings['byref'] = True     # this 'works'
# dill.settings['recurse'] = True   # no effect

"""
pass: 3.3, 3.4, 3.5, 3.6
fail: 2.7, 3.1, 3.2
error: 2.6
"""

class Drive(object):
    def __init__(self, osa):
        self.os_address = osa

def gather_os_addresses():
    drive_list = []
    drive_list.append(Drive("/dev/sda"))
   #drive_list.append(Drive("/dev/sdb"))
   #drive_list.append(Drive("/dev/sdc"))
    return drive_list

def test_pool(pool):
   #p = pool.apply_async(gather_os_addresses)
    drive_list = pool.apply(gather_os_addresses)
    bail = False
    while not bail:
        bail = True    
   #    if not p.ready():
   #        bail = False
        #End if the pool process isn't ready yet
    #End wait for processes to complete loop
    pool.close()
   #drive_list = p.get()
    for d in drive_list:
        print("d is type {}, isinstace(d, Drive) is {}".format(type(d), isinstance(d, Drive)))

pool = multiprocessing.Pool(5)
print("Using MultiprocessING:")
test_pool(pool)
print("")
print("Using Multiprocess:")
pool = multiprocess.Pool(5)
test_pool(pool)


"""
Using MultiprocessING:
d is type <class '__main__.Drive'>, isinstace(d, Drive) is True
d is type <class '__main__.Drive'>, isinstace(d, Drive) is True
d is type <class '__main__.Drive'>, isinstace(d, Drive) is True

Using Multiprocess:
d is type <class '__main__.Drive'>, isinstace(d, Drive) is False
d is type <class '__main__.Drive'>, isinstace(d, Drive) is False
d is type <class '__main__.Drive'>, isinstace(d, Drive) is False

Further details, when using python 2.7.10, the output is like above. However with python 3.6.2 it works as expected
"""
