import sys
import contextlib

from dill.dill import PY3

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO


@contextlib.contextmanager
def capture(stream='stdout'):  #XXX: goes in dill.temp ?
    '''builds a context that temporarily replaces the given stream name'''
    orig = getattr(sys, stream)
    setattr(sys, stream, StringIO())
    try:
        yield getattr(sys, stream)
    finally:
        setattr(sys, stream, orig)

del contextlib
