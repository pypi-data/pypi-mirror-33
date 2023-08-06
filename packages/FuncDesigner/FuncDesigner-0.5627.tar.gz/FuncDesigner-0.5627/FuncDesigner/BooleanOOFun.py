from numpy import asanyarray, int8#, logical_xor, logical_not
from ooFun import oofun
from logic import AND, EQUIVALENT, NOT, XOR, OR#, nlh_not
from FDmisc import FuncDesignerException

class BooleanOOFun(oofun):
    # an oofun that returns True/False
#    _unnamedBooleanOOFunNumber = 0
    discrete = True
    isBoolean = True
#    mb lh implementation - a func that is overwritten in some cases
    def __init__(self, func, _input, *args, **kwargs):
        oofun.__init__(self, func, _input, *args, **kwargs)
        #self.input = oofun_Involved.input
#        BooleanOOFun._unnamedBooleanOOFunNumber += 1
        #self.name = 'unnamed_boolean_oofun_id_' + str(BooleanOOFun._unnamedBooleanOOFunNumber)
        self.name = 'unnamed_boolean_oofun_id_' + str(oofun._id)
        self.oofun = oofun(lambda *args, **kw: asanyarray(func(*args, **kw), int8), _input, vectorized = True)
        # TODO: THIS SHOULD BE USED IN UP-LEVEL ONLY
        self.lb = self.ub = 1
    
    __hash__ = oofun.__hash__
    
    def size(self, *args, **kwargs): 
        raise FuncDesignerException('currently BooleanOOFun.size() is disabled')
    def D(self, *args, **kwargs): 
        raise FuncDesignerException('currently BooleanOOFun.D() is disabled')
    def _D(self, *args, **kwargs): 
        raise FuncDesignerException('currently BooleanOOFun._D() is disabled')
    
    def nlh(self, *args, **kw):
        raise FuncDesignerException('This is virtual method to be overloaded in derived class instance')
    
    __and__ = AND
    
    #IMPLICATION = IMPLICATION
    __eq__ = EQUIVALENT
    __ne__ = lambda self, arg: NOT((self==arg)(tol=0.5))# TODO: check is tol used? & mb rework it
    
    __or__ = OR
    __invert__ = NOT
    __xor__ = XOR
    
