import dill as pickle
from functools import partial
#pickle.detect.trace(True)


def get_trigger(model):
    pass


class Machine(object):

    def __init__(self):
        self.child = Model()
        # raises RuntimeError
        self.trigger = partial(get_trigger, self)
        # does not work either
        self.child.trigger = partial(get_trigger, self.child)


class Model(object):
    pass

m = Machine()
dump = pickle.dumps(m)
