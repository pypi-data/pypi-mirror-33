>>> import dill 
>>> def foo(f):
...   squared = lambda x: f(x)**2
...   return squared
... 
>>> @foo
... def bar(x):
...   return 2*x
... 
>>> dill.source.importable(bar, source=False)
'from __main__ import bar\n'
>>> 
>>> lines,lnum = dill.source.findsource(bar)
>>> lnum
0
>>> 
>>> pat2 = r'^(\s*@)'
>>> name = bar.__name__
>>> name 
'<lambda>'
>>> pat1 = r'(.*(?<!\w)lambda(:|\s))'
>>> object = bar.func_code
>>> stdin = object.co_filename == '<stdin>'
>>> stdin
True
>>> lnum = len(lines) - 1
>>> lnum
1408
>>> pat1
'(.*(?<!\\w)lambda(:|\\s))'
>>> import re
>>> pat1 = re.compile(pat1)
>>> pat2 = re.compile(pat2)
>>> dummy = lambda : '__this_is_a_big_dummy_function__'
>>> 
>>> [i for i in range(lnum) if pat1.match(lines[i])]
[1360, 1382, 1391]
>>> 
>>> line = lines[1391] 
>>> line
'  squared = lambda x: f(x)**2\n'
>>> 
>>> lhs,rhs = line.split('lambda ',1)[-1].split(":", 1)
>>> lhs
'x'
>>> rhs
' f(x)**2\n'
>>> _ = eval("lambda %s : %s" % (lhs,rhs), globals(), locals())
>>> _
<function <lambda> at 0x109cf2050>
>>> _
<function <lambda> at 0x109cf2050>
>>> bar(2)
16
>>> _(2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <lambda>
NameError: global name 'f' is not defined
>>> _bar = _
>>> _bar
<function <lambda> at 0x109cf2050>
>>> 
>>> _ = _.func_code
>>> _
<code object <lambda> at 0x109ceb230, file "<string>", line 1>
>>> 
>>> _.co_code
't\x00\x00|\x00\x00\x83\x01\x00d\x01\x00\x13S'
>>> object.co_code
'\x88\x00\x00|\x00\x00\x83\x01\x00d\x01\x00\x13S'
>>> 
>>> dill.detect.globalvars(bar)
{}
>>> dill.detect.globalvars(_bar)
{}
>>> dill.detect.varnames(bar)   
(('x',), ())
>>> dill.detect.varnames(_bar)
(('x',), ())
>>> dill.detect.freevars(bar)
{'f': <function bar at 0x109ceede8>}
>>> dill.detect.freevars(_bar)
{}
>>> dill.source.getsource(dill.detect.freevars(bar)['f'])
'@foo\ndef bar(x):\n  return 2*x\n'
>>> 
### If no 'freevars', check code for a match.
### If has 'freevars', then can't check code for a exact match...
###  1) should be indented, check for an indent (if freevars)s
###  -) should have all(key in line for key in freevars.keys())
###  -) should have all(key in line for key in globalvars.keys())
###  -) should have all "varnames in line"
###  5) should have a 'near match' of "func_code.co_code"  ***see below***
###     * split code on [0] character
###     * 'throw out' first '\x*' for each string item (should same set)
###     * ...everything else should match

>>> def aaa(a,b):
...   def bbb(f):
...     ccc = lambda x: a*f(x) + b
...     return ccc
...   return bbb
... 
>>> @aaa(2,3)
... def ddd(x):
...   return x
... 
>>> ddd(2)
7
>>> ddd
<function <lambda> at 0x109cf21b8>
>>> ###############################################################
>>> line = "  lambda x: a*f(x) + b"
>>> 
>>> dill.detect.freevars(ddd)
{'a': 2, 'b': 3, 'f': <function ddd at 0x109cf2230>}
>>> dill.detect.globalvars(ddd)
{}
>>> dill.detect.varnames(ddd)
(('x',), ())
>>> _f = [line.count(i) for i in dill.detect.freevars(ddd).keys()]
>>> if _f:
...   all(_f) == True  #XXX: VERY WEAK
...   bool(dill.source.indentsize(line)) == True
... else:
...   bool(dill.source.indentsize(line)) == False
...
>>> _f = dill.detect.varnames(ddd)
>>> _f = [line.count(i) for i in _f[0]+_f[1]]
>>> if _f:
...   all(_f) == True  #XXX: VERY WEAK
>>> _f = [line.count(i) for i in dill.detect.globalvars(ddd).keys()]
>>> if _f:
...   all(_f) == True  #XXX: VERY WEAK
>>> ###############################################################
>>> # < process line here >
>>> zzz = eval("lambda x: a*f(x) + b")
>>> zzz.func_code.co_code
't\x00\x00t\x01\x00|\x00\x00\x83\x01\x00\x14t\x02\x00\x17S'
>>> ddd.func_code.co_code
'\x88\x00\x00\x88\x02\x00|\x00\x00\x83\x01\x00\x14\x88\x01\x00\x17S'
>>> _zzz = zzz.func_code.co_code
>>> _ddd = ddd.func_code.co_code
>>> _d = _ddd.split(_ddd[0])  # '\x88'
>>> _z = _zzz.split(_zzz[0])  # 't'
>>> 
>>> _d = dict(re.match('([\W\D\S])(.*)', _d[i]).groups() for i in range(1,len(_d)))
>>> _z = dict(re.match('([\W\D\S])(.*)', _z[i]).groups() for i in range(1,len(_z)))
>>> _d.keys() == _z.keys()  #XXX: TRUE
>>> sorted(_d.values()) == sorted(_z.values()) #XXX: TRUE



