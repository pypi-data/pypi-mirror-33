""" DELETE __reduce__ due to from_address?

dude@borel>$ grep "from_address" py*/multiprocess/managers.py
py2.6/multiprocess/managers.py:        return type(self).from_address, \
py2.7/multiprocess/managers.py:        return type(self).from_address, \
py3.1/multiprocess/managers.py:        return type(self).from_address, \
py3.2/multiprocess/managers.py:        return type(self).from_address, \
pypy/multiprocess/managers.py:        return type(self).from_address, \
"""
