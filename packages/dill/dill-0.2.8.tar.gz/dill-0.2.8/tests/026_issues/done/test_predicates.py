"""
Greetings from the still-frigid Great White North (i.e., Canada). Upfront apologies for polluting your issue tracker with yet another frivolous feature request: in this case, global attribute filtering.
What U Want?

Our downstream application would love to avoid pickling any object attributes whose attribute names match a user-defined predicate – regardless of the types of those objects. Sadly, neither the underlying pickle nor higher-level dill APIs appear to be extensible in this way. Both permit callers to define custom reduction functions uniquely applicable to specific types but appear to have no means of defining custom reduction functions globally applicable to all types.
Why U Want This?

A bit of context might be useful. Like most obese large-scale Python projects, ours internally defines a @property_cached decorator for efficiently caching property return values into object attributes. The names of these attributes are all prefixed by the magic substring __property_cached_.

Efficiency is fun, so this works. Except under pickling.

These attributes tend to be quite large in worst-case scenarios – like several gigabytes too large. Since these attributes are all safely recomputable at runtime, we'd rather not pickle them if we don't have to. Since any arbitrary object of any arbitrary type may contain methods decorated by @property_cached, attempting to exclude these attributes from pickling by defining custom reduction functions specific to particular types fails to scale.

A general-purpose strategy is needed.
Why U No Do This the Easy Way?

"It'll be easy!", I initially said. It wasn't easy. After several hours of futile grepping through the pickle and dill codebases, I'm no closer to a sane solution. At this point, I'll happily accept an insane solution.

The only one on hand appears to be:

    Define a new application specific SmartPickleableMixin class implementing the __getstate__() special method to omit all object attributes prefixed by the magic substring __property_cached_.
    Refactor all existing application classes to additionally subclass the SmartPickleableMixin class.

This is pretty insane for any number of obvious reasons, the least of which is that implementing this change across a codebase exceeding 100,000 lines of raw, brutal, no-holds-barred scientific Python will probably require two human lifetimes. Moreover, it's manual and hence fragile – really, really fragile.

Humans are imperfect meat bags. Any class that I or other project contributors accidentally neglect to subclass from SmartPickleableMixin will continue to silently pickle cached properties – which is bad.

The younger me might try monkey-patching that __getstate__() implementation into the root object type, transparently enabling this functionality across the entire codebase. The older me merely squints suspiciously and refuses to do anything.

Hence, this modest request for a global attribute filtering solution applicable to all types. Maybe this already exists? My grep-fu isn't what it was.
"""

# This should filter out all attributes beginning with __property_cached_.
import dill

class CustomPickler(dill.Pickler):
    def save(self, obj, *args, **kwargs):
        # Filter out cached attrs
        tmp_rm = {}
        if hasattr(obj, "__dict__"):
            for key in list(obj.__dict__):
                if type(key) is str and key.startswith("__property_cached_"):
                    tmp_rm[key] = obj.__dict__.pop(key)
        # Pickle obj
        super().save(obj, *args, **kwargs)
        # Restore cached attrs
        for key, value in tmp_rm.items():
            obj.__dict__[key] = value

dill.dill.Pickler = CustomPickler

# Testing

from functools import wraps

def property_cached(property_method):
    func_body = '''
@wraps(__property_method)
def property_method_cached(self, __property_method=__property_method):
    try:
        return self.{property_name}
    except AttributeError:
        self.{property_name} = __property_method(self)
        return self.{property_name}
'''.format(property_name='__property_cached_' + property_method.__name__)
    local_attrs = {'__property_method': property_method}
    exec(func_body, globals(), local_attrs)
    return property(local_attrs['property_method_cached'])


class A:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    @property_cached
    def magic(self):
        return "a" * 10000

a=A(1, None, set())
assert a.magic == "a" * 10000
assert a.magic == "a" * 10000

raw = dill.dumps(a)
assert len(raw) < 10000

assert a.__property_cached_magic == "a" * 10000

clone = dill.loads(raw)
assert clone.x == 1
assert clone.y is None
assert clone.z == set()
assert clone.magic == "a" * 10000

