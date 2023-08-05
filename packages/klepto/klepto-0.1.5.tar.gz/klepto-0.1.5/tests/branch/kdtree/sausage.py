#! /usr/bin/env python
"""
... find the envelopes for graphical distance around a model

requires 2-D model, where one direction only has 3 discrete values
"""
verbose = False

def sausage_bounds(x, model, Y_bounds, **settings):
  y = model(list(x))
  from numpy import asarray
  pts = [1]*len(x)
  params = list(asarray(zip(pts,x)).flatten()) + [y]
  Y_lower, Y_upper = Y_bounds

  #APPLY THE SETTINGS OVERRIDES HERE#
  for k,v in settings.items():
    exec("%s = %s" % (str(k),repr(v))) #XXX: HACK

  from mystic.math.dirac_measure import scenario
  c = scenario()
  c.load(params, pts)
# x,y = _get_xy(c)
  ny = 1 #len(y)
  nx = len(params) - ny

  # original Y
  yo = asarray(c.values)

  from mystic.math.dirac_measure import impose_valid

  # fixed x values as bounds
  lower_bounds = [pi for pi in params]
  upper_bounds = [pi for pi in params[:nx]]
  # open bounds for y values
  upper_bounds += [Y_upper if b <= Y_upper else b for b in params[-ny:]]
  ubounds = lower_bounds, upper_bounds

  if verbose:
    print "ymax bounds:", asarray(ubounds).T[-1]

  # get maximum Y
  c.values = [Y_upper]*ny
  yu = impose_valid(Cy, model, guess=c, bounds=ubounds, xtol=Cx, hausdorff=hdn,\
                    tol=tol, maxiter=maxiter, imax=imax, ipop=ipop, npop=npop)

  # fixed x values as bounds
  upper_bounds = [pi for pi in params]
  lower_bounds = [pi for pi in params[:nx]]
  # open bounds for y values
  lower_bounds += [Y_lower if Y_lower <= b else b for b in params[-ny:]]
  lbounds = lower_bounds, upper_bounds

  if verbose:
    print "ymin bounds:", asarray(lbounds).T[-1]

  # get minimum Y
  c.values = [Y_lower]*ny
  yl = impose_valid(Cy, model, guess=c, bounds=lbounds, xtol=Cx, hausdorff=hdn,\
                    tol=tol, maxiter=maxiter, imax=imax, ipop=ipop, npop=npop)

  if verbose:
    print "orig:", yo
    print "ymax:", yu.values
    print "ymin:", yl.values

  # restore c to original
  c.values = yo

  # validity
  if verbose:
    from envelope import graphical_distance
    x,d = graphical_distance(model, yu, ytol=Cy, xtol=Cx, ipop=ipop, imax=imax, hausdorff=hdn, cutoff=0.0)
    print "\ndH+(Cy=%s,Cx=%s):" % (str(Cy),str(asarray(Cx))), d
    print "  at x:\n", x
    print "  and Y:\n", asarray([model(list(xi)) for xi in x])

    x,d = graphical_distance(model, yl, ytol=Cy, xtol=Cx, ipop=ipop, imax=imax, hausdorff=hdn, cutoff=0.0)
    print "\ndH-(Cy=%s,Cx=%s):" % (str(Cy),str(asarray(Cx))), d
    print "  at x:\n", x
    print "  and Y:\n", asarray([model(list(xi)) for xi in x])

  return yl.values, yo, yu.values

def sausage_queue(bounds, gridsize):
  "build a queue of all desired combinations of 3-D x's"
  lower_bounds, upper_bounds = bounds
  h_lower, v_lower, a_lower = lower_bounds
  h_upper, v_upper, a_upper = upper_bounds

  # build a mgrid for the first two x dimensions
  gridsize = eval('%sj' % gridsize)
  from numpy import vstack, hstack, mgrid, ones
  grid2d = mgrid[h_lower:h_upper:gridsize, v_lower:v_upper:gridsize]
 
  # produce an array of x values
  runs = hstack([grid2d[:,i,:] for i in range(grid2d.shape[1])]).T
  # add a column for the fixed values
  alpha = 0.0
  runs = vstack([runs.T, alpha*ones(runs.shape[0])]).T
  return runs

from memoize import memoized0_nopickle_round as memoized
# vectorize 'sausage_bounds' to find min/max for every evaluation point
@memoized(tol=3)
def model_sausage(x):
  "find the boundary of the sausage in Y for the given x"
  from sausage import sausage_bounds
  from runinfo import model, Y_bounds, settings
  ymin, yo, ymax = sausage_bounds(x, model, Y_bounds, **settings)
  from numpy import array
  return array([ymin, yo, ymax]).flatten()



if __name__ == '__main__':

  from runinfo import Y_bounds, model, settings
  from numpy import array

  #   [ h    v    a ]
# x = [3.0, 6.0, 0.0]
  _x = array(
       [[0.5, 4.5, 0.0],
        [0.5, 7.0, 0.0],
        [3.0, 4.5, 0.0],
        [3.0, 7.0, 0.0],
	[1.5, 6.0, 0.0],
	[0.8, 5.0, 0.0],
	[1.0, 5.5, 0.0]])
  x = _x[-1]

  # find the boundary of the sausage in Y for the given x
  ymin, yo, ymax = sausage_bounds(x, model, Y_bounds, **settings)
  if not verbose: print ymin, yo, ymax


# EOF
