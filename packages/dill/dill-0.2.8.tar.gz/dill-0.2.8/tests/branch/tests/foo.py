objects = {}
import bar

def load_types(pickleable=True, unpickleable=True):
    import objects as _objects
    if pickleable:
        objects.update(_objects.succeeds)
    else:
        [objects.pop(obj,None) for obj in _objects.succeeds]
    if unpickleable:
        objects.update(_objects.failures)
    else:
        [objects.pop(obj,None) for obj in _objects.failures]
    objects.update(_objects.registered)
    del _objects
    # reset contents of bar to 'empty'
    [bar.__dict__.pop(o) for o in bar.__dict__.keys() if o.find('Type') != -1]
    # add corresponding types from objects to bar
    reload(bar)

