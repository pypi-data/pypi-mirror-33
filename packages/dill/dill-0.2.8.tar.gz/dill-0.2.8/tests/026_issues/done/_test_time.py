# NOTE: moved imports into `A`

class A(object):
    def __init__(self, njobs=15):#1000):
        import time
        from pathos.pools import ProcessPool as Pool
        self.map = Pool().map
        self.njobs = njobs
        print(time.time())
        self.start()
    def start(self):
        self.result = self.map(self.RunProcess, range(self.njobs))
        return self.result
    def RunProcess(self, i):
        import time
        time.sleep(.1)
        return i*i

if __name__ == '__main__': 
    myA = A()
    print(myA.result[:11])
    myA.njobs = 3
    myA.start()
