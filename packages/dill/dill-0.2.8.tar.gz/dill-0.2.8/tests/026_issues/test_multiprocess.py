from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from multiprocess import Pool


def skip(func):
    def wrapper(*args, **kwargs):
        raise SkipTest("Test %s is skipped" % func.__name__)
    wrapper.__name__ = func.__name__
    return wrapper


def test_1():
    """Test returning a standard Exception."""

    error = Exception()
    assert isinstance(error, Exception)

    def callback(_):
        return Exception()

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError1(Exception):
    pass


def test_2():
    """Test returning a minimal extention of the standard Exception."""

    error = CustomError1()
    assert isinstance(error, Exception)

    def callback(_):
        return CustomError1()

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError2(Exception):
    def __init__(self):
        Exception.__init__(self)


def test_3():
    """Test returning an extention of the standard Exception with a custom init."""

    error = CustomError2()
    assert isinstance(error, Exception)

    def callback(_):
        return CustomError2()

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


def test_4():
    """Test returning an extention with improper arguments raises."""

    def callback(msg):
        return CustomError2(msg)

    with assert_raises(TypeError):
        error = CustomError2('A')

    with assert_raises(TypeError):
        results = pool.map(callback, ['A', 'B', 'C'])


class CustomError3(Exception):
    def __init__(self):
        msg = 'Something went wrong.'
        Exception.__init__(self, msg)


@skip
def test_5():
    """Test returning an extention that passes an additional argument to standard Exception."""

    def callback(_):
        return CustomError3()

    error = CustomError3()
    assert isinstance(error, Exception)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


def test_6():
    """Test returning an extention that passes an additional argument to standard Exception that is rewrapped."""

    def callback(_):
        error = CustomError3()
        return RuntimeError(*error.args)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError4(Exception):
    def __init__(self, item):
        msg = 'Something went wrong with {}.'.format(item)
        Exception.__init__(self, msg)


def test_7():
    """Test returning an extention with an additional argument that passes that argument to standard Exception."""

    def callback(item):
        return CustomError4(item)

    error = CustomError4('A')
    assert isinstance(error, Exception)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError5(Exception):
    def __init__(self, item=None):
        msg = 'Something went wrong with {}.'.format(item or 'something')
        Exception.__init__(self, msg)


def test_8():
    """Test returning an extention with an additional default argument that passes that argument to standard Exception."""

    def callback(item):
        return CustomError5()

    error = CustomError5()
    assert isinstance(error, Exception)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError6(Exception):
    def __init__(self, item):
        msg = 'Something went wrong with {}.'.format(item)
        Exception.__init__(self, msg, 500)


@skip
def test_9():
    """Test returning an extention with an additional argument that passes that argument and another to standard Exception."""

    def callback(item):
        return CustomError6(item)

    error = CustomError6('A')
    assert isinstance(error, Exception)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


def test_10():
    """Test returning an extention with an additional argument that passes that argument and another to standard Exception that is rewrapped."""

    def callback(item):
        error = CustomError6(item)
        return RuntimeError(*error.args)

    results = pool.map(callback, ['A', 'B', 'C'])
    assert len(results) == 3


class CustomError7(Exception):
    def __init__(self, item, error_code):
        msg = 'Something went wrong with {}.'.format(item)
        Exception.__init__(self, msg, error_code)


def test_11():
    """Test returning an extention with additional arguments that passes those arguments to standard Exception."""

    def callback(pair):
        item, error_code = pair
        return CustomError7(item, error_code)

    error = CustomError7('A', 403)
    assert isinstance(error, Exception)

    results = pool.map(callback, [('A', 403), ('B', 404), ('C', 500)])
    assert len(results) == 3


pool = Pool(1)