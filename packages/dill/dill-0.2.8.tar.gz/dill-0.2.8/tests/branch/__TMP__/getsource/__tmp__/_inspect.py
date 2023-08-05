#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2008-2015 California Institute of Technology.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/dill/blob/master/LICENSE
#
# inspired by inspect.py from Python-2.7.6
# inspect.py author: 'Ka-Ping Yee <ping@lfw.org>'
# inspect.py merged into original dill.source by Mike McKerns 4/13/14
"""
Extensions to python's 'inspect' module, which can be used
to retrieve information from live python objects. The methods
defined in this module are augmented to facilitate access to 
source code of interactively defined functions and classes,
as well as provide access to source code for objects defined
in a file.
"""

__all__ = ['findsource', 'getsourcelines', 'getsource', 'indent', 'outdent', \
           '_wrap', 'dumpsource', 'getname', '_namespace', 'getimport']

import sys
PYTHON3 = (hex(sys.hexversion) >= '0x30000f0')

import re
import linecache
from tokenize import TokenError
from inspect import ismodule, isclass, ismethod, isfunction, istraceback
from inspect import isframe, iscode, getfile, getmodule, getsourcefile
from inspect import getblock, indentsize, isbuiltin


def findsource(object):
    """Return the entire source file and starting line number for an object.
    For interactively-defined objects, the 'file' is the interpreter's history.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of all the lines
    in the file and the line number indexes a line in that list.  An IOError
    is raised if the source code cannot be retrieved, while a TypeError is
    raised for objects where the source code is unavailable (e.g. builtins)."""

    module = getmodule(object)
    if module and module.__name__ == '__main__':
        import readline
        lbuf = readline.get_current_history_length()
        lines = [readline.get_history_item(i)+'\n' for i in range(1,lbuf)]
    else:
        try: # special handling for class instances
            if not isclass(object) and isclass(object.__class__):
                file = getfile(getmodule(object))        
                sourcefile = getsourcefile(getmodule(object))
            else: # builtins fail with a TypeError
                file = getfile(object)
                sourcefile = getsourcefile(object)
        except (TypeError, AttributeError): # fail with better error
            file = getfile(object)
            sourcefile = getsourcefile(object)
        if not sourcefile and file[:1] + file[-1:] != '<>':
            raise IOError('source code not available')
        file = sourcefile if sourcefile else file

        module = getmodule(object, file)
        if module:
            lines = linecache.getlines(file, module.__dict__)
        else:
            lines = linecache.getlines(file)

    if not lines:
        raise IOError('could not get source code')

    #FIXME: all below may fail if exec/eval used (i.e. exec('f = lambda x:x') )
    if ismodule(object):
        return lines, 0

    name = ''
    pat = ''
    if ismethod(object):
        name = object.__name__
        if name == '<lambda>': pat = r'(.*(?<!\w)lambda(:|\s))'
        else: pat = r'^(\s*def\s)'
        if PYTHON3: object = object.__func__
        else: object = object.im_func
    if isfunction(object):
        name = object.__name__
        if name == '<lambda>': pat = r'(.*(?<!\w)lambda(:|\s))'
        else: pat = r'^(\s*def\s)'
        if PYTHON3: object = object.__code__
        else: object = object.func_code
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        if not hasattr(object, 'co_firstlineno'):
            raise IOError('could not find function definition')
        if object.co_filename == '<stdin>':
            lnum = len(lines) - 1 # can't get lnum easily, so leverage pat
            if not pat: pat = r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)'
        else:
            lnum = object.co_firstlineno - 1
            pat = r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)'
        pat = re.compile(pat)
        dummy = lambda : '__this_is_a_big_dummy_function__'
        while lnum > 0: #XXX: won't find decorators in <stdin> ?
            line = lines[lnum]
            if pat.match(line):
                if name == '<lambda>': # hackery needed to confirm a match
                    lhs,rhs = line.split('lambda ',1)[-1].split(":", 1)
                    try: #FIXME: unsafe
                        _ = eval("lambda %s : %s" % (lhs,rhs), globals(),\
                                                               locals())
                    except: _ = dummy 
                    if PYTHON3: _ = _.__code__
                    else: _ = _.func_code
                    if _.co_code == object.co_code: break
                else: # not a lambda, just look for the name
                    if name in line: break
            lnum = lnum - 1
        return lines, lnum

    try: # turn instances into classes
        if not isclass(object) and isclass(object.__class__):
            object = object.__class__
            #XXX: we don't find how the instance was built
    except AttributeError: pass
    if isclass(object):
        name = object.__name__
        pat = re.compile(r'^(\s*)class\s*' + name + r'\b')
        # make some effort to find the best matching class definition:
        # use the one with the least indentation, which is the one
        # that's most probably not inside a function definition.
        candidates = []
        for i in range(len(lines)-1,-1,-1):
            match = pat.match(lines[i])
            if match:
                # if it's at toplevel, it's already the best one
                if lines[i][0] == 'c':
                    return lines, i
                # else add whitespace to candidate list
                candidates.append((match.group(1), i))
        if candidates:
            # this will sort by whitespace, and by line number,
            # less whitespace first  #XXX: should sort high lnum before low
            candidates.sort()
            return lines, candidates[0][1]
        else:
            raise IOError('could not find class definition')
    raise IOError('could not find code object')


def getblocks(object, lstrip=False, enclosing=False, locate=False):
    """Return a list of source lines and starting line number for an object.
    Interactively-defined objects refer to lines in the interpreter's history.

    DEPRECATED: use getsourcelines instead
    """
    lines, lnum = findsource(object)

    if ismodule(object):
        if lstrip: lines = _outdent(lines)
        return ([lines], [0]) if locate is True else [lines]

    #XXX: 'enclosing' means: closures only? or classes and files?
    indent = indentsize(lines[lnum])
    block = getblock(lines[lnum:]) #XXX: catch any TokenError here?

    if not enclosing or not indent:
        if lstrip: block = _outdent(block)
        return ([block], [lnum]) if locate is True else [block]

    pat1 = r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))'; pat1 = re.compile(pat1)
    pat2 = r'^(\s*@)'; pat2 = re.compile(pat2)
   #pat3 = r'^(\s*class\s)'; pat3 = re.compile(pat3) #XXX: enclosing class?
    #FIXME: bound methods need enclosing class (and then instantiation)
    #       *or* somehow apply a partial using the instance

    skip = 0
    line = 0
    blocks = []; _lnum = []
    target = ''.join(block)
    while line <= lnum: #XXX: repeat lnum? or until line < lnum?
        # see if starts with ('def','lambda') and contains our target block
        if pat1.match(lines[line]):
            if not skip:
                try: code = getblock(lines[line:])
                except TokenError: code = [lines[line]]
            if indentsize(lines[line]) > indent: #XXX: should be >= ?
                line += len(code) - skip
            elif target in ''.join(code):
                blocks.append(code) # save code block as the potential winner
                _lnum.append(line - skip) # save the line number for the match
                line += len(code) - skip
            else:
                line += 1
            skip = 0
        # find skip: the number of consecutive decorators
        elif pat2.match(lines[line]):
            try: code = getblock(lines[line:])
            except TokenError: code = [lines[line]]
            skip = 1
            for _line in code[1:]: # skip lines that are decorators
                if not pat2.match(_line): break
                skip += 1
            line += skip
        # no match: reset skip and go to the next line
        else:
            line +=1
            skip = 0

    if not blocks:
        blocks = [block]
        _lnum = [lnum]
    if lstrip: blocks = [_outdent(block) for block in blocks]
    # return last match
    return (blocks, _lnum) if locate is True else blocks


def getsourcelines(object, lstrip=False, enclosing=False):
    """Return a list of source lines and starting line number for an object.
    Interactively-defined objects refer to lines in the interpreter's history.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of the lines
    corresponding to the object and the line number indicates where in the
    original source file the first line of code was found.  An IOError is
    raised if the source code cannot be retrieved, while a TypeError is
    raised for objects where the source code is unavailable (e.g. builtins).
    If lstrip=True, ensure there is no indentation in the first line of code.
    If enclosing=True, then also return any enclosing code."""
    code, n = getblocks(object, lstrip=lstrip, enclosing=enclosing, locate=True)
    return code[-1], n[-1]


#NOTE: broke backward compatibility 4/16/14 (was lstrip=True, force=True)
def getsource(object, alias='', lstrip=False, enclosing=False, force=False):
    """Return the text of the source code for an object. The source code for
    interactively-defined objects are extracted from the interpreter's history.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a single string.  An
    IOError is raised if the source code cannot be retrieved, while a
    TypeError is raised for objects where the source code is unavailable
    (e.g. builtins).

    If enclosing=True, then also return any enclosing code.
    If force=True, catch (TypeError,IOError) and try to use import hooks.
    If lstrip=True, ensure there is no indentation in the first line of code.
    If alias is provided, then add a line of code that renames the object.
    """
    # hascode denotes a callable
    hascode = _hascode(object)
    # is a class instance type (and not in builtins)
    instance = _isinstance(object)

    # get source lines; if fail, try to 'force' an import
    try: # fails for builtins, and other assorted object types
        lines, lnum = getsourcelines(object, enclosing=enclosing)
    except (TypeError, IOError): # failed to get source, resort to import hooks
        if not force: # don't try to get types that findsource can't get
            raise
        if not getmodule(object): # get things like 'None' and '1'
            name = repr(object)
            lines, lnum = ["%s\n" % name], 0
        else:
            if instance: name = object.__class__.__name__
            else: name = object.__name__

            if ismodule(object):
                lines, lnum = ["%s = __import__('%s')\n" % (name,name)], 0
            else:
                module = object.__module__
                if module in ['builtins','__builtin__']:
                    # handle 'special cases' (types.NoneType)
                    if _intypes(name): #XXX: BuiltinFunctionType
                        if name == 'ellipsis': name = 'EllipsisType'
                        lines, lnum = ["%s = __import__('%s', fromlist=['%s']).%s\n" % (name,'types',name,name)], 0
                    else:
                        lines, lnum = ["%s = %s\n" % (name, name)], 0
                else:
                    lines, lnum = ["%s = __import__('%s', fromlist=['%s']).%s\n" % (name,module,name,name)], 0
        if instance: # we now go for the class source
            obj = eval(lines[0].lstrip(name + ' = '))
            lines, lnum = getsourcelines(obj, enclosing=enclosing)

    # strip leading indent (helps ensure can be imported)
    if lstrip or alias:
        lines = _outdent(lines)

    # instantiate, if there's a nice repr  #XXX: BAD IDEA???
    if instance: #and force: #XXX: move into findsource or getsourcelines ?
        if '(' in repr(object): lines.append('%r\n' % object)
       #else: #XXX: better to somehow to leverage __reduce__ ?
       #    reconstructor,args = object.__reduce__()
       #    _ = reconstructor(*args)
        else: # fall back to serialization #XXX: bad idea?
            #XXX: better not duplicate work? #XXX: better new/enclose=True?
            lines = dumpsource(object, alias='', new=force, enclose=False)
            lines, lnum = [line+'\n' for line in lines.split('\n')][:-1], 0
       #else: object.__code__ # raise AttributeError

    # add an alias to the source code
    if alias:
        if hascode:
            skip = 0
            for line in lines: # skip lines that are decorators
                if not line.startswith('@'): break
                skip += 1
            #XXX: use regex from findsource / getsourcelines ?
            if lines[skip].lstrip().startswith('def '): # we have a function
                lines.append('\n%s = %s\n' % (alias, object.__name__))
            elif 'lambda ' in lines[skip]: # we have a lambda
                lines[skip] = '%s = %s' % (alias, lines[skip])
            else: # ...try to use the object's name
                lines.append('\n%s = %s\n' % (alias, object.__name__))
        else: # class or class instance
            if instance: lines[-1] = ('%s = ' % alias) + lines[-1]
            elif not getmodule(object): # things like 'None' and '1'
                lines.append('\n%s = %s\n' % (alias, repr(object)))
            else: lines.append('\n%s = %s\n' % (alias, object.__name__))
    return ''.join(lines)


def _hascode(object):
    '''True if object has an attribute that stores it's __code__'''
    return getattr(object,'__code__',None) or getattr(object,'func_code',None)

def _isinstance(object):
    '''True if object is a class instance type (and is not a builtin)'''
    if _hascode(object) or isclass(object) or ismodule(object):
        return False
    if istraceback(object) or isframe(object) or iscode(object):
        return False
    _types = ('<class ',"<type 'instance'>")
    if not repr(type(object)).startswith(_types):
        return False
    if not getmodule(object) or object.__module__ in ['builtins','__builtin__']:
        return False
    return True # by process of elimination... it's what we want


def _intypes(object):
    '''check if object is in the 'types' module'''
    import types
    # allow user to pass in object or object.__name__
    if type(object) is not type(''):
        object = getname(object, force=True)
    if object == 'ellipsis': object = 'EllipsisType'
    return True if hasattr(types, object) else False


def _isstring(object): #XXX: isstringlike better?
    '''check if object is a string-like type'''
    if PYTHON3: return isinstance(object, (str, bytes))
    return isinstance(object, basestring)


def indent(code, spaces=4):
    '''indent a block of code with whitespace (default is 4 spaces)'''
    indent = indentsize(code) 
    if type(spaces) is int: spaces = ' '*spaces
    # if '\t' is provided, will indent with a tab
    nspaces = indentsize(spaces)
    # blank lines (etc) need to be ignored
    lines = code.split('\n')
##  stq = "'''"; dtq = '"""'
##  in_stq = in_dtq = False
    for i in range(len(lines)):
        #FIXME: works... but shouldn't indent 2nd+ lines of multiline doc
        _indent = indentsize(lines[i])
        if indent > _indent: continue
        lines[i] = spaces+lines[i]
##      #FIXME: may fail when stq and dtq in same line (depends on ordering)
##      nstq, ndtq = lines[i].count(stq), lines[i].count(dtq)
##      if not in_dtq and not in_stq:
##          lines[i] = spaces+lines[i] # we indent
##          # entering a comment block
##          if nstq%2: in_stq = not in_stq
##          if ndtq%2: in_dtq = not in_dtq
##      # leaving a comment block
##      elif in_dtq and ndtq%2: in_dtq = not in_dtq
##      elif in_stq and nstq%2: in_stq = not in_stq
##      else: pass
    if lines[-1].strip() == '': lines[-1] = ''
    return '\n'.join(lines)


def _outdent(lines, spaces=None, all=True):
    '''outdent lines of code, accounting for docs and line continuations'''
    indent = indentsize(lines[0]) 
    if spaces is None or spaces > indent or spaces < 0: spaces = indent
    for i in range(len(lines) if all else 1):
        #FIXME: works... but shouldn't outdent 2nd+ lines of multiline doc
        _indent = indentsize(lines[i])
        if spaces > _indent: _spaces = _indent
        else: _spaces = spaces
        lines[i] = lines[i][_spaces:]
    return lines

def outdent(code, spaces=None, all=True):
    '''outdent a block of code (default is to strip all leading whitespace)'''
    indent = indentsize(code) 
    if spaces is None or spaces > indent or spaces < 0: spaces = indent
    #XXX: will this delete '\n' in some cases?
    if not all: return code[spaces:]
    return '\n'.join(_outdent(code.split('\n'), spaces=spaces, all=all))


#XXX: not sure what the point of _wrap is...
#exec_ = lambda s, *a: eval(compile(s, '<string>', 'exec'), *a)
__globals__ = globals()
__locals__ = locals()
wrap2 = '''
def _wrap(f):
    """ encapsulate a function and it's __import__ """
    def func(*args, **kwds):
        try:
            _ = eval(getsource(f, force=True)) #FIXME: safer, but not as robust
            #exec getimportable(f, alias='_') in %s, %s
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
            _ = eval(getsource(f, force=True)) #FIXME: safer, but not as robust
            #exec(getimportable(f, alias='_'), %s, %s)
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


def _enclose(object, alias=''): #FIXME: needs alias to hold returned object
    """create a function enclosure around the source of some object"""
    #XXX: dummy and stub should append a random string
    dummy = '__this_is_a_big_dummy_enclosing_function__'
    stub = '__this_is_a_stub_variable__'
    code = 'def %s():\n' % dummy
    code += indent(getsource(object, alias=stub, lstrip=True, force=True))
    code += indent('return %s\n' % stub)
    if alias: code += '%s = ' % alias
    code += '%s(); del %s\n' % (dummy, dummy)
   #code += "globals().pop('%s',lambda :None)()\n" % dummy
    return code


def dumpsource(object, alias='', new=False, enclose=True):
    """'dump to source', where the code includes a pickled object.

    If new=True and object is a class instance, then create a new
    instance using the unpacked class source code. If enclose, then
    create the object inside a function enclosure (thus minimizing
    any global namespace pollution).
    """
    from dill import dumps
    pik = repr(dumps(object))
    code = 'import dill\n'
    if enclose:
        stub = '__this_is_a_stub_variable__' #XXX: *must* be same _enclose.stub
        pre = '%s = ' % stub
        new = False #FIXME: new=True doesn't work with enclose=True
    else:
        stub = alias
        pre = '%s = ' % stub if alias else alias
    
    # if a 'new' instance is not needed, then just dump and load
    if not new or not _isinstance(object):
        code += pre + 'dill.loads(%s)\n' % pik
    else: #XXX: other cases where source code is needed???
        code += getsource(object.__class__, alias='', lstrip=True, force=True)
        mod = repr(object.__module__) # should have a module (no builtins here)
        if PYTHON3:
            code += pre + 'dill.loads(%s.replace(b%s,bytes(__name__,"UTF-8")))\n' % (pik,mod)
        else:
            code += pre + 'dill.loads(%s.replace(%s,__name__))\n' % (pik,mod)
       #code += 'del %s' % object.__class__.__name__ #NOTE: kills any existing!

    if enclose:
        # generation of the 'enclosure'
        dummy = '__this_is_a_big_dummy_object__'
        dummy = _enclose(dummy, alias=alias)
        # hack to replace the 'dummy' with the 'real' code
        dummy = dummy.split('\n')
        code = dummy[0]+'\n' + indent(code) + '\n'.join(dummy[-3:])

    return code #XXX: better 'dumpsourcelines', returning list of lines?


def getname(obj, force=False): #XXX: allow 'throw'(?) to raise error on fail?
    """get the name of the object. for lambdas, get the name of the pointer """
    if not getmodule(obj): # things like "None" and "1"
        if not force: return None
        return repr(obj)
    try:
        if obj.__name__ == '<lambda>':
            return getsource(obj).split('=',1)[0].strip()
        #XXX: 'wrong' for decorators and curried functions ?
        #       if obj.func_closure: ...use logic from getimportable, etc ?
        return obj.__name__
    except AttributeError: #XXX: better to just throw AttributeError ?
        if not force: return None
        name = repr(obj)
        if name.startswith('<'): # or name.split('('):
            return None
        return name


def _namespace(obj):
    """_namespace(obj); return namespace hierarchy (as a list of names)
    for the given object.  For an instance, find the class hierarchy.

    For example:

    >>> from functools import partial
    >>> p = partial(int, base=2)
    >>> _namespace(p)
    [\'functools\', \'partial\']
    """
    # mostly for functions and modules and such
    #FIXME: 'wrong' for decorators and curried functions
    try: #XXX: needs some work and testing on different types
        module = qual = str(getmodule(obj)).split()[1].strip('"').strip("'")
        qual = qual.split('.')
        if ismodule(obj):
            return qual
        # get name of a lambda, function, etc
        name = getname(obj) or obj.__name__ # failing, raise AttributeError
        # check special cases (NoneType, Ellipsis, ...)
        if module in ['builtins', '__builtin__']: #XXX: BuiltinFunctionType
            if name == 'ellipsis': name = 'EllipsisType'
            if _intypes(name): return ['types'] + [name]
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
        # check special cases (NoneType, Ellipsis, ...)
        if qual[-1] == 'ellipsis': qual[-1] = 'EllipsisType'
        if _intypes(qual[-1]): module = 'types' #XXX: BuiltinFunctionType
        qual = [module] + qual
    return qual


def _getimport(head, tail, verify=True, builtin=False):
    """helper to build a likely import string from head and tail of namespace"""
    # special handling for a few common types
    if tail in ['Ellipsis', 'NotImplemented'] and head in ['types']:
        head = len.__module__
    elif tail in ['None'] and head in ['types']: return '' # can't import None
    # we don't need to import from builtins, so return ''
#   elif tail in ['NoneType','int','float','long','complex']: return '' #XXX: ?
    if head in ['builtins','__builtin__']:
        # special cases (NoneType, Ellipsis, ...) #XXX: BuiltinFunctionType
        if tail == 'ellipsis': tail = 'EllipsisType'
        if _intypes(tail): head = 'types'
        elif not builtin: return ''
        else: pass # handle builtins below
    # get likely import string
    if not head: _str = "import %s\n" % tail
    else: _str = "from %s import %s\n" % (head, tail)
    # FIXME: fails on most decorators, currying, and such...
    #        (could look for magic __wrapped__ or __func__ attr)
    #        (could fix in 'namespace' to check obj for closure)
    if verify and not head.startswith('dill.'):# weird behavior for dill
       #print(_str)
        try: exec(_str) #XXX: check if == obj? (name collision)
        except ImportError: #XXX: better top-down or bottom-up recursion?
            _head = head.rsplit(".",1)[0] #(or get all, then compare == obj?)
            if not _head: raise
            if _head != head:
                _str = _getimport(_head, tail, verify)
    return _str


def getimport(obj, verify=True, builtin=False):
    """get the likely import string for the given object

    obj: the object to inspect
    verify: if True, then try to verify with an attempted import
    builtin: if True, then also include imports for builtins
    """
    # for named things... with a nice repr #XXX: move into _namespace?
    if not repr(obj).startswith('<'): name = repr(obj).split('(')[0]
    else: name = None
    # get the namespace
    qual = _namespace(obj)
    head = '.'.join(qual[:-1])
    tail = qual[-1]
    if name: # try using name instead of tail
        try: return _getimport(head, name, verify, builtin)
        except (ImportError,SyntaxError): pass
    try:
       #if type(obj) is type(abs): _builtin = builtin # BuiltinFunctionType
       #else: _builtin = False
        return _getimport(head, tail, verify, builtin)
    except (ImportError,SyntaxError):
        raise # could do some checking against obj


# def _getimportable(obj, alias='', source=False, builtin=False):
def _getcode(obj, alias='', source=True, builtin=True):
    """get source code for an importable obj, if possible; otherwise get import

For simple objects, this function will discover the name of the object, or the
repr of the object, or the source code for the object. To attempt to force
discovery of the source code, use source=True, otherwise an import will be
sought. The intent is to build a string that can be imported from a python
file. Use builtin=True if imports from builtins need to be included.
    """
   #FIXME: fails for decorated functions
   #try: # get the module name (to see if it's __main__)
   #    module = str(getmodule(obj)).split()[1].strip('"').strip("'")
   #except: module = ''
    try: _import = getimport(obj, builtin=builtin)
    except: _import = ""
    if source: # get the source
        try: return getsource(obj, alias=alias)
        except: pass
    # get the name (of functions, lambdas, and classes)
    # or hope that obj can be built from the __repr__
    #XXX: what to do about class instances and such?
    obj = getname(obj, force=True)
    # we either have __repr__ or __name__ (or None)
    if not obj or obj.startswith('<'):
        raise AttributeError("object has no atribute '__name__'")
    elif alias: result = _import+'%s = %s\n' % (alias,obj)
    elif _import.endswith('%s\n' % obj): result = _import
    else: result = _import+'%s\n' % obj
    return result
    #XXX: possible failsafe... (for example, for instances when source=False)
    #     "import dill; result = dill.loads(<pickled_object>); # repr(<object>)"



# backward compatability
def likely_import(obj, passive=False, builtin=False):
    return getimport(obj, not passive, builtin)
def _likely_import(first, last, passive=False, explicit=True):
    return _getimport(first, last, not passive, explicit)
_get_name = getname
getblocks_from_history = getblocks

del sys


# EOF
