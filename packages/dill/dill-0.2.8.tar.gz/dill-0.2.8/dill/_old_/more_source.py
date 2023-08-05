#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2008-2015 California Institute of Technology.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/dill/blob/master/LICENSE
"""
Extensions to python's 'inspect' module, which can be used
to retrieve information from live python objects. The primary
target of 'dill.source' is to facilitate access to the source
code of interactively defined functions and classes.
"""

__all__ = ['getblocks', 'getsource', '_wrap', 'getname',\
           'getimportable', 'likely_import', '_namespace']

import sys
PYTHON3 = (hex(sys.hexversion) >= '0x30000f0')

def getblocks(object, lstrip=False, enclosing=False):# gettype=False):
    """extract code blocks from a code object using stored history"""
    import inspect
    try:
        code = inspect.findsource(object)[0]
    except (TypeError, IOError):
        # reraise TypeError when is a builtin
        import sys
        if sys.exc_info()[0] is TypeError and type(object) is type(len):
            raise
        # instance also may trigger TypeError, we try to handle instances
        import readline
        lbuf = readline.get_current_history_length()
        code = [readline.get_history_item(i)+'\n' for i in range(1,lbuf)]
    lnum = 0
    codeblocks = []
   #objtypes = []
    dummy = lambda : '__this_is_a_big_dummy_function__'
    try:
        if PYTHON3:
            fname = object.__name__
            ocode = object.__code__
            close = object.__closure__
        else:
            fname = object.func_name
            ocode = object.func_code
            close = object.func_closure
        cname = ''
    except AttributeError:
        fname = ''
        ocode = dummy
        ocode.co_code = '__this_is_a_big_dummy_co_code__'
        close = None #XXX: does not handle classes in a closure
       #try: inspect.getmro(object) #XXX: ensure that it's a class
        if hasattr(object, '__name__'): cname = object.__name__ # class
        else: cname = object.__class__.__name__ # instance
    skip = 0
    while lnum < len(code):#-1:
        #XXX: get all enclosing code, then further lines to reproduce obj ?
        _name = ('def ',)#'class ') #FIXME: decorator classes but not methods
        if enclosing and close and code[lnum].lstrip().startswith(_name):
            #NOTE: decorators will never be seen, code will trace thru them
            if not skip: block = inspect.getblock(code[lnum:])
            _fname = ('def %s' % fname)
            _cname = ('class %s(' % cname, 'class %s:' % cname)
            if fname \
            and any([line.lstrip().startswith(_fname) for line in block]):
                if lstrip:
                    for i in range(skip+1): block[i] = block[i].lstrip()
                codeblocks.append(block)
                lnum += len(block) - skip
            elif cname \
            and any([line.lstrip().startswith(_cname) for line in block]):
                if lstrip:
                    for i in range(skip+1): block[i] = block[i].lstrip()
                codeblocks.append(block)
                lnum += len(block) - skip
            elif fname and 'lambda ' in block:
                for lhs,rhs in (line.split('lambda ',1)[-1].split(":", 1) \
                                for line in block if 'lambda ' in line):
                    try: #FIXME: unsafe
                        _ = eval("lambda %s : %s" % (lhs,rhs), globals(),\
                                                               locals())
                    except: _ = dummy
                    if PYTHON3: _ = _.__code__
                    else: _ = _.func_code
                    if _.co_code == ocode.co_code:
                        if lstrip:
                            for i in range(skip+1): block[i] = block[i].lstrip()
                        codeblocks.append(block)
                        lnum += len(block) - skip
                        break
            else:
                lnum += 1
            skip = 0
        elif not close and code[lnum].lstrip().startswith('@'):
            block = inspect.getblock(code[lnum:])
            skip = 1
            for line in block[1:]: # skip lines that are decorators
                if not line.startswith('@'): break
                skip += 1
            lnum += skip
        # the following can never start with decorators, as it will trace thru
        elif fname and code[lnum].lstrip().startswith('def '):
            # functions and methods
            if not skip: block = inspect.getblock(code[lnum:])
            #else: use existing block
            if block[skip].lstrip().startswith('def %s(' % fname):
                if lstrip:
                    for i in range(skip+1): block[i] = block[i].lstrip()
                codeblocks.append(block)
   #            obtypes.append(types.FunctionType)
                lnum += len(block) - skip
            else: lnum += 1 if close else len(block) - skip
            skip = 0
        elif cname and code[lnum].lstrip().startswith('class '):
            # classes and instances
            block = inspect.getblock(code[lnum:])
            _cname = ('class %s(' % cname, 'class %s:' % cname)
            if block[skip].lstrip().startswith(_cname):
                if lstrip:
                    for i in range(skip+1): block[i] = block[i].lstrip()
                codeblocks.append(block)
                lnum += len(block) - skip
            else: lnum += 1 if close else len(block) - skip
            skip = 0
        elif fname and 'lambda ' in code[lnum]:
            # lambdas
            block = inspect.getblock(code[lnum:])
            lhs,rhs = block[skip].split('lambda ',1)[-1].split(":", 1)
            try: #FIXME: unsafe
                _ = eval("lambda %s : %s" % (lhs,rhs), globals(), locals())
            except: _ = dummy
            if PYTHON3: _ = _.__code__
            else: _ = _.func_code
            if _.co_code == ocode.co_code:
                if lstrip:
                    for i in range(skip+1): block[i] = block[i].lstrip()
                codeblocks.append(block)
   #            obtypes.append('<lambda>')
                lnum += len(block) - skip
            else: lnum += 1 if close else len(block) - skip
            skip = 0
        #XXX: would be nice to grab constructor for instance, but yikes.
        else:
            lnum +=1
            skip = 0
   #if gettype: return codeblocks, objtypes 
    return codeblocks #XXX: danger... gets methods and closures w/o containers

def getsource(object, alias='', lstrip=True, enclosing=False):#XXX:lstrip=False?
    """Extract source code from python code object.

This function is designed to work with simple functions, and will not
work on any general callable. However, this function can extract source
code from functions that are defined interactively.
    """
    import inspect
    _types = ()
    try:
        if PYTHON3:
            ocode = object.__code__
            attr = '__code__'
        else:
            ocode = object.func_code
            attr = 'func_code'
        mname = ocode.co_filename
    except AttributeError:
        try:
            inspect.getmro(object) # ensure it's a class
            mname = inspect.getfile(object)
        except TypeError: # fails b/c class defined in __main__, builtin
            mname = object.__module__
            if mname == '__main__': mname = '<stdin>'
        except AttributeError: # fails b/c it's not a class
            _types = ('<class ',"<type 'instance'>")#,"<type 'module'>")
            if not repr(type(object)).startswith(_types): raise
            mname = getattr(object, '__module__', None)
            if mname == '__main__': mname = '<stdin>'
        attr = '__module__' #XXX: better?
    # no try/except
    if hasattr(object,attr) and mname == '<stdin>':
        # class/function is typed in at the python shell (instance ok)
        lines = getblocks(object, lstrip=lstrip, enclosing=enclosing)[-1]
        #FIXME: '-1' is not always best line... inspect.findsource uses regex
    else:
        try: # get class/functions from file #(instances fail)
            lines = getblocks(object, lstrip=lstrip, enclosing=enclosing)
            if lines: lines = lines[-1] #FIXME: '-1' is not always best line
            else: # we fail to get lines, so try inspect.getsource
                lines = inspect.getsourcelines(object)[0]
                # remove indentation from first line
                #FIXME: no accounting for 'enclosing' or for "@" in lstrip
                if lstrip: lines[0] = lines[0].lstrip()
        except TypeError: # failed to get source, resort to import hooks
            if _types: name = object.__class__.__name__
            else: name = object.__name__
           #module = object.__module__.replace('__builtin__','__builtins__')
            module = object.__module__
            if module in ['__builtin__','__builtins__']:
                lines = ["%s = %s\n" % (name, name)]
            else:
                lines = ["%s = __import__('%s', fromlist=['%s']).%s\n" % (name,module,name,name)]
            if _types: # we now go for the class source
                obj = eval(lines[0].lstrip(name + ' = '))
                lines = inspect.getsourcelines(obj)[0]
                #FIXME: no accounting for 'enclosing' or for "@" in lstrip
                if lstrip: lines[0] = lines[0].lstrip()
    if _types: # instantiate, if there's a nice repr  #XXX: BAD IDEA???
        if '(' in repr(object): lines.append('\n_ = %s\n' % repr(object))
        else: object.__code__ # raise AttributeError
    if alias:
        if attr != '__module__':
            skip = 0
            for line in lines: # skip lines that are decorators
                if not line.startswith('@'): break
                skip += 1
            if lines[skip].lstrip().startswith('def '): # we have a function
                lines.append('\n%s = %s\n' % (alias, object.__name__))
            elif 'lambda ' in lines[skip]: # we have a lambda
                lines[skip] = '%s = %s' % (alias, lines[skip])
            else: # ...try to use the object's name
                lines.append('\n%s = %s\n' % (alias, object.__name__))
        else: # class or class instance
            if _types: lines.append('%s = _\n' % alias)
            else: lines.append('\n%s = %s\n' % (alias, object.__name__))
    return ''.join(lines)

#exec_ = lambda s, *a: eval(compile(s, '<string>', 'exec'), *a)
__globals__ = globals()
__locals__ = locals()
wrap2 = '''
def _wrap(f):
    """ encapsulate a function and it's __import__ """
    def func(*args, **kwds):
        try:
            #_ = eval(getsource(f)) #FIXME: safer, but not as robust
            exec getimportable(f, alias='_') in %s, %s
        except:
            raise ImportError('cannot import name ' + f.__name__)
        return _(*args, **kwds)
    func.__name__ = f.__name__
    func.__doc__ = f.__doc__
    return func
''' % ('__globals__', '__locals__')
wrap3 = '''
def _wrap(f):
    """ encapsulate a function and it's __import__ """
    def func(*args, **kwds):
        try:
            #_ = eval(getsource(f)) #FIXME: safer, but not as robust
            exec(getimportable(f, alias='_'), %s, %s)
        except:
            raise ImportError('cannot import name ' + f.__name__)
        return _(*args, **kwds)
    func.__name__ = f.__name__
    func.__doc__ = f.__doc__
    return func
''' % ('__globals__', '__locals__')
if PYTHON3:
    exec(wrap3)
else:
    exec(wrap2)
del wrap2, wrap3

def getname(obj): #XXX: too simple... pull in logic from getimportable, etc ?
    """ get the name of the object. for lambdas, get the name of the pointer """
    if obj.__name__ == '<lambda>':
        return getsource(obj).split('=',1)[0].strip()
    return obj.__name__

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
        from inspect import getmodule, ismodule
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

def _likely_import(first, last, passive=False, explicit=False):
    """build a likely import string"""
    # we don't need to import from builtins, so return ''
    if last in ['NoneType','int','float','long','complex']: return ''#XXX: more
    if not explicit and first in ['builtins','__builtin__']: return ''
    # get likely import string
    if not first: _str = "import %s\n" % last
    else: _str = "from %s import %s\n" % (first, last)
    # FIXME: breaks on most decorators, currying, and such...
    #        (could look for magic __wrapped__ or __func__ attr)
    if not passive and not first.startswith('dill.'):# weird behavior for dill
       #print(_str)
        try: exec(_str) #XXX: check if == obj? (name collision)
        except ImportError: #XXX: better top-down or bottom-up recursion?
            _first = first.rsplit(".",1)[0] #(or get all, then compare == obj?)
            if not _first: raise
            if _first != first:
                _str = _likely_import(_first, last, passive)
    return _str

def likely_import(obj, passive=False, explicit=False):
    """get the likely import string for the given object

    obj: the object to inspect
    passive: if True, then don't try to verify with an attempted import
    explicit: if True, then also include imports for builtins
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
        if type(obj) is type(abs): _explicit = explicit # BuiltinFunctionType
        else: _explicit = False
        return _likely_import(first, last, passive, _explicit)
    except (ImportError,SyntaxError):
        raise # could do some checking against obj

def _getimportable(obj, alias='', byname=True, explicit=False):
    """attempt to get an importable string that captures the state of obj

For simple objects, this function will discover the name of the object, or the
repr of the object, or the source code for the object. To attempt to force
discovery of the source code, use byname=False. The intent is to build a
string that can be imported from a python file. Use explicit=True if imports
from builtins need to be included.
    """
   #FIXME: fails for decorated functions, when decorator defined in __main__
   #try: # get the module name (to see if it's __main__)
   #    module = str(getmodule(obj)).split()[1].strip('"').strip("'")
   #except: module = ''
    try: _import = likely_import(obj, explicit=explicit)
    except: _import = ""
    # try to get the name (or source)...
    if repr(obj).startswith('<'):
        if not byname:
            try: # try to get the source for lambdas and such
               #print(result)
                return getsource(obj, alias=alias)
            except: pass # AttributeError: pass
        try: # get the name (of functions and classes)
            obj = getname(obj)
        except: 
            obj = repr(obj)
        #FIXME: what to do about class instances and such?
    # hope that it can be built from the __repr__
    else: obj = repr(obj)
    # we either have __repr__ or __name__
    if obj.startswith('<'):
        raise AttributeError("object has no atribute '__name__'")
    elif alias: result = _import+'%s = %s\n' % (alias,obj)
    elif _import.endswith('%s\n' % obj): result = _import
    else: result = _import+'%s\n' % obj
   #print(result)
    return result
    #XXX: possible failsafe...
    #     "import dill; result = dill.loads(<pickled_object>); # repr(<object>)"

def _getclosured(func):
    """get the dict of closured objects: {name:object}"""
    try: #XXX: handles methods correctly? classes? etc?
        if PYTHON3:
            freevars = func.__code__.co_freevars
            closures = func.__closure__
        else:
            freevars = func.func_code.co_freevars
            closures = func.func_closure or ()
    except AttributeError: # then not a function
        return {}
    return dict((name,c.cell_contents) for (name,c) in zip(freevars,closures))

def _getreferred(func):
    """get the dict of objects referred to by func: {name:object}"""
    try: #XXX: handles methods correctly? classes? etc?
        if PYTHON3:
            names = func.__code__.co_names #XXX: what about co_cellvars ?
            globs = func.__globals__
        else:
            names = func.func_code.co_names
            globs = func.func_globals
    except AttributeError: # then not a function
        return {}
    #NOTE: if name not in func_globals, then we skip it...
    return dict((name,globs[name]) for name in names if name in globs)

def getrequired(func):
    """get the dict of objects required by func: {name:object}"""
    required = _getreferred(func)
    required.update(_getclosured(func))
    return required

def _getcode(obj, alias='', byname=False, explicit=True):
    """get source code for importable obj, if possible; otherwise get import"""
    # shortcut for _getimportable (i.e. no enclosing scope)
    return _getimportable(obj, alias=alias, byname=byname, explicit=explicit)

def _getclosurecode(func, *args, **kwds):
    """get source code of closured objects"""
    try: #XXX: handles methods correctly? classes? etc?
        if PYTHON3:
            freevars = func.__code__.co_freevars
            closures = func.__closure__
        else:
            freevars = func.func_code.co_freevars
            closures = func.func_closure or ()
    except AttributeError: # then not a function
        return ''
    if not freevars: return ''
    # _getcode: not recursive; getcode: recursive introspection
    src = (getcode(c.cell_contents, name, *args, **kwds) \
                   for (name,c) in zip(freevars,closures))
    return '\n'.join(src)

def _getreferredcode(func, *args, **kwds):
    """get source code of objects referred to by func"""
    src = _getreferred(func).items()
    if not src: return ''
    # _getcode: not recursive; getcode: recursive introspection
    src = (getcode(value, name, *args, **kwds) for (name,value) in src)
    return '\n'.join(src)

def _getrequiredcode(func, *args, **kwds):
    """get source code of objects required by func"""
    #FIXME: order can be very important, the following is 'randomly ordered'
    ref = _getreferredcode(func, *args, **kwds)
    src = _getclosurecode(func, *args, **kwds)
    if not ref: return src
    if not src: return ref
    return '\n'.join([ref,src])

def getcode(obj, alias='', byname=False, explicit=True, enclosing=True):
    """get source code for importable obj, if possible; otherwise get import"""
    #NOTE: same as getimportable, but shorter and prefers source code
    if not enclosing: ref = ''
    else: ref = _getrequiredcode(obj, byname=byname, explicit=explicit)
    src = _getcode(obj, alias, byname=byname, explicit=explicit)
    if not ref: return src
    if not src: return ref
    return '\n'.join([ref,src])

def getimportable(obj, alias='', byname=True, explicit=False, enclosing=True):
    """attempt to get an importable string that captures the state of obj

For simple objects, this function will discover the name of the object, or the
repr of the object, or the source code for the object. To attempt to force
discovery of the source code, use byname=False. The intent is to build a
string that can be imported from a python file. Use explicit=True if imports
from builtins need to be included.
    """
    #XXX: enable code 'byname=True' and enclosing 'byname=False' ?
    return getcode(obj, alias, byname=byname, \
                   explicit=explicit, enclosing=enclosing)


# backward compatability
_get_name = getname
getblocks_from_history = getblocks

del sys


# EOF
