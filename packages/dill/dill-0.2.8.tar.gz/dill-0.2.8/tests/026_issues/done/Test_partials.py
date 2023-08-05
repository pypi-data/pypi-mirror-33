import dill
from functools import partial
from dill.dill import PY3, OLDER


class Machine(object):
    def __init__(self):
        self.go = partial(self.member, self)
    def member(self, model):
        pass


class SubMachine(Machine):
    def __init__(self):
        super(SubMachine, self).__init__()


def test_partials():
    assert dill.copy(SubMachine(), byref=True)
    assert dill.copy(SubMachine(), byref=True, recurse=True)
    if not OLDER:
        assert dill.copy(SubMachine(), recurse=True)
    assert dill.copy(SubMachine())



if __name__ == '__main__':
    test_partials()

