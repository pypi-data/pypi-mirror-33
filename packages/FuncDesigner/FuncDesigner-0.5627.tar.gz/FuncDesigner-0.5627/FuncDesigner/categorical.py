#PythonSum = sum
import numpy as np, copy

def categoricalAttribute(oof, attr):
    from ooFun import oofun
    L = len(oof.domain)
    if not hasattr(oof, 'aux_domain'):
        oof.aux_domain = copy.copy(oof.domain)
        ind_numeric = [j for j, elem in enumerate(oof.aux_domain[0]) if type(elem) not in (str, np.str_)]
        if len(ind_numeric):
            ind_first_numeric = ind_numeric[0]
            oof.aux_domain.sort(key = lambda elem: elem[ind_first_numeric])
        oof.domain = np.arange(len(oof.domain))
    ind = oof.fields.index(attr)
    
    # usually oof.aux_domain is python list or tuple
    dom = np.array([oof.aux_domain[j][ind] for j in range(L)])
    
    f = lambda x: dom[np.asarray(x, int) if type(x) == np.ndarray else int(x)]
    r = oofun(f, oof, engine = attr, vectorized = True, domain = dom)
    r._interval_ = lambda domain, dtype: categorical_interval(r, oof, domain, dtype)
    
    # ascending, descending, none
    r._sort_order = \
    'a' if np.all(dom[1:] >= dom[:-1]) \
    else 'd' if np.all(dom[1:] <= dom[:-1]) \
    else 'n'
    
    return r

def categorical_interval(r, oof, domain, dtype):
    l_ind, u_ind = np.asarray(domain[oof], int)
    s = l_ind.size
    variable_domain = r.domain
    if r._sort_order == 'a':
        vals = np.vstack((variable_domain[l_ind], variable_domain[u_ind]))
    elif r._sort_order == 'd':
        vals = np.vstack((variable_domain[u_ind], variable_domain[l_ind]))
    else:
        vals = np.zeros((2, s), dtype)
        U_ind = u_ind + 1 # not inplace for more safety
        # TODO: mb rework or remove the cycle (improve by vectorization if possible)
        for j in range(s):
            tmp = variable_domain[l_ind[j]:U_ind[j]]
            vals[0, j], vals[1, j] = tmp.min(), tmp.max()
    definiteRange = True
    return vals, definiteRange
