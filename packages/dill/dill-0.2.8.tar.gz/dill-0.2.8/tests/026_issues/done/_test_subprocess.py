from pathos.pools import ProcessPool, ParallelPool, SerialPool, ThreadPool
#NOTE: moved `subprocess` import into `run_call`

def run_call(i):
    from subprocess import Popen, PIPE
    p = Popen('echo hello', stdout=PIPE, stderr=PIPE, shell=True)
    out,err = p.communicate()
    p.wait()
    return out

def run():
    p=ParallelPool(1)
    res = p.map(run_call, range(1))
    p.close()
    p.join()
    print(res)


if __name__ == '__main__':
    run()
