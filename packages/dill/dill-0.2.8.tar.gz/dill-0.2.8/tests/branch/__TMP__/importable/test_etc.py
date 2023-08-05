# itself
assert likely_import(likely_import) == 'from dill.source import likely_import'

# builtin functions and objects
assert likely_import(pow) == ''
assert likely_import(100) == ''
assert likely_import(True) == ''
# this is kinda BS... you can't import a None
assert likely_import(None) == ''

# other imported functions
from math import sin
assert likely_import(sin) == 'from math import sin'

# interactively defined functions
assert likely_import(add) == 'from %s import add' % __name__

# interactive lambdas
assert likely_import(squared) == 'from %s import squared' % __name__

# classes and class instances
try: #XXX: should this be a 'special case'?
    from StringIO import StringIO
    x = "from StringIO import StringIO"
    y = x
except ImportError:
    from io import BytesIO as StringIO
    x = "from io import BytesIO"
    y = "from _io import BytesIO"
s = StringIO()
assert likely_import(StringIO) == x
assert likely_import(s) == y

# interactively defined classes and class instances
assert likely_import(Foo) == 'from %s import Foo' % __name__
assert likely_import(f) == 'from %s import Foo' % __name__


# EOF
