#! /usr/bin/env python
"""
... find the envelopes for graphical distance around a model

requires 2-D model, where one direction only has 3 discrete values
"""
from __future__ import with_statement
import dill as pickle
#try:
#  import simplejson as pickle
# #import json as pickle
#except ImportError:
#  pass

debug = False

from mystic.math.paramtrans import infeasibility, _get_xy

def graphical_distance(model, points, **kwds):
  """find the radius(x') that minimizes the graph between reality, y = G(x),
and an approximating function, y' = F(x')

Inputs:
  model = the model function, y' = F(x'), that approximates reality, y = G(x)
  points = object of type 'datapoint' to validate against; defines y = G(x)

Additional Inputs:
  ytol = maximum acceptable difference |y - F(x')|; a single value
  xtol = maximum acceptable difference |x - x'|; an iterable or single value
  cutoff = zero out distances less than cutoff; typically: ytol, 0.0, or None
  hausdorff = norm; where if given, ytol = |y - F(x')| + |x - x'|/norm

Returns:
  radius = minimum distance from x,G(x) to x',F(x') for each x

Notes:
  xtol defines the n-dimensional base of a pilar of height ytol, centered at
  each point. The region inside the pilar defines the space where a "valid"
  model must intersect. If xtol is not specified, then the base of the pilar
  will be a dirac at x' = x. This function performs an optimization for each
  x to find an appropriate x'. While cutoff and ytol are very tightly related,
  they play a distinct role; ytol is used to set the optimization termination
  for an acceptable |y - F(x')|, while cutoff is applied post-optimization.
  If we are using the hausdorff norm, then ytol will set the optimization
  termination for an acceptable |y - F(x')| + |x - x'|/norm, where the x
  values are normalized by norm = hausdorff.
""" #FIXME: update docs to show normalization in y
 #NotImplemented:
 #L = list of lipschitz constants, for use when lipschitz metric is desired
 #constraints = constraints function for finding minimum distance
  from mystic.math.legacydata import dataset
  from numpy import asarray, sum, isfinite, zeros, seterr
  from mystic.solvers import diffev2, fmin_powell
  from mystic.monitors import Monitor, VerboseMonitor

  # ensure target xe and ye is a dataset
  target = dataset()
  target.load(*_get_xy(points))
  nyi = target.npts             # y's are target.values
  nxi = len(target.coords[-1])  # nxi = len(x) / len(y)
  
  # NOTE: the constraints function is a function over a single xe,ye
  #       because each underlying optimization is over a single xe,ye.
  #       thus, we 'pass' on using constraints at this time...
  constraints = None   # default is no constraints
  if kwds.has_key('constraints'): constraints = kwds.pop('constraints')
  if not constraints:  # if None (default), there are no constraints
    constraints = lambda x: x

  # get tolerance in y and wiggle room in x
  ytol = kwds.pop('ytol', 0.0)
  xtol = kwds.pop('xtol', 0.0) # default is to not allow 'wiggle room' in x 

  cutoff = ytol  # default is to zero out distances less than tolerance
  if kwds.has_key('cutoff'): cutoff = kwds.pop('cutoff')
  if cutoff is True: cutoff = ytol
  elif cutoff is False: cutoff = None
  ipop = kwds.pop('ipop', min(20, 3*nxi)) #XXX: tune ipop?
  imax = kwds.pop('imax', 1000) #XXX: tune imax?

  # get range for the dataset (normalization for hausdorff distance)
  hausdorff = kwds.pop('hausdorff', False)
  if not hausdorff:  # False, (), None, ...
    ptp = [0.0]*nxi
    yptp = 1.0
  elif hausdorff is True:
    from mystic.math.measures import spread
    ptp = [spread(xi) for xi in zip(*target.coords)]
    yptp = spread(target.values)
  else:
    try: #iterables
      if len(hausdorff) < nxi+1:
        hausdorff = list(hausdorff) + [0.0]*(nxi - len(hausdorff)) + [1.0]
      ptp = hausdorff[:-1]  # all the x
      yptp = hausdorff[-1]  # just the y
    except TypeError: #non-iterables
      ptp = [hausdorff]*nxi
      yptp = hausdorff

  #########################################################################
  def radius(model, point, ytol=0.0, xtol=0.0, ipop=None, imax=None):
    """graphical distance between a single point x,y and a model F(x')"""
    # given a single point x,y: find the radius = |y - F(x')| + delta
    # radius is just a minimization over x' of |y - F(x')| + delta
    # where we apply a constraints function (of box constraints) of
    # |x - x'| <= xtol  (for each i in x)
    #
    # if hausdorff = some iterable, delta = |x - x'|/hausdorff
    # if hausdorff = True, delta = |x - x'|/spread(x); using the dataset range
    # if hausdorff = False, delta = 0.0
    #
    # if ipop, then DE else Powell; ytol is used in VTR(ytol)
    # and will terminate when cost <= ytol
    x,y = _get_xy(point)
    y = asarray(y)

    # build the cost function
    if hausdorff: # distance in all directions
      def cost(rv):
        '''cost = |y - F(x')| + |x - x'| for each x,y (point in dataset)'''
        errs = seterr(invalid='ignore', divide='ignore') # turn off warning 
        z = abs((asarray(x) - rv)/ptp)  # normalize by range
        m = abs(y - model(rv))/yptp     # normalize by range
        m = m if isfinite(m) else 10.0**6
        seterr(invalid=errs['invalid'], divide=errs['divide']) # turn on warning
        return m + sum(z[isfinite(z)])
    else:  # vertical distance only
      def cost(rv):
        '''cost = |y - F(x')| for each x,y (point in dataset)'''
        return abs(y - model(rv))

    if debug:
      print "rv: %s" % str(x)
      print "cost: %s" % cost(x)

    # if xtol=0, radius is difference in x,y and x,F(x); skip the optimization
    try:
      if not imax or not max(xtol): #iterables
        return x, cost(x)
    except TypeError:
      if not xtol: #non-iterables
        return x, cost(x)

    # set the range constraints
    xtol = asarray(xtol)
    bounds = zip( x - xtol, x + xtol )

    if debug:
      print "lower: %s" % str(zip(*bounds)[0])
      print "upper: %s" % str(zip(*bounds)[1])

    # optimize where initially x' = x
    stepmon = Monitor()
    if debug: stepmon = VerboseMonitor(1)
    #XXX: edit settings?
    MINMAX = 1 #XXX: confirm MINMAX=1 is minimization
    if ipop: # use VTR
      results = diffev2(cost, bounds, ipop, ftol=ytol, gtol=None, \
                        itermon = stepmon, maxiter=imax, bounds=bounds, \
                        full_output=1, disp=0, handler=False)
    else: # use VTR
      results = fmin_powell(cost, x, ftol=ytol, gtol=None, \
                            itermon = stepmon, maxiter=imax, bounds=bounds, \
                            full_output=1, disp=0, handler=False)
   #solved = results[0]            # x'
    func_opt = MINMAX * results[1] # cost(x')
    if debug:
      print "solved: %s" % results[0]
      print "cost: %s" % func_opt

    # get the minimum distance |y - F(x')|
    return results[0], func_opt
  #########################################################################

  #XXX: better to do a single optimization rather than for each point ???
  _d = [radius(model, point, ytol, xtol, ipop, imax) for point in target]
  r,d = zip(*_d)
  return asarray(r),infeasibility(d, cutoff)


def np_map(func, x): # *args
  "numpy map function"
  from numpy import vectorize
  vfunc = vectorize(func)
  return vfunc(x) # array of *args


def read_results(oldresults):
  try:
    with open(oldresults, 'rb') as file:
      memo = pickle.load(file)
  except:
    memo = {}
  return memo


def write_results(memo, newresults):
  with open(newresults, 'wb') as file:
    pickle.dump(memo, file)
  return


#def model_sausage(x):
#  from sausage import model_sausage
#  return model_sausage(x)

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

  verbose = True #False
  oldresults = "cache.pkl"
  newresults = "cache.pkl"

  # get the run settings
  from runinfo import bounds, gridsize

  # get a queue of points to evaluate at
  from sausage import sausage_queue
  runs = sausage_queue(bounds, gridsize)
  if verbose: print "h v i:\n", runs

  # read any existing runs and results from archive
  model_sausage.memo.update(read_results(oldresults))
    
  # do a map of model_sausage over the runs
  # with 'serial' python
# results = map(model_sausage, runs)
  # with numpy
# results = np_map(model_sausage, runs)
  # with multiprocessing 
  from pathos.mp_map import mp_map as map  # multiprocessing
  results = map(model_sausage, runs)#, nproc=nodes)
  # with MPI
# nodes = 4 #len(runs)
# from pyina.ez_map import ez_map2 as map  # mpi4py
# results = map(model_sausage, runs, nnodes=nodes)
  # with MPI on a cluster
# nodes = '25:ppn=2'
# queue = 'weekdayQ'
# timelimit = '11:59:59'
# from pyina.ez_map import ez_map2 as map  # mpi4py
# from pyina.launchers import mpirun_launcher, torque_launcher
# from pyina.mappers import carddealer_mapper, equalportion_mapper
# from pyina.schedulers import torque_scheduler
# results = map(model_sausage, runs, nnodes=nodes, queue=queue, \
#               timelimit=timelimit, launcher=mpirun_launcher, \
#               scheduler=torque_scheduler)

  from numpy import asarray
  if verbose: print "yl yo yu:\n", asarray(results)

  # save the runs and results for later use
  write_results(model_sausage.memo, newresults)

### using tuples not arrays
##[memo.update({tuple(xi):tuple(yi)}) for (xi,yi) in zip(runs, results)]

  # check validity of results
  if verbose:
    assert model_sausage.memo == read_results(newresults)

  # linear interpolation to get envelope functions [6 func = 3 hi * 2 bounds]

  # apply envelopes as constraints to y




# EOF
