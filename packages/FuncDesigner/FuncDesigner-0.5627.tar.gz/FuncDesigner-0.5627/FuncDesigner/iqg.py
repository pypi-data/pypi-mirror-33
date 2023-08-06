from ooPoint import ooPoint
from numpy import all, atleast_1d, logical_or, logical_and, bool_, vstack, logical_not
import numpy as np
from Interval import splitDomainForDiscreteVariable
from FDmisc import Copy
from baseClasses import Stochastic

# for PyPy
from FDmisc import where

try:
    from bottleneck import nanmin, nanmax
except ImportError:
    from numpy import nanmin, nanmax

def iqg(Self, domain, dtype = float, lb=None, ub=None, UB = None):
    if type(domain) != ooPoint:
        domain = ooPoint(domain, skipArrayCast=True)
        domain.isMultiPoint=True
    domain.useSave = True
    r0 = Self.interval(domain, dtype, resetStoredIntervals = False)
    
    r0.lb, r0.ub = atleast_1d(r0.lb).copy(), atleast_1d(r0.ub).copy() # is copy required?
    
    # TODO: get rid of useSave
    domain.useSave = False
    
    # TODO: rework it with indexation of required data
    if lb is not None and ub is not None:
        # comes from constraints
        ind = logical_or(logical_or(r0.ub < lb, r0.lb > ub), all(logical_and(r0.lb >= lb, r0.ub <= ub)))
    elif UB is not None:
        # comes from objective (excluding MOP)
        ind = r0.lb > UB # TODO: mb add fTol here? at least until feasible point is not obtained yet
    else:
        ind = None
    
    useSlicing = False
    
    if ind is not None:
        if all(ind):
            return {}, r0
        j = where(logical_not(ind))[0]
        #DOESN'T WORK FOR FIXED OOVARS AND DefiniteRange != TRUE YET
        if 0 and j.size < 0.85*ind.size:  # at least 15% of values to skip
            useSlicing = True
            tmp = []
            for key, val in domain.storedIntervals.items():
                Interval, definiteRange = val
                if type(definiteRange) not in (bool, bool_):
                    definiteRange = definiteRange[j]
                tmp.append((key, (Interval[:, j], definiteRange)))
            _storedIntervals = dict(tmp)
            
            Tmp = []
            for key, val in domain.storedSums.items():
                # TODO: rework it
                R0, DefiniteRange0 = val.pop(-1)
                #R0, DefiniteRange0 = val[-1]
                R0 = R0[:, j]
                if type(DefiniteRange0) not in (bool, bool_):
                    DefiniteRange0 = DefiniteRange0[j]
                tmp = []
                for k,v in val.items():
                    # TODO: rework it
#                        if k is (-1): continue
                    v = v[:, j]
                    tmp.append((k,v))
                val = dict(tmp)
                val[-1] = (R0, DefiniteRange0)
                Tmp.append((key,val))
            _storedSums = dict(Tmp)
            #domain.storedSums = dict(tmp)
            
            Tmp = []
            for key, val in domain.items():
                lb_,ub_ = val
                # TODO: rework it when lb, ub will be implemented as 2-dimensional
                Tmp.append((key, (lb_[j],ub_[j])))
            dictOfFixedFuncs = domain.dictOfFixedFuncs
            domain2 = ooPoint(Tmp, skipArrayCast=True)
            domain2.storedSums = _storedSums
            domain2.storedIntervals = _storedIntervals
            domain2.dictOfFixedFuncs = dictOfFixedFuncs
            domain2._dictOfRedirectedFuncs = domain._dictOfRedirectedFuncs
            domain2.nPoints = domain.nPoints
            domain2.isMultiPoint=True
            domain = domain2
            
    domain.useAsMutable = True
    
    r = {}
    # TODO: mb omit recalculation for OpenOpt problems
    Dep = Self.Dep.intersection(domain.keys())
    
    for i, v in enumerate(Dep):
        domain.modificationVar = v
        r_l, r_u = _iqg(Self, domain, dtype, r0)
        if useSlicing and r_l is not r0:# r_l is r0 when array_equal(lb, ub)
            lf1, lf2, uf1, uf2 = r_l.lb, r_u.lb, r_l.ub, r_u.ub
            Lf1, Lf2, Uf1, Uf2 = Copy(r0.lb), Copy(r0.lb), Copy(r0.ub), Copy(r0.ub)
            Lf1[:, j], Lf2[:, j], Uf1[:, j], Uf2[:, j] = lf1, lf2, uf1, uf2
            r_l.lb, r_u.lb, r_l.ub, r_u.ub = Lf1, Lf2, Uf1, Uf2
            if type(r0.definiteRange) not in (bool, bool_):
                d1, d2 = r_l.definiteRange, r_u.definiteRange
                D1, D2 = atleast_1d(r0.definiteRange).copy(), atleast_1d(r0.definiteRange).copy()
                D1[j], D2[j] = d1, d2
                r_l.definiteRange, r_u.definiteRange = D1, D2
            
        r[v] = r_l, r_u
        if not Self.isUncycled:
            lf1, lf2, uf1, uf2 = r_l.lb, r_u.lb, r_l.ub, r_u.ub
            lf, uf = nanmin(vstack((lf1, lf2)), 0), nanmax(vstack((uf1, uf2)), 0)
            if i == 0:
                L, U = lf.copy(), uf.copy()
            else:
                L[L<lf] = lf[L<lf].copy()
                U[U>uf] = uf[U>uf].copy()
    if not Self.isUncycled:
        for R in r.values():
            r1, r2 = R
            if type(r1.lb) != np.ndarray:
                r1.lb, r2.lb, r1.ub, r2.ub = atleast_1d(r1.lb), atleast_1d(r2.lb), atleast_1d(r1.ub), atleast_1d(r2.ub)
            r1.lb[r1.lb < L] = L[r1.lb < L]
            r2.lb[r2.lb < L] = L[r2.lb < L]
            r1.ub[r1.ub > U] = U[r1.ub > U]
            r2.ub[r2.ub > U] = U[r2.ub > U]
        
        r0.lb[r0.lb < L] = L[r0.lb < L]
        r0.ub[r0.ub > U] = U[r0.ub > U]
        
    # for more safety
    domain.useSave = True
    domain.useAsMutable = False
    domain.modificationVar = None 
    domain.storedIntervals.clear() # the dict
    
    return r, r0
    
def _iqg(Self, domain, dtype, r0):
    v = domain.modificationVar
    v_0 = domain[v]
    if isinstance(v_0, Stochastic):
        # TODO: modify it for non-fixed stochastic variables (dependend on oovar params)
        tmp = v._getFuncCalcEngine(domain)
        return tmp, tmp
    lb, ub = v_0#[0], v_0[1]

    if v.domain is not None and np.array_equal(lb, ub):
        # TODO: add tol parameter(s) for array_equal
        return r0,r0 
    
    if v.domain is None:
        middle1 = middle2 = 0.5 * (lb+ub)
    else:
        middle1, middle2 = splitDomainForDiscreteVariable(lb, ub, v)
        
    domain[v] = (lb, middle1)
    domain.localStoredIntervals = {}
    r_l = Self.interval(domain, dtype, resetStoredIntervals = False)

    domain[v] = (middle2, ub)
    domain.localStoredIntervals.clear()
    r_u = Self.interval(domain, dtype, resetStoredIntervals = False)
    
    domain[v] = v_0 # TODO: is it required yet?
    domain.localStoredIntervals.clear()
    return r_l, r_u
