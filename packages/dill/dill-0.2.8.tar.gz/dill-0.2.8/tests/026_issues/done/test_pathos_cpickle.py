import random
import dill
# dill.detect.trace(True)
from pathos.pools import ProcessPool as Pool


def process(item):
    return item.power()


class A(object):
    def __init__(self, num):
        super(A, self).__init__()
        self.num = num

    def power(self):
        self.num = self.num ** 2
        return self.num


pool = Pool(3)
items = [A(random.uniform(1,10)) for x in range(1,3)]

results = pool.map(process, items)
print(results)

