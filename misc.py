"""
DxTools: Processing XRD data files recorded with the Bruker D8 diffractometer
Copyright 2016, Alexandre  Boulle
alexandre.boulle@unilim.fr
"""
from numpy import log, exp, max, where, abs, arange, pi, sqrt, random, array
from scipy.optimize import  leastsq

def pVoigt(x, p):
    maximum = p[0]
    pos = p[1]
    FWHM = p[2]
    eta = p[3]
    a = p[4]
    b = p[5]
    gauss = maximum * exp(-log(2.) * ((x-pos)/(0.5*FWHM))**2)
    lorentz = maximum / (1. + ((x - pos)/(0.5*FWHM))**2)
    return eta*lorentz + (1-eta)*gauss + a*x + b

def guess_param(x,y):
    a = 0
    b = y.min()
    maximum = y.max()
    pos = x[y==maximum][0]
    d=y-(maximum/2.) - b/2.
    indexes = where(d > 0)[0]
    FWHM = abs(x[indexes[-1]] - x[indexes[0]])
    eta = 0.5
    return array([maximum-b, pos, FWHM, eta, a, b])

def pVoigt_area(p):
    maximum = p[0]
    FWHM = p[2]
    eta = p[3]
    beta = (eta*pi*FWHM/2.) + (1-eta)*(FWHM/2.)*sqrt(pi/log(2))
    return beta*maximum

def pVfit_param(x,y):
    errfunc = lambda p, x, y: (pVoigt(x, p) - y)#/(y**0.5)
    p0 = guess_param(x,y)
    p1 = leastsq(errfunc, p0[:], args=(x, y))[0]
    return p1
