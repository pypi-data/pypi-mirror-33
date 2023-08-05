import dill
import doctest

def test_dill():
    """
    >>> out = dill.dumps(lambda x: x)
    """

    out = dill.dumps(lambda x: x)

doctest.testmod()
