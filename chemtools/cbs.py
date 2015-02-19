
'''rMmodule for Complete Basis Set Extrapolations.'''

import numpy as np

def uste(x, e_cbs, A3, method="CI"):

    '''CBS extrapolation using USTE shceme based on
    A. J. C. Varandas, JPCA 114, 8505-8516 (2010).'''

    # parameters calibrated for MRCI(Q)
    ci_params = {
        "A05" :  0.003769,
        "c"   : -1.1784771,
        "m"   : 1.25,
        "alpha" : -0.375}
    # parameters calibrated for CC
    cc_params = {
        "A05" :  0.1660699,
        "c"   : -1.4222512,
        "m"   : 1.0,
        "alpha" : -0.375}

    if method == "CI":
        dd = ci_params.copy()
    elif method == "CC":
        dd = cc_params.copy()

    A5 = dd["A05"] + c*math.pow(A3, dd["m"])

    v = e_cbs + A3/np.power(x+dd["alpha"], 3) +A5/np.power(x+dd["alpha"], 5)

    return v

def helgaker_X3(x, a, b):

    '''Inverse power extrapolation based on T. Helgaker et. al. JCP 106(23),
    9639 (1997).'''

    return a + b * np.power(x,-3)

def cbs_helgaker(x, Dinf, alpha, beta):

    '''Helgaker type extrapolationn to CBS with 3 parameters.'''

    return Dinf + alpha*np.power(x, -beta)

def scf_exp(x, e_cbs, b, a):
    '''
    CBS extrapolation by exponential Dunning-Feller relation.
    e^hf(x) = e_cbs + b*exp(-ax)
        x    : cardinal number of the basis set,
        b, c : empirical parameters.
    '''

    return e_cbs + b * np.exp(-a*x)

def scf_pol(x, e_cbs, b, a):
    '''
    CBS extrapolation by polynomial relation.
    e^hf(x) = e_cbs + b*x^(-a)
        x    : cardinal number of the basis set,
        b, c : empirical parameters.
    '''

    return e_cbs + b * np.power(x, -a)

