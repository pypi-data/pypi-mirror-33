# Handling of FuncDesigner probs

from numpy import hstack, atleast_1d, cumsum, asfarray, asarray, zeros, \
ndarray, prod, nan, array_equal, copy, array, flatnonzero
import numpy as np
#from nonOptMisc import scipyInstalled, isspmatrix, SparseMatrixConstructor#, DenseMatrixConstructor

from FDmisc import FuncDesignerException, SparseMatrixConstructor, scipyInstalled, isspmatrix, \
Hstack, Find
from ooPoint import ooPoint
DenseMatrixConstructor = np.zeros
#isspmatrix = lambda *args: False

try:
    # available since numpy 1.6.x
    from numpy import count_nonzero
except:
    count_nonzero = lambda elem: len(flatnonzero(asarray(elem)))

def pointDerivative2array(S, pointDerivative,  **kw): 
    useSparse = kw.get('useSparse', S.useSparse) # useSparse can be True, False, 'auto'
    # TODO: print warning of involving dense for sparse cases
    func = kw.get('func', None)
    point= kw.get('point', None)

    #TODO: move it outside the func
    if not scipyInstalled and useSparse == 'auto':
        useSparse = False
    if useSparse is True and not scipyInstalled:
        raise FuncDesignerException('to handle sparse matrices you should have module scipy installed') 
    ######################################################
    
    oovarsIndDict = S.oovarsIndDict
    n = S.n
    
    if len(pointDerivative) == 0: 
        if func is not None:
            # TODO: mb take funcLen from other source
            funcLen = func(point).size
            if useSparse is not False:
                return SparseMatrixConstructor((funcLen, n))
            else:
                return DenseMatrixConstructor((funcLen, n))
        else:
            raise FuncDesignerException('unclear error, maybe you have function|constraint independend on any optimization variables') 

    Items = pointDerivative.items()
    key, val = Items[0] if type(Items) == list else next(iter(Items))
    var_inds = oovarsIndDict[key]
    
    # val.size works in other way (as nnz) for scipy.sparse matrices
    funcLen = int(prod((val if isspmatrix(val) else atleast_1d(val)).shape) / (var_inds[1] - var_inds[0]))
    
    if useSparse == 'auto':
        # Calculate number of zero/nonzero elements
        nTotal = n * funcLen#sum([prod(elem.shape) for elem in pointDerivative.values()])
        nNonZero = sum((elem.size if isspmatrix(elem) else count_nonzero(elem)) for elem in pointDerivative.values())
        involveSparse = 4*nNonZero < nTotal and nTotal > 1000
    else:
        involveSparse = useSparse
        
    if involveSparse:
        r2 = []
        if funcLen == 1:
            inds = []
            for oov, val in pointDerivative.items():
                ind_start, ind_end = oovarsIndDict[oov]
                
                # works faster than isscalar()
                if type(val) in (float, np.float64)\
                or np.isscalar(val):
                    r2.append(val)
                    inds.append(ind_start)
                elif type(val) in (np.ndarray, np.matrix):
                    Val = (val if type(val) == ndarray else val.A).flatten()
                    Ind = np.where(Val)[0]
                    r2 += Val[Ind].tolist()
                    inds += (ind_start+Ind).tolist()
                elif isspmatrix(val):
                    I, J, vals = Find(val)
                    r2 += vals.tolist()
                    inds += (ind_start+J).tolist()

            from scipy.sparse import coo_matrix
            r3 = coo_matrix((r2, ([0]*len(r2), inds)), shape=(funcLen, n))
        else:
            # USE STACK
            ind_Z = 0
            derivative_items = list(pointDerivative.items())
            derivative_items.sort(key=lambda elem: elem[0]._id)
            for oov, val in derivative_items:#pointDerivative.items():
                ind_start, ind_end = oovarsIndDict[oov]
                if ind_start != ind_Z:
                    r2.append(SparseMatrixConstructor((funcLen, ind_start - ind_Z)))
                if not isspmatrix(val): 
                    val = asarray(val) # else bug with scipy sparse hstack
                r2.append(val)
                ind_Z = ind_end
            if ind_Z != n:
                # assert ind_Z < n
                r2.append(SparseMatrixConstructor((funcLen, n - ind_Z)))
            r3 = Hstack(r2) 
            #if isspmatrix(r3) and 4 * r3.nnz > asarray(r3.shape, int64).prod(): r3 = r3.A
        return r3
    else:
        # USE INSERT
        if funcLen == 1:
            r = DenseMatrixConstructor(n)
        else:
            r = SparseMatrixConstructor((funcLen, n)) if involveSparse else DenseMatrixConstructor((funcLen, n)) 
        
        for key, val in pointDerivative.items():
            indexes = oovarsIndDict[key]
            if not involveSparse and isspmatrix(val): val = val.A
            if r.ndim == 1:
                r[indexes[0]:indexes[1]] = val.flatten() if type(val) == ndarray else val
            else:
                r[:, indexes[0]:indexes[1]] = val if val.shape == r.shape else val.reshape((funcLen, prod(val.shape)/funcLen))
        # TODO: mb remove it
        if useSparse is True and funcLen == 1: 
            return SparseMatrixConstructor(r)
        elif r.ndim <= 1:
            r = r.reshape(1, -1)
        if useSparse is False and hasattr(r, 'toarray'):
            r = r.toarray()
        return r

point2vector = lambda S, point: \
asfarray(atleast_1d(hstack([(point[v] if v in point else zeros(S._shapeDict[v])) for v in S._variables])))

def vector2point(S, x):
    isComplexArray = isinstance(x, ndarray) and str(x.dtype).startswith('complex')
    
    x = atleast_1d(array(x, copy=True) if isComplexArray else array(x, copy=True, dtype=float))

    if array_equal(x, S._SavedValues['prevX']):
        return S._SavedValues['prevVal']
    
    # without copy() ipopt and probably others can replace it by noise after closing
    kw = {'skipArrayCast':True} if isComplexArray else {}
    r = ooPoint(((v, x[S.oovar_indexes[i]:S.oovar_indexes[i+1]]) for i, v in enumerate(S._variables)), **kw)
    
    S._SavedValues['prevVal'] = r
    S._SavedValues['prevX'] = copy(x)
    return r
    
class FuncDesignerTranslator:
#    freeVars = []
#    fixedVars = []
    def __init__(self, PointOrVariables, **kwargs): #, freeVars=None, fixedVars=None
        #assert freeVars is not None or fixedVars is not None, 'at most one parameter of "fixedVars" and "freeVars" is allowed'
        #assert 'freeVars' not in kwargs, 'only "fixedVars" and "freeVars" arguments are allowed, not "freeVars"'
        
        self.useSparse = kwargs.get('useSparse', False)
        if isinstance(PointOrVariables, dict):
            Point = PointOrVariables
            Variables = list(Point.keys())
            self._sizeDict = dict((v, asarray(PointOrVariables[v]).size) for v in PointOrVariables)
            self._shapeDict = dict((v, asarray(PointOrVariables[v]).shape) for v in PointOrVariables)
            # TODO: assert v.size (if provided) == PointOrVariables[v]).size
            # and same with shapes
        else:
            assert type(PointOrVariables) in (list, tuple)
            Variables = PointOrVariables
            self._sizeDict = dict((v, (v.size if hasattr(v, 'size') and isinstance(v.size, int) else 1)) for v in Variables)
            self._shapeDict = dict((v, (v.shape if hasattr(v, 'shape') else ())) for v in Variables)
            
        self._variables = Variables
        self.n = sum(self._sizeDict.values())
        
        oovar_sizes = list(self._sizeDict.values()) # FD: for opt oovars only
        self.oovar_indexes = oovar_indexes = cumsum([0] + oovar_sizes)

        self.oovarsIndDict = dict((v, (oovar_indexes[i], oovar_indexes[i+1])) for i, v in enumerate(Variables))
        
        # TODO: mb use oovarsIndDict here as well (as for derivatives?)
        
        #startDictData = [] #if fixedVars is None else [(v, startPoint[v]) for v in fixedVars]
        # TODO: involve fixed variables
        self._SavedValues = {'prevX':nan}

    
    vector2point = vector2point

    point2vector = point2vector
    
    pointDerivative2array = pointDerivative2array#lambda *arg, **kw:
    
