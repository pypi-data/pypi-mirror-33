from pickle import *
#from pickle import PicklingError
#from pickle import loads, dumps

def copy(obj):
    """use pickling to 'copy' an object"""
    return loads(dumps(obj))

# quick sanity checking
def pickles(obj,exact=False):
    """quick check if object pickles with pickle"""
    try:
        pik = copy(obj)
        if exact:
            return pik == obj
        return type(pik) == type(obj)
    except (TypeError, PicklingError):
        return False

