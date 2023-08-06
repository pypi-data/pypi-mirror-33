import os, sys
curr_dir = ''.join([elem + os.sep for elem in __file__.split(os.sep)[:-1]])
sys.path += [curr_dir]

__version__ = '0.5627'
_all = [__version__]

from ooVar import oovar, oovars
_all += [oovar, oovars]
#from ooFun import _getAllAttachedConstraints, broadcast, ooFun as oofun, AND, OR, NOT, NAND, NOR, XOR
from ooFun import oofun, fd_trace_id
_all += [oofun, fd_trace_id]

from ooSystem import ooSystem as oosystem
from translator import FuncDesignerTranslator as ootranslator
_all += [oosystem, ootranslator]

from ooPoint import ooPoint as oopoint, ooMultiPoint 
_all += [oopoint, ooMultiPoint]
from logic import AND, OR, XOR, NOT, EQUIVALENT, NAND, NOR, IMPLICATION
_all += [AND, OR, XOR, NOT, EQUIVALENT, NAND, NOR, IMPLICATION]
from baseClasses import Stochastic as _Stochastic
_all += [_Stochastic]
from FDmisc import FuncDesignerException, _getDiffVarsID, _getAllAttachedConstraints, broadcast
_all += [FuncDesignerException, _getDiffVarsID, _getAllAttachedConstraints, broadcast]
try:
    import distribution
    from distribution import P, mean, var, std
except ImportError:
    def sp_err(self, *args,  **kw): 
        raise FuncDesignerException('''
        to use FuncDesigner stochastic programming 
        you should have FuncDesigner with its stochastic module installed
        (this addon is commercial, free for research/educational small-scale problems only).
        Visit http://openopt.org/StochasticProgramming for more details.
        ''')
    class Distribution:
        __getattr__ = sp_err
    distribution = Distribution()
    P = mean = var = std = sp_err

_all += [P, mean, var, std]

from ooarray import ooarray
_all += [ooarray]
ifThen = IMPLICATION
_all += [ifThen]

from sle import sle
_all += [sle]
from ode import ode
_all += [ode]

from dae import dae
_all += [dae]

import overloads
_all += overloads.__all__

# custom imports from FuncDesigner don't work w/o this line
from overloads import *


from stencils import d, d2
_all += [d, d2]
#from overloads import _sum as sum
from interpolate import scipy_InterpolatedUnivariateSpline as interpolator
from integrate import integrator
_all += [interpolator, integrator]

isE = False
try:
    import enthought
    isE = True
    del(enthought)
except ImportError:
    pass
try:
    import envisage
    import mayavi
    isE = True
    del(envisage, mayavi)
except ImportError:
    pass
try:
    import xy
    isE = False
    del(xy)
except ImportError:
    pass
  
if isE:
    s = """
    Seems like you are using OpenOpt from 
    commercial Enthought Python Distribution;
    consider using free GPL-licensed alternatives
    PythonXY (http://www.pythonxy.com) or
    Sage (http://sagemath.org) instead.
    """
    print(s)
#    del(isE)
    
del(isE, curr_dir, os, sys)
