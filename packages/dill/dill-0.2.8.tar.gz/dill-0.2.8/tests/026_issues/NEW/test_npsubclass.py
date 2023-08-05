import numpy as np

import dill
#dill.settings['recurse'] = True
dill.detect.trace(True)


class RealisticInfoArray(np.ndarray):

    def __new__(cls, input_array, info=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.info = info
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.info = getattr(obj, 'info', None)


class MyContainer:

    def __init__(self, things):

        self.things = things


my_things = RealisticInfoArray([1, 2, 3], info='a')

#"""
my_box = MyContainer(my_things)

new_box = dill.loads(dill.dumps(my_box))

print(my_box.things.info)
print(new_box.things.info)
"""
new_things = dill.loads(dill.dumps(my_things))

print(my_things.info)
print(new_things.info)
"""

