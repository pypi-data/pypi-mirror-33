from inspect import getmodule, ismodule
from dill.source import getname, getsource

def _namespace(obj):
    """_namespace(obj); return namespace hierarchy (as a list of names)
    for the given object.

    For example:

    >>> from functools import partial
    >>> p = partial(int, base=2)
    >>> _namespace(p)
    [\'functools\', \'partial\']
    """
    # mostly for functions and modules and such
    try: #FIXME: this function needs some work and testing on different types
        qual = str(getmodule(obj)).split()[1].strip('"').strip("'")
        qual = qual.split('.')
        if ismodule(obj):
            return qual
        try: # special case: get the name of a lambda
            name = getname(obj)
        except: #XXX: fails to get name
            name = obj.__name__
        return qual + [name] #XXX: can be wrong for some aliased objects
    except: pass
    # special case: numpy.inf and numpy.nan (we don't want them as floats)
    if str(obj) in ['inf','nan','Inf','NaN']: # is more, but are they needed?
        return ['numpy'] + [str(obj)]
    # mostly for classes and class instances and such
    module = getattr(obj.__class__, '__module__', None)
    qual = str(obj.__class__)
    try: qual = qual[qual.index("'")+1:-2]
    except ValueError: pass # str(obj.__class__) made the 'try' unnecessary
    qual = qual.split(".")
    if module in ['builtins', '__builtin__']:
        qual = [module] + qual
    return qual

def _likely_import(first, last, passive=False):
    """build a likely import string"""
    # we don't need to import from builtins, so return ''
    if first in ['builtins','__builtin__']: return ''
    # get likely import string
    if not first: _str = "import %s\n" % last
    else: _str = "from %s import %s\n" % (first, last)
    # FIXME: breaks on most decorators, currying, and such...
    #        (could look for magic __wrapped__ or __func__ attr)
    if not passive:
       #print(_str)
        try: exec(_str) #XXX: check if == obj? (name collision)
        except ImportError: #XXX: better top-down or bottom-up recursion?
            _first = first.rsplit(".",1)[0] #(or get all, then compare == obj?)
            if not _first: raise
            if _first != first:
                _str = _likely_import(_first, last, passive)
    return _str

def likely_import(obj, passive=False):
    """get the likely import string for the given object

    obj: the object to inspect
    passive: if True, then don't try to verify with an attempted import
    """
    # for named things... with a nice repr #XXX: move into _namespace?
    if not repr(obj).startswith('<'): name = repr(obj).split('(')[0]
    else: name = None
    # get the namespace
    qual = _namespace(obj)
    first = '.'.join(qual[:-1])
    last = qual[-1]
    if name: # try using name instead of last
        try: return _likely_import(first, name, passive)
        except (ImportError,SyntaxError): pass
    try:
        return _likely_import(first, last, passive)
    except (ImportError,SyntaxError):
        raise # could do some checking against obj


def getimportable(obj, alias='', byname=True):
    """attempt to get an importable string that captures the state of obj

For simple objects, this function will discover the name of the object, or the
repr of the object, or the source code for the object.  To attempt to force
discovery of the source code, use byname=False.  The intent is to build a
string that can be imported.
    """
   #try: # get the module name (to see if it's __main__)
   #    module = str(getmodule(obj)).split()[1].strip('"').strip("'")
   #except: module = ''
    try: _import = likely_import(obj)
    except: _import = ""
    # try to get the name...
    memo = None
    if repr(obj).startswith('<'):
        try: # get the name (of functions and classes)
            if byname:
                _obj = getname(obj)
            else:
                _obj = obj.__name__
                if _obj.startswith('<'): raise # probably a lambda
                if '__main__' in _import: # we *choose* to use getsource
                    raise # and don't import from __main__
            obj = _obj
        except:
            try: # try to get the source for lambdas and such
                memo = getsource(obj, alias=alias)
            except AttributeError: pass
        #FIXME: what to do about class instances and such?
    # hope that it can be built from the __repr__
    else: obj = repr(obj)
    # if we got the source, just use it
    if memo: pass
    # otherwise, try from __repr__ or __name__
    elif repr(obj).startswith('<'): #XXX: seems weird for class w byname=False
        raise AttributeError("object has no atribute '__name__'")
    elif alias: memo = _import+'%s = %s\n' % (alias,obj)
    elif _import.endswith('%s\n' % obj): memo = _import
    else: memo = _import+'%s\n' % obj
   #print(memo)
    return memo
    #XXX: possible failsafe...
    #     "import dill; memo = dill.loads(<pickled_object>); # repr(<object>)"



# EOF
