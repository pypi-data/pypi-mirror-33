from mystic.symbolic import *

#XXX: finds (X-1) not (X-1)**2, however tan(X-1) not (X-1)
def _denominator(equation, variables=None):
    """find denominators containing the given variables in an equation"""
    import re
    # deal with the lhs and rhs separately
    cmp = comparator(equation)
    if cmp:
        lhs,equation = equation.split(cmp,1)
        lhs = _denominator(lhs, variables)
    else: lhs = []
    # remove the enclosing parenthesis
    par = lambda eqn: eqn.startswith('(') and eqn.endswith(')') and eqn.count(')')+eqn.count('(') is 2
    nopar = lambda eqn: eqn[1:-1] if (par(eqn) or (re.findall('^\([^\)]*\(', eqn) and re.findall('\)[^\(]*\)$', eqn))) else eqn
    equation = nopar(equation.strip())
    # check if variables x are found in eqn
    has = lambda eqn,x: (get_variables(eqn,x) if x else True)
    # check if parentheses are unbalanced
    unbalanced = lambda eqn: (eqn.find(')') < eqn.find('('))
    res = []
    var, expr = equation.count('/'), equation.count('\(')
    ### find ['x1', 'tan(x1-x2)']
    if var > expr:
        _res = [i.strip('/') for i in re.findall('/\S+', equation) if not i.startswith('/(')]
        res.extend([i.split(')')[0] if unbalanced(i) else i for i in _res if has(i,variables)])
        if len(res) != len(_res): var -= len(_res)
        del _res
        #XXX: recurse/etc on f(x)?
    if var is len(res): return lhs+res
    ### find ['1/(x1 - x2)']
    l = len(res)
    _res = [i.strip('/') for i in re.findall('/\([^\(]*\)', equation)]
    res.extend([i for i in _res if has(i,variables)])
    if len(res) - l != len(_res): var -= len(_res)
    del _res
    if var is len(res): return lhs+res
    ### find ['1/(x1 - (x2*x1))', etc]
    l = len(res)
    _res = [i.strip('/') for i in re.findall('/\(.*\)', equation)]
    res.extend([i for i in _res if has(i,variables)])
    if len(res) - l != len(_res): var -= len(_res)
    del _res
    if var is len(res): return lhs+res
    ### still missing some... check recursively
    _res = [_denominator(nopar(i),variables) for i in res]
    for i in _res:
        res.extend(i)
    del _res
    if var > len(res):
        msg = '%s of %s denominators were not found' % (var-len(res), var)
        raise ValueError(msg)
    return lhs+res


#XXX: add target=None to kwds?
def _solve_zeros(equation, variables=None, implicit=True):
    '''symbolic solve the equation for when produces a ZeroDivisionError''' 
    res = _denominator(equation, variables)#XXX: w/o this, is a general solve
    x = variables or 'x'
    for i,eqn in enumerate(res):
        _eqn = eqn+' = 0'
        try:
            _eqn = solve(_eqn, target=variables, variables=x)
            if not _eqn: raise ValueError()
        except ValueError:
            if not implicit:
               msg = "cannot simplify '%s'" % _eqn
               raise ValueError(msg)
            #else: pass
        res[i] = _eqn
    return res


def equals(before, after, vals=None, **kwds):
    """check if equations before and after are equal for the given vals

Inputs:
    before -- an equation string
    after -- an equation string
    vals -- a dict with variable names as keys and floats as values

Additional Inputs:
    variables -- a list of variable names
    locals -- a dict with variable names as keys and 'fixed' values
    variants -- a list of ints to use as variants for fractional powers
    verbose -- print debug messages
"""
    variants = kwds.get('variants', None)
    verbose = kwds.get('verbose', False)
    vars = kwds.get('variables', 'x')
    _vars = get_variables(after, vars)
    locals = kwds['locals'] if 'locals' in kwds else None
    if locals is None: locals = {}
    if vals is None: vals = {}
    locals.update(vals)
    if verbose: print locals
    locals_ = locals.copy() #XXX: HACK _locals
    while variants:
        try:
            after, before = eval(after,{},locals_), eval(before,{},locals_)
            break
        except ValueError as error:  #FIXME: python2.5
            if error.message.startswith('negative number') and \
               error.message.endswith('raised to a fractional power'):
                val = variants.pop()
                [locals_.update({k:v+val}) for k,v in locals_.items() if k in _vars]
            else:
                raise error
    else: #END HACK
        after, before = eval(after,{},locals_), eval(before,{},locals_)
    return before is after


#FIXME: should minimize number of times LHS is reused; (or use 'and_')?
def simplify(constraints, variables='x', target=None, **kwds):
    """simplify a system of symbolic constraints equations.

Returns a system of equations where a single variable has been isolated on
the left-hand side of each constraints equation, thus all constraints are
of the form "x_i = f(x)".

Inputs:
    constraints -- a string of symbolic constraints, with one constraint
        equation per line. Standard python syntax should be followed (with
        the math and numpy modules already imported).

    For example:
        >>> constraints = '''
        ...     x0 - x2 <= 2.
        ...     x2 = x3*2.'''
        >>> print simplify(constraints)
        x0 <= x2 + 2.0
        x2 = 2.0*x3
        >>> constraints = '''
        ...     x0 - x1 - 1.0 = mean([x0,x1])   
        ...     mean([x0,x1,x2]) >= x2'''
        >>> print simplify(constraints)
        x0 = 3.0*x1 + 2.0
        x0 >= -x1 + 2*x2

Additional Inputs:
    variables -- desired variable name. Default is 'x'. A list of variable
        name strings is also accepted for when desired variable names
        don't have the same base, and can include variables that are not
        found in the constraints equation string.
    target -- list providing the order for which the variables will be solved.
        If there are "N" constraint equations, the first "N" variables given
        will be selected as the dependent variables. By default, increasing
        order is used.

Further Inputs:
    locals -- a dictionary of additional variables used in the symbolic
        constraints equations, and their desired values.
    cycle -- boolean to cycle the order for which the variables are solved.
        If cycle is True, there should be more variety on the left-hand side
        of the simplified equations. By default, the variables do not cycle.
    all -- boolean to return all simplifications due to negative values.
        When dividing by a possibly negative variable, an inequality may flip,
        thus creating alternate simplifications. If all is True, return all
        of the possible simplifications due to negative values in an inequalty.
        The default is False, returning only one possible simplification.
"""
    all = kwds.get('all', False)
    import random
    import itertools as it
    locals = kwds['locals'] if 'locals' in kwds else {} #XXX: HACK _locals
    _locals = {}
    # default is _locals with numpy and math imported
    # numpy throws an 'AttributeError', but math passes error to sympy
    code = """from numpy import *; from math import *;""" # prefer math
    code += """from numpy import mean as average;""" # use np.mean not average
    code += """from numpy import var as variance;""" # look like mystic.math
    code += """from numpy import ptp as spread;"""   # look like mystic.math
    code += """_sqrt = lambda x:x**.5;""" # 'domain error' to 'negative power'
    code = compile(code, '<string>', 'exec')
    exec code in _locals
    _locals.update(locals)
    kwds['locals'] = _locals
    del locals

    def _simplify(eqn, rand=random.random, target=None, **kwds):
        'isolate one variable on the lhs'
        verbose = kwds.get('verbose', False)
        vars = kwds.get('variables', 'x')
        cmp = comparator(eqn)
        # get all variables used
        allvars = get_variables(eqn, vars)
        # find where the sign flips might occur (from before)
        res = eqn.replace(cmp,'=')
        zro = _solve_zeros(res, allvars)
        # check which variables have been used
        lhs = lambda zro: tuple(z.split('=')[0].strip() for z in zro)
        used = lhs(zro) #XXX: better as iterator?
        # cycle used variables to the rear
        _allvars = []
        _allvars = [i for i in allvars if i not in used or (_allvars.append(i) if i not in _allvars else False)] + _allvars
        # simplify so lhs has only one variable
        res = solve(res, target=target, **kwds)
        _eqn = res.replace('=',cmp)
        # find where the sign flips might occur (from after)
        zro += _solve_zeros(res, get_variables(res.split('=')[-1],_allvars))
        _zro = [z.replace('=','!=') for z in zro]
        if verbose: print 'in: %s\nout: %s\nzero: %s' % (eqn, _eqn, _zro)
        # if no inequalities, then return
        if not cmp.count('<')+cmp.count('>'):
            return '\n'.join([_eqn]+_zro) if _zro else _eqn
        del _zro

        # make sure '=' is '==' so works in eval
        before,after = (eqn,_eqn) if cmp != '=' else (eqn.replace(cmp,'=='),_eqn.replace(cmp,'=='))
        #HACK: avoid (rand-M)**(1/N) w/ (rand-M) negative; sqrt(x) to x**.5
        before = before.replace('sqrt(','_sqrt(')
        after = after.replace('sqrt(','_sqrt(')

        # sort zeros so equations with least variables are first
        zro.sort(key=lambda z: len(get_variables(z, vars))) #XXX: best order?
        # build dicts of test variables, with +/- epsilon at solved zeros
        testvars = dict((i,2*rand()-1) for i in allvars)
        eps = str(.01 * rand()) #XXX: better epsilon?
        #FIXME: following not sufficient w/multiple 'zs' (A != 0, A != -B)
        testvals = it.product(*((z+'+'+eps,z+'-'+eps) for z in zro))
        # build tuple of corresponding comparators for testvals
        signs = it.product(*(('>','<') for z in zro))

        def _testvals(testcode):
            '''generate dict of test values as directed by the testcode'''
            locals = _locals.copy()
            locals.update(testvars)
            code = ';'.join(i for i in testcode)
            code = compile(code, '<string>', 'exec')
            try:
                exec code in locals
            except SyntaxError as error:
                msg = "cannot simplify '%s'" % testcode
                raise SyntaxError(msg,) 
            return dict((i,locals[i]) for i in allvars)

        # iterator of dicts of test values
        testvals = it.imap(_testvals, testvals)

        # evaluate expression to see if comparator needs to be flipped
        results = []
        variants = (100000,-200000,100100,-200,110,-20,11,-2,1) #HACK
        kwds['variants'] = list(variants)
        for sign in signs:
            if equals(before,after,testvals.next(),**kwds):
                new = [after]
            else:
                new = [after.replace(cmp,flip(cmp))]
            new.extend(z.replace('=',i) for (z,i) in it.izip(zro,sign))
            results.append(new)

        # reduce the results to the simplest representation
       #results = condense(*results, **kwds) #XXX: remove depends on testvals
        # convert results to a tuple of multiline strings
        results = tuple('\n'.join(i).replace('_sqrt(','sqrt(') for i in results)
        if len(results) is 1: results = results[0]
        return results

    #### ...the rest is simplify()... ###
    cycle = kwds.get('cycle', False)
    eqns = []
    used = []
    for eqn in constraints.strip().split('\n'):
        # get least used, as they are likely to be simpler
        vars = get_variables(eqn, variables)
        vars.sort(key=eqn.count) #XXX: better to sort by count(var+'**')?
        vars = target[:] if target else vars
        if cycle: vars = [var for var in vars if var not in used] + used
        while vars:
            try: # cycle through variables trying 'simplest' first
                res = _simplify(eqn, variables=variables, target=vars, **kwds)
                #print '#:', res
                res = res if type(res) is tuple else (res,)
                eqns.append(res)
                r = res[0] #XXX: only add the 'primary' variable to used
                used.append(r.split(comparator(r.split('\n')[0]),1)[0].strip())
                #print "v,u: ", vars, used
                break
            except ValueError:
                if isinstance(vars, basestring): vars = []
                else: vars.pop(0)
                #print "v,u: ", vars, used
        else: # failure... so re-raise error
            res = _simplify(eqn, variables=variables, target=target, **kwds)
            #print 'X:', res
            res = res if type(res) is tuple else (res,)
            eqns.append(res)
    #print eqns
    _eqns = it.product(*eqns)
    eqns = tuple('\n'.join(i) for i in _eqns)
    # "merge" the multiple equations to find simplest bounds
    eqns = tuple(merge(*e.split('\n'), inclusive=False) for e in eqns)
    if eqns.count(None) is len(eqns): return None
    #   msg = 'No solution'
    #   raise ValueError(msg) #XXX: return None? throw Error? or ???
    eqns = tuple('\n'.join(e) for e in eqns if e != None)
    #XXX: if all=False, is possible to return "most True" (smallest penalty)?
    return (eqns if all else eqns[random.randint(0,len(eqns)-1)]) if len(eqns) > 1 else (eqns[0] if len(eqns) else '')

#### THE ABOVE IS UNUSED; IS A COPY OF CONTENTS IN ms.symbolic ####

if __name__ == '__main__':
    eps = 1e-16
    equations = """
    A*(B-C) + 2*C > 1
    B + C = 2*D
    D < 0
    """
    print equations

    from mystic.constraints import and_ as _and, or_ as _or
    from mystic.coupler import and_, or_
    import mystic.symbolic as ms
    var = list('ABCD')
    eqns = ms.simplify(equations, variables=var, all=True)
    if isinstance(eqns, basestring):
      _join = join_ = None
      print eqns
    else:
      _join,join_ = _or,or_
      for eqn in eqns:
        print eqn + '\n----------------------'

    constrain = ms.generate_constraint(ms.generate_solvers(eqns, var, locals=dict(e_=eps)), join=_join)
    solution = constrain([1,2,1,-1])

    print 'solved: ', dict(zip(var, solution))

    penalty = ms.generate_penalty(ms.generate_conditions(eqns, var, locals=dict(e_=eps)), join=join_)
    print 'penalty: ', penalty(solution)
    #XXX: worry about ZeroDivisionError ?

