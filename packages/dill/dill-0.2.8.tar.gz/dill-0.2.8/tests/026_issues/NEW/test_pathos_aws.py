'''
apparently fails on AWS
'''

import requests as req
from pathos.multiprocessing import Pool
from multiprocessing import cpu_count

class MigrationEngine():

    def start_process(self):
        pool = Pool(processes=2 if cpu_count() < 2 else cpu_count())
        r1 = pool.apply_async(
            self.testApi, ('http://google.com',))
        d1 = r1.get()
        print d1
        pool.close()
        pool.join()

    def testApi(self, q):
        r = req.get(q)
        print r.status_code
        cont = r.content
        return cont

if __name__ == '__main__':
    me = MigrationEngine()
    me.start_process()
