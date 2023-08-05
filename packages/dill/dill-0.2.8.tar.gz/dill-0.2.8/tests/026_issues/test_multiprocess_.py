from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from multiprocessing import Pool

class CustomError3(Exception):
    def __init__(self):
        msg = 'Something went wrong.'
        Exception.__init__(self, msg)

def callback(_):
    return CustomError3()

def test_5():
    """Test returning an extension that passes an additional argument to standard Exception."""

    error = CustomError3()
    assert isinstance(error, Exception)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3

pool = Pool(1)
