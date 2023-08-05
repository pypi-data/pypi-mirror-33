from pathos import multiprocessing, pools as pp
import time


class Multiprocess(object):

    def __init__(self):
        pass

    def qmp_worker(self,(inputs, the_time)):
        print " Processs %s\tWaiting %s seconds" % (inputs, the_time)
        time.sleep(int(the_time))
        print " Process %s\tDONE" % inputs

    def qmp_handler(self):                      # Non tandem pair processing
        pool = pp.ProcessPool(2)
        pool.map(self.qmp_worker, data)


def mp_worker((inputs, the_time)):
    print " Processs %s\tWaiting %s seconds" % (inputs, the_time)
    time.sleep(int(the_time))
    print " Process %s\tDONE" % inputs

def mp_handler():                           # Non tandem pair processing
    p = multiprocessing.Pool(2)
    p.map(mp_worker, data)

def mp_handler_tandem():
    subdata = zip(data[0::2], data[1::2])
    print subdata
    for task1, task2 in subdata:
        p = multiprocessing.Pool(2)
        p.map(mp_worker, (task1, task2))


#data = (['a', '1'], ['b', '2'], ['c', '3'], ['d', '4'])
data = (['a', '2'], ['b', '3'], ['c', '1'], ['d', '4'], ['e', '1'], ['f', '2'], ['g', '3'], ['h', '4'])

if __name__ == '__main__':
    mp_handler()
    mp_handler_tandem()

    Multiprocess().qmp_handler()
