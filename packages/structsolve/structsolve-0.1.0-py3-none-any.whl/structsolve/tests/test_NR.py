import numpy as np
from scipy.sparse import csr_matrix

from structsolve import Analysis

def calc_fext(**kwargs):
    return np.array([0.]) # aiming to find roots

def calc_fint(c=1., **kwargs):
    if not isinstance(c, float):
        c = c[0]
    print('DEBUG', c)
    return csr_matrix(np.array([[2.*c**3]]))

def calc_kC(c=1., **kwargs):
    if not isinstance(c, float):
        c = c[0]
    return csr_matrix(np.array([[6.*c**2]]))

def calc_kG(**kwargs):
    return csr_matrix(np.array([[0.]]))


an = Analysis(calc_fext, calc_fint, calc_kC, calc_kG)
an.static(NLgeom=True)
