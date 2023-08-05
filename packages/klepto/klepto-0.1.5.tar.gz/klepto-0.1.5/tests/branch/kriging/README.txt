http://stackoverflow.com/questions/24804298/fit-a-non-linear-function-to-data-observations-with-pymcmc-pymc

http://scikit-learn.org/stable/modules/gaussian_process.html

and http://stackoverflow.com/a/24983256/4646678



What is a sensible solution largely depends on what questions you're trying to answer with the interpolated pixels -- caveat emptor: extrapolating over missing data can lead to very misleading answers!

Radial Basis Function Interpolation / Kernel Smoothing

In terms of practical solutions available in Python, one way to fill those pixels in would be to use Scipy's implementation of Radial Basis Function interpolation (see here) which is intended for the smoothing/interpolation of scattered data.

Given your matrix M and underlying 1D coordinate arrays r and c (such that M.shape == (r.size, c.size)), where missing entries of M are set to nan, this seems to work fairly well with a linear RBF kernel as follows:



import numpy as np
import scipy.interpolate as interpolate

with open('measurement.txt') as fh:
    M = np.vstack(map(float, r.split(' ')) for r in fh.read().splitlines())
r = np.linspace(0, 1, M.shape[0]) 
c = np.linspace(0, 1, M.shape[1])

rr, cc = np.meshgrid(r, c)
vals = ~np.isnan(M)
f = interpolate.Rbf(rr[vals], cc[vals], M[vals], function='linear')
interpolated = f(rr, cc)




from sklearn.gaussian_process import GaussianProcess

gp = GaussianProcess(theta0=0.1, thetaL=.001, thetaU=1., nugget=0.01)
gp.fit(X=np.column_stack([rr[vals],cc[vals]]), y=M[vals])
rr_cc_as_cols = np.column_stack([rr.flatten(), cc.flatten()])
interpolated = gp.predict(rr_cc_as_cols).reshape(M.shape)


