"""
DxTools: Processing XRD data files recorded with the Bruker D8 diffractometer
Copyright 2016, Alexandre  Boulle
alexandre.boulle@unilim.fr
"""
from numpy import log, exp, max, where, abs, arange, pi, sqrt, random, array, inf, diag
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

def pVoigt_area_err(p, perr):
    maximum = p[0]
    dmax = perr[0]
    FWHM = p[2]
    dFWHM = perr[2]
    eta = p[3]
    deta = perr[3]

    dbeta2 = ((eta*pi*dFWHM/2.)**2) + ((deta*pi*FWHM/2.)**2) + (((1-eta)*(dFWHM/2.)*sqrt(pi/log(2)))**2) + ((deta*(FWHM/2.)*sqrt(pi/log(2)))**2)

    beta = (eta*pi*FWHM/2.) + (1-eta)*(FWHM/2.)*sqrt(pi/log(2))
    area = beta*maximum
    err_area = area*sqrt((dmax/maximum)**2 + (dbeta2/(beta**2)))

    return err_area

def pVfit_param(x,y):
    errfunc = lambda p, x, y: (pVoigt(x, p) - y)#/(y**0.5)
    p0 = guess_param(x,y)
    p1 = leastsq(errfunc, p0[:], args=(x, y))[0]
    return p1

def pVfit_param_err(x,y):
    errfunc = lambda p, x, y: (pVoigt(x, p) - y)#/(y**0.5)
    p0 = guess_param(x,y)
    p1, pcov, infodict, errmsg, success = leastsq(errfunc, p0[:], args=(x, y), full_output=1)

    #compute esd from fit
    if (len(y) > len(p0)) and pcov is not None:
        s_sq = (errfunc(p1, x, y)**2).sum()/(len(y)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    error = []
    for i in range(len(p1)):
        try:
          error.append(abs(pcov[i,i])**0.5)
        except:
          error.append( 0.00 )

    return p1, error