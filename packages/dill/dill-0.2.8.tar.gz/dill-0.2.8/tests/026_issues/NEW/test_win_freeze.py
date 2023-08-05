import dill
#dill.detect.trace(True)

def host(x):
    return x*x

if __name__ == '__main__':
    from pathos.helpers import freeze_support
    freeze_support()

    from pathos.pools import ProcessPool as Pool
    pool = Pool()

    pool.ncpus = 2
    res3 = pool.map(host, range(5))
    print(pool)
    print(res3)
    print('')
