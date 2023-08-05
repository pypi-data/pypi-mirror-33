import unittest
import multiprocessing as mp
#import multiprocess as mp

#
# Test to verify catching all exceptions in Pool workers, see issue 8296
#

def raise_exc(x):
    raise x

class TestPoolWorkersExceptions(unittest.TestCase):
    def test_map_keyboard_interrupt(self):
        p = mp.Pool(2)
        self.assertRaises(KeyboardInterrupt,
                          p.map,
                          raise_exc,
                          [KeyboardInterrupt()])
        p.close()
        p.join()

