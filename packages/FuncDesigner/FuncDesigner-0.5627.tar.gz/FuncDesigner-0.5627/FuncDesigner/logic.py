PythonSum = sum
PythonAny = any
from numpy import array, inf, logical_and, all, isnan, ndarray, where, \
atleast_1d, isfinite, log2, logical_not, sum as np_sum#, empty_like
from FDmisc import FuncDesignerException, raise_except
from baseClasses import OOFun, OOArray
from types import GeneratorType

import operator

#def discreteNLH(_input_bool_oofun, Lx, Ux, p, dataType):
#    
#    T0, res, DefiniteRange = _input_bool_oofun.nlh(Lx, Ux, p, dataType)
#    #T = 1.0 - T0
#    #R = dict([(v, 1.0-val) for v, val in res.items()])
#    return T.flatten(), R, DefiniteRange

def nlh_and(_input, dep, Lx, Ux, p, dataType):
    nlh_0 = array(0.0)
    R = {}
    DefiniteRange = True
    
    elems_nlh = [(elem.nlh(Lx, Ux, p, dataType) if isinstance(elem, OOFun) \
                  else (0, {}, None) if elem is True 
                  else (inf, {}, None) if elem is False 
                  else raise_except()) for elem in _input]

    for T0, res, DefiniteRange2 in elems_nlh:
        DefiniteRange = logical_and(DefiniteRange, DefiniteRange2)
        
    for T0, res, DefiniteRange2 in elems_nlh:
        if T0 is None or T0 is True: continue
        if T0 is False or all(T0 == inf):
            return inf, {}, DefiniteRange
        if all(isnan(T0)):
            raise FuncDesignerException('unimplemented for non-oofun or fixed oofun input yet')
        
        if type(T0) == ndarray:
            if nlh_0.shape == T0.shape:
                nlh_0 += T0
            elif nlh_0.size == T0.size:
                nlh_0 += T0.reshape(nlh_0.shape)
            else:
                nlh_0 = nlh_0 + T0
        else:
            nlh_0 += T0
        
        T_0_vect = T0.reshape(-1, 1) if type(T0) == ndarray else T0
        
        for v, val in res.items():
            r = R.get(v, None)
            if r is None:
                R[v] = val - T_0_vect
            else:
                r += (val if r.shape == val.shape else val.reshape(r.shape)) - T_0_vect
    
    R, nlh_0 = update_R_nlh(R, nlh_0)
    return nlh_0, R, DefiniteRange
    
#    nlh_0_shape = nlh_0.shape
#    nlh_0 = nlh_0.reshape(-1, 1)
#    for v, val in R.items():
#        # TODO: check it
#        #assert all(isfinite(val))
#        tmp =  val + nlh_0
#        tmp[isnan(tmp)] = inf # when val = -inf summation with nlh_0 == inf
#        R[v] = tmp
#
#    return nlh_0.reshape(nlh_0_shape), R, DefiniteRange

def update_R_nlh(R, nlh_0):
    nlh_0_shape = nlh_0.shape
    nlh_0 = nlh_0.reshape(-1, 1)
    for v, val in R.items():
        # TODO: check it
        #assert all(isfinite(val))
        tmp =  val + nlh_0
        tmp[isnan(tmp)] = inf # when val = -inf summation with nlh_0 == inf
        R[v] = tmp
    
    nlh_0 = nlh_0.reshape(nlh_0_shape)
    return R, nlh_0#, DefiniteRange
    

def nlh_xor(_input, dep, Lx, Ux, p, dataType):
    nlh_0 = array(0.0)
    nlh_list = []
    nlh_list_m = {}
    num_inf_m = {}
    num_inf_0 = atleast_1d(0)
    num_inf_elems = []
    R_diff = {}
    R_inf = {}
    
    DefiniteRange = True

    elems_lh = [(elem.lh(Lx, Ux, p, dataType) if isinstance(elem, OOFun) \
                  else (inf, {}, None) if elem is True 
                  else (0, {}, None) if elem is False 
                  else raise_except()) for elem in _input]


    for T0, res, DefiniteRange2 in elems_lh:
        DefiniteRange = logical_and(DefiniteRange, DefiniteRange2)

    for j, (T0, res, DefiniteRange2) in enumerate(elems_lh):
        if T0 is None: 
            raise FuncDesignerException('probably bug in FD kernel')
        if isnan(T0).all():
            raise FuncDesignerException('unimplemented for non-oofun or fixed oofun input yet')
        
        T_inf = where(isfinite(T0), 0, 1)
        num_inf_elems.append(T_inf)
        T0 = where(isfinite(T0), T0, 0.0)
        if type(T0) == ndarray:
            if nlh_0.shape == T0.shape:
                nlh_0 += T0
                num_inf_0 += T_inf
            elif nlh_0.size == T0.size:
                nlh_0 += T0.reshape(nlh_0.shape)
                num_inf_0 += T_inf.reshape(nlh_0.shape)
            else:
                nlh_0 = nlh_0 + T0
                num_inf_0 = num_inf_0 + T_inf
        else:
            nlh_0 += T0
            num_inf_0 += T_inf
            
        nlh_list.append(T0)
        
        for v, val in res.items():
            T_inf_v = where(isfinite(val), 0, 1)
            val_noninf = where(isfinite(val), val, 0)
            T0v = val_noninf - T0.reshape(-1, 1)
            
            r = nlh_list_m.get(v, None)
            if r is None:
                nlh_list_m[v] = [(j, T0v)]
                num_inf_m[v] = [(j, T_inf_v.copy())]
                #num_inf_m[v] = T_inf_v.copy()
            else:
                r.append((j, T0v))
                num_inf_m[v].append((j, T_inf_v.copy()))
                #num_inf_m[v] +=T_inf_v
                
            r = R_inf.get(v, None)
            T_inf = T_inf.reshape(-1, 1)
            if r is None:
                R_inf[v] = T_inf_v - T_inf#.reshape(-1, 1)
                R_diff[v] = T0v.copy()
            else:
                # TODO: check for 1st elem of size 1
                r += (T_inf_v if r.shape == T_inf_v.shape else T_inf_v.reshape(r.shape))  - T_inf#.reshape(-1, 1)
                R_diff[v] += T0v
                
        
    nlh_1 = [nlh_0 - elem for elem in nlh_list]
    # !!! TODO: speedup it via matrix insted of sequence of vectors
    num_infs = [num_inf_0 - t for t in num_inf_elems]

    S1 = PythonSum(2.0 ** where(num_infs[j] == 0, -t, -inf) for j, t in enumerate(nlh_1))
    S2 = atleast_1d(len(elems_lh) * 2.0 ** (-nlh_0))
    S2[num_inf_0 != 0] = 0
    #nlh_t = -log(S2 - S1 + 1.0)
    #nlh_t = -log1p(S2 - S1) * 1.4426950408889634
    nlh_t = -log2(S1-S2)
#    assert not any(isnan(nlh_t))
#    if not all(isfinite(nlh_t)):
#        print('='*10)
#        print(nlh_t)
#        print(elems_lh)
#        raise 0
    #print(elems_lh)
#    print(R_inf)
    #raise 0
    R = {}
    nlh_0 = nlh_0.reshape(-1, 1)
    num_inf_0 = num_inf_0.reshape(-1, 1)

    for v, nlh_diff in R_diff.items():
        nlh = nlh_0 + nlh_diff
        nlh_1 = [nlh - elem.reshape(-1, 1) for elem in nlh_list]
        
        for j, val in nlh_list_m[v]:
            nlh_1[j] -= val
        Tmp = R_inf[v] + num_inf_0
        num_infs = [Tmp] * len(nlh_1)
        for j, num_inf in num_inf_m[v]:
            num_infs[j] = num_inf
        
        num_infs2 = [Tmp - elem for elem in num_infs]
        #num_infs = num_inf - num_inf_m[v]
        S1 = PythonSum(2.0 ** where(num_infs2[j] == 0, -elem, -inf) for j, elem in enumerate(nlh_1))
        S2 = atleast_1d(len(elems_lh)  * 2.0 ** (-nlh))
        S2[Tmp.reshape(S2.shape) != 0] = 0
        R[v] = -log2(S1 - S2)
        #R[v] = -log1p(S2 - S1) * 1.4426950408889634
        
    for v, val in R.items():
        val[isnan(val)] = inf
        val[val < 0.0] = 0.0
        
    # TODO: check is R, nlh_0 = update_R_nlh(R, nlh_0) required here
    # is seems like not, nlh = nlh_0 + nlh_diff is present in the cycle above
    
    return nlh_t, R, DefiniteRange


def nlh_not(_input_bool_oofun, dep, Lx, Ux, p, dataType):
    assert isinstance(_input_bool_oofun, OOFun), 'unimplemented for non-oofun input yet'
    
    T0, res, DefiniteRange = _input_bool_oofun.nlh(Lx, Ux, p, dataType)
    T = reverse_l2P(T0)
    R = dict((v, reverse_l2P(val)) for v, val in res.items())
    return T, R, DefiniteRange


def reverse_l2P(l2P):
    l2P = atleast_1d(l2P)# elseware bug "0-d arrays cannot be indexed"
    #l2P[l2P<0]=0
    r = 1.0 / l2P
    ind = l2P < 15
    r[ind] = -log2(1.0 - 2.0**(-l2P[ind]))
    #r[r<0] = 0
    return r

def AND(*args):
    '                                 Type checks                                 '
    
    
    if len(args) == 1:
        Args = args[0]
        if isinstance(Args, GeneratorType):
            Args = list(Args)
    else:
       Args = args
       assert not PythonAny(isinstance(arg, (list, set, tuple, ndarray)) and len(arg) > 1 for arg in args), 'unimplemented yet' 
    
    
    Args2 = []
    for arg in Args:
        if not isinstance(arg, OOFun):
            if arg is False:
                return False
            elif arg is True:
                continue
            # TODO: mb handle ndarray here
            raise FuncDesignerException('FuncDesigner logical AND currently is implemented for oofun instances only')
        Args2.append(arg)
    if len(Args2) == 0:
        return True
    elif len(Args2) == 1:
        return Args2[0]
    
    '                                    Engine                                    '
    
    from BooleanOOFun import BooleanOOFun
    f  = logical_and if len(Args2) == 2 else alt_AND_engine
    r = BooleanOOFun(f, Args2, vectorized = True, engine = 'AND')
    r.nlh = lambda *arguments: nlh_and(Args2, r._getDep(), *arguments)
    r.oofun = r# TODO: mb rework it
    return r
    
def alt_AND_engine(*input):
    #TODO:rework it when numpy.logical_and will be reworked/improved 
    tmp = input[0]
    for i in range(1, len(input)):
        tmp = logical_and(tmp, input[i])
    return tmp

# TODO: multiple args
XOR_prev = lambda arg1, arg2: (arg1 & NOT(arg2)) | (NOT(arg1) & arg2)

def XOR(*args):
    '                                 Type checks                                 '

    # TODO: handle input True/False here as it is done with AND and OR
    Args = args[0] if len(args) == 1 and isinstance(args[0], (ndarray, tuple, list, set)) \
    else list(args[0]) if isinstance(args[0], GeneratorType)\
    else args
    
    assert not isinstance(args[0], ndarray) or args[0].ndim <= 1, 'unimplemented yet' 
    for arg in Args:
        if not isinstance(arg, OOFun):
            raise FuncDesignerException('FuncDesigner logical XOR currently is implemented for oofun instances only')    
    #f = lambda *args: logical_xor(hstack([asarray(elem).reshape(-1, 1) for elem in args]))
    
    '                                    Engine                                    '
    
    from BooleanOOFun import BooleanOOFun
    F_xor = operator.xor if len(Args) == 2 else f_xor
    r = BooleanOOFun(F_xor, Args, vectorized = True, engine = 'XOR')
    r.nlh = lambda *arguments: nlh_xor(Args, r._getDep(), *arguments)
    r.oofun = r # is it required?# TODO: mb rework it
    
    return r
    
def f_xor(*args):
    # TODO: rework it, mb when numpy.logical_xor will be updated
#    import time
#    t = time.time()
#    if type(args[0])==ndarray and args[0].size > 100:
#        print('size: %d  num_elems: %d' % (args[0].size, len(args)))
#        N = 10000
#        from numpy import empty_like
#        for i in range(N):
#            has_at_least_one_true = empty_like(args[0])
#            has_at_least_one_true.fill(False)
#            has_more_then_one_true = empty_like(args[0])
#            has_more_then_one_true.fill(False)
#            for arg in args:
#                has_more_then_one_true |= (has_at_least_one_true & arg)
#                has_at_least_one_true |= arg
#            r = has_at_least_one_true & (~has_more_then_one_true)
#            r1 = r
#        print('way1: time = % 0.1f' % (time.time()-t))
#        
#        t = time.time()
#        for i in range(N):
#            tmp = np_sum(array(args, int), 0)
#            r = tmp == 1
#            r2 = r
#        print('way2: time = % 0.1f' % (time.time()-t))
#        if not all(r1==r2): 
#            print('NOT EQUAL!')
#            input()
#        print('-----')
#    print(array(args, int).shape)
    r = np_sum(array(args, int), 0) == 1
    #r = sum(array(args), 0) == 1
    
    return r


EQUIVALENT = lambda arg1, arg2: (arg1 & arg2) | (NOT(arg1) & NOT(arg2))
    
def NOT(_bool_oofun):
    
    '                        Type checks                        '
    
    if _bool_oofun is False:
        return True
    elif _bool_oofun is True:
        return False
    
    if isinstance(_bool_oofun, ndarray):
        if ndarray.dtype == bool:
            return logical_not(_bool_oofun)
        elif isinstance(_bool_oofun, OOArray):
            return OOArray([NOT(elem) for elem in _bool_oofun])
        else:
           raise FuncDesignerException('FuncDesigner logical NOT invoked on ndarray of unclear dtype')
    assert not isinstance(_bool_oofun, (list, tuple, set)), 'FuncDesigner logical NOT is not implemented for lists/tuples/sets yet' 
    if not isinstance(_bool_oofun, OOFun):
        raise FuncDesignerException('FuncDesigner logical NOT invoked on data of type %s' % type(_bool_oofun))
    
    
    '                           Engine                          '
    
    if '_invert' in _bool_oofun.__dict__:
        return _bool_oofun._invert
    
    from BooleanOOFun import BooleanOOFun
    r = BooleanOOFun(logical_not, [_bool_oofun], vectorized = True, lh = _bool_oofun.nlh)
    r._lh_natively_implemented = True
    r.oofun = r# TODO: mb rework it
    
    r.nlh = _bool_oofun.lh if _bool_oofun._lh_natively_implemented \
    else lambda *arguments: nlh_not(_bool_oofun, r._getDep(), *arguments)

    _bool_oofun._invert = r
    r._invert = _bool_oofun
    r.engine = 'NOT'

    return r

# TODO: mb implement it (requires expr with possibly some filtered arg(s))
#def NAND(*args, **kw): 
#    r = NOT(AND(*args, **kw))
#    r.expression = lambda *args, **kw: ...
#    return r

NAND = lambda *args, **kw: NOT(AND(*args, **kw))
NOR = lambda *args, **kw: NOT(OR(*args, **kw))


def OR(*args):
    '                        Type checks                        '
    
    Args = args[0] if len(args) == 1 and isinstance(args[0], (ndarray, list, tuple, set)) else args
    assert not isinstance(args[0], ndarray) or args[0].ndim <= 1, 'unimplemented yet' 
    Args2 = []
    for arg in Args:
        if not isinstance(arg, OOFun):
            if arg is True:
                return True
            elif arg is False:
                continue
            # TODO: mb handle ndarray here
            raise FuncDesignerException('''
            FuncDesigner logical OR currently is implemented 
            for oofun instances or list/tuple/set/1dim_array on them only''')
        Args2.append(arg)
        
    if len(Args2) == 0:
        return False
    elif len(Args2) == 1:
        return Args2[0]
    
    '                           Engine                          '
    
    r =  NAND(NOT(elem) for elem in Args2)
    #r.fun = np.logical_or
    r.oofun = r# TODO: mb rework it

    r.expression = lambda *args, **kw: 'OR(%s)' % \
    ''.join((elem.expression(*args, **kw)+', ' for elem in Args2))[:-2]
    return r


#prev
#def IMPLICATION(condition, *args):
#    if condition is False: 
#        return True
#    if len(args) == 1 and isinstance(args[0], (tuple, set, list, ndarray)):
#        return OR(NOT(condition), AND(args[0]))
#        #return ooarray([IMPLICATION(condition, elem) for elem in args[0]]) if condition is not True else args[0]
#    elif len(args) > 1:
#        return OR(NOT(condition), AND(args))
##        return ooarray([IMPLICATION(condition, elem) for elem in args]) if condition is not True else args
#    return NOT(condition & NOT(args[0])) if condition is not True else args[0]
#    


#new
def IMPLICATION(condition, *args):
    if isinstance(condition, ndarray):
        assert condition.size == 1
        condition = condition.item()
    if condition is False: 
        return True
    
    if len(args) > 1:
        consequence = AND(args)
    elif isinstance(args[0], (tuple, set, list, ndarray)):
        assert len(args) < 2, 'unimplemented for the case yet'
        consequence = AND(args[0])
    else:
        consequence = args[0]
    
    if condition is True:
        return consequence
    
    # equivalent for OR(NOT(condition), consequence)
    r = NOT(condition & NOT(consequence))
    r.expression = lambda *args, **kw: 'IMPLICATION(%s, %s)' \
    % (condition.expression(*args, **kw), consequence.expression(*args, **kw))
    return r
