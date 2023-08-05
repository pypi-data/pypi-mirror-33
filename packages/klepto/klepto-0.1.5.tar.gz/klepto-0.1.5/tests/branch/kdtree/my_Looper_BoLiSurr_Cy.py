#!/usr/bin/env python
"""
OUQ with model sausage: valid_wrt_model, mean(y), norm(wts)
  with 'wiggle room' around the model in Y
"""

hausdorff = (1.0, 1.0, 1.0, 1.0) # spread(x) where x = h,v,a,Y
cde = 20 #NOTE: int is DE(cde), 0 is powell(); used in graphical_distance
ide = 10 #NOTE: int is DE(ide), 0 is powell(); used in graphical_distance
debug = False
MINMAX = -1  ## NOTE: sup = maximize = -1; inf = minimize = 1
from mystic.math.measures import mean
#######################################################################
# optimizer configuration parameters
#######################################################################
npop = 20 #16 #32 # 40 #50  #!!!
maxiter = 1000
maxfun = 1e+6
convergence_tol = 1e-6; ngen = 40 #20  #!!!
smearing = 0.001
crossover = 0.9
percent_change = 0.9

# MPI
nodes = '25:ppn=2' # using mp_map in solver, means 4 processor per (Cy,theta)
queue = 'weekdayQ'
timelimit = '11:59:59'


#######################################################################
# the model function
#######################################################################
#from otm_hvi import eureka as model
from otm_hvi_new import eureka as model


#######################################################################
# the differential evolution optimizer
#######################################################################
def optimize(cost,_bounds,_constraints,initial=None,job='',stepmon=None):
  from mystic.solvers import DifferentialEvolutionSolver2
  from mystic.termination import ChangeOverGeneration as COG
  from mystic.strategy import Best1Exp
  from mystic.monitors import Null #, Monitor
 #from mystic.tools import random_seed
 #random_seed(123)

  if stepmon is None:
    logfile = 'paramlog'
    stamp = "_".join([logfile, str(job)])
    from mystic.monitors import VerboseLoggingMonitor #, LoggingMonitor
    stepmon = VerboseLoggingMonitor(1,10,filename=stamp+'.txt',info=stamp)
# evalmon = Monitor()
  evalmon = Null()

  lb,ub = _bounds
  ndim = len(lb)

  solver = DifferentialEvolutionSolver2(ndim,npop)
  if initial:
    solver.SetInitialPoints(initial,radius=smearing)
  else:
    solver.SetRandomInitialPoints(min=lb,max=ub)
 #ALTERNATE: initial population
 #solver.SetRandomInitialPoints(min=lb,max=ub)
 #if initial:
 #  solver.population[0] = initial 
  solver.SetStrictRanges(min=lb,max=ub)
  solver.SetEvaluationLimits(maxiter,maxfun)
  solver.SetEvaluationMonitor(evalmon)
  solver.SetGenerationMonitor(stepmon)
  solver.SetConstraints(_constraints)
 #ALTERNATE: multiprocessing map of cost function
##from pathos.mp_map import mp_map as map  # multiprocessing
##solver.SetMapper(map)
 #ALTERNATE: MPI map of cost function
##from pyina.ez_map import ez_map2 as map  # mpi4py
##from pyina.launchers import mpirun_launcher, torque_launcher
##from pyina.mappers import carddealer_mapper, equalportion_mapper
##from pyina.schedulers import torque_scheduler
##solver.SetMapper(map, equalportion_mapper)
##solver.SetLauncher(mpirun_launcher, nodes)
##solver.SelectScheduler(torque_scheduler, queue, timelimit)
  tol = convergence_tol
  solver.Solve(cost,termination=COG(tol,ngen),strategy=Best1Exp, \
               CrossProbability=crossover,ScalingFactor=percent_change)

  solved = solver.bestSolution
 #print "solved: %s" % solver.Solution()
  func_max = MINMAX * solver.bestEnergy       #NOTE: -solution assumes -Max
 #func_max = 1.0 + MINMAX*solver.bestEnergy   #NOTE: 1-sol => 1-success = fail
  func_evals = solver.evaluations
 #from mystic.munge import write_support_file
 #write_support_file(stepmon, log_file=stamp+'.py', header=stamp)#, npts=npts)
  return solved, func_max, func_evals


#######################################################################
# maximize the function
#######################################################################
def maximize(params,npts,bounds,initial=None,job='',printmon=None):

  from my_dirac_measure import scenario
  from numpy import inf
  target,error = params
  lb,ub = bounds

  # NOTE: rv, lb, ub are of the form:
  #    rv = [wxi]*nx + [xi]*nx + [wyi]*ny + [yi]*ny + [wzi]*nz + [zi]*nz
  #       +  [Yi]*nY

  # generate secondary constraints function
  def more_constraints(rv):
    ##################### begin function-specific #####################
    ###################### end function-specific ######################
    return rv

# from memoize import memoized0_nopickle_round as memoized

  # generate primary constraints function
# @memoized(tol=3)
  def constraints(rv):
    rrv = range(len(rv))
    for i in rrv:
      rv[i] = min(max(rv[i], lb[i]), ub[i])
    # impose range constraints: first try bounce-back to maintain randomness
#   rv = [2*lb[i]-rv[i] if max(rv[i], lb[i]) == lb[i] else rv[i] for i in rrv]
#   rv = [2*ub[i]-rv[i] if min(rv[i], ub[i]) == ub[i] else rv[i] for i in rrv]
    # if bounceback fails, then use a hard cutoff  #FIXME: breaks randomness
#   rv = [max(rv[i], lb[i]) for i in rrv]
#   rv = [min(rv[i], ub[i]) for i in rrv]

    c = scenario()
    c.load(rv, npts)

    # ensure norm(wi) = 1.0 in each discrete measure
    norm = 1.0
    for i in range(len(c)):
      w = c[i].weights
      w[-1] = norm - sum(w[:-1])
      c[i].weights = w

    ##################### begin function-specific #####################
    # impose mean on the values of the product measure
    from mystic.math.dirac_measure import mean_y_norm_wts_constraintsFactory as factory
    constrain = factory((target[0],error[0]), npts)

    # check mean value, and if necessary use constrain to set mean value
    y = float(mean(c.values, c.weights))
    if not (y >= float(target[0] - error[0])):
      c.update( constrain( c.flatten(all=True) ) )

    # then test if valid... then impose model validity on product measure
    if not c.valid_wrt_model(model, ytol=target[2], xtol=target[3], \
                             imax=target[4], ipop=cde, hausdorff=hausdorff):
      c.set_valid(model, cutoff=target[2], bounds=bounds, tol=error[2], \
                  constraints=constrain, xtol=target[3], maxiter=error[3], \
                  imax=error[4], ipop=ide, hausdorff=hausdorff)
    ###################### more function-specific #####################
    if debug:
      if not c.valid_wrt_model(model, ytol=target[2], xtol=target[3], \
                               imax=target[4], ipop=cde, hausdorff=hausdorff):
        print "valid_wrt_model: False"
      if not [sum(w) for w in c.wts] == [1.0] * len(c.wts):
        print "norm(w) == 1.0: False"
      if not c.get_mean_value() >= float(target[0] - error[0]):
        print "mean(y) >= %s: False" % str(target[0] - error[0])
    ###################### end function-specific ######################
    # extract weights and positions and values
    return c.flatten(all=True)

  # generate a function that returns True for 'success' and False for 'failure'
  def safe(f):
    y = f - target[1]  #XXX: thus... if [f - theta] <= 0: then 'failure'
    return 0.0 if y <= 0.0 else y

  # generate maximizing function
  def cost(rv):
    c = scenario()
    c.load(rv, npts)
    #XXX: apply 'filters' to catch errors in constraints solver (necessary ?)
    ##################### begin function-specific #####################
    y = float(mean(c.values, c.weights))
    if not (y >= float(target[0] - error[0])):
      if debug: print "skipping mean: %s" % y
      return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS

    if not c.valid_wrt_model(model, ytol=target[2], xtol=target[3], \
                             imax=target[4], ipop=cde, hausdorff=hausdorff):
      if debug: print "skipping model-invalidity"
      return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS
    ###################### end function-specific ######################
    return MINMAX * c.pof_value(safe)

  # maximize
  solved, func_max, func_evals = optimize(cost,(lb,ub),constraints, \
                                          initial,job,printmon)

  # clear the cache
# constraints.memo.clear()

  if MINMAX == 1:
    tag = 'minimum' # inf
  else:
    tag = 'maximum' # sup
  if printmon:
    printmon.info("func_%s: %s" % (tag,func_max))
    printmon.info("func_evals: %s" % func_evals)
  else:
    print "func_%s: %s" % (tag,func_max)
    print "func_evals: %s" % func_evals

  return solved, func_max


def outer_loop(initial=None, **settings):
  """
  initial: initial optimization parameter values, often taken from prior runs
  settings: a dict of settings (such as theta, Cy, etc) to override

  Returns these same parameters.  If convergence is unsatisfactory, should
  trigger a rerun of current settings instead of moving on.
  """
  function_name = model.__name__

  y_mean = 12.0   #NOTE: SET THE 'mean' HERE!
  y_mean_error = 0.0 #NOTE: SET THE 'error' HERE!
  theta = 8.0      #NOTE: SET THE 'failure criteria' HERE!
  Cy = 3.0           #NOTE: SET THE 'cutoff' HERE!
  Cx = (0.0,0.0,0.0,0.0) #NOTE: SET THE 'wiggle' HERE!
  valid_tol = 0.0  #NOTE: SET THE 'model tolerance' HERE!
  imax_c = 200     #NOTE: SET THE 'max iterations to check valid' HERE!
  imax_i = 10      #NOTE: SET THE 'max inner iterations to set valid' HERE!
  imax_o = 50      #NOTE: SET THE 'max outer iterations to set valid' HERE!

  #APPLY THE SETTINGS OVERRIDES HERE#
  for k,v in settings.items():
    exec("%s = %s" % (str(k),repr(v))) #XXX: HACK

  nx = 2  #NOTE: SET THE NUMBER OF 'h' POINTS HERE!
  ny = 2  #NOTE: SET THE NUMBER OF 'v' POINTS HERE!
  nz = 1  #NOTE: SET THE NUMBER OF 'a' POINTS HERE!

  #XXX: check units versus those in model
  w_lower = [0.0]; Y_lower = [theta]
  w_upper = [1.0]; Y_upper = [30.0+Cy]#[100.0]
  h_lower = [0.5]; a_lower = [0.0];  v_lower = [4.5]
  h_upper = [3.0]; a_upper = [0.0];  v_upper = [7.0]

  target = (y_mean,theta,Cy,Cx,imax_c)
  error = (y_mean_error,None,valid_tol,imax_o,imax_i)
  pars = (target,error)

  npts = (nx,ny,nz)
  from mystic.math.paramtrans import _npts
  _n = _npts(npts)

 #XXX: EDITED TO FIX Y1 == Y_lower
  lower_bounds = (nx * w_lower) + (nx * h_lower) \
               + (ny * w_lower) + (ny * v_lower) \
               + (nz * w_lower) + (nz * a_lower) \
               + (_n * Y_lower)
  upper_bounds = (nx * w_upper) + (nx * h_upper) \
               + (ny * w_upper) + (ny * v_upper) \
               + (nz * w_upper) + (nz * a_upper) \
               + (Y_lower) + (Y_upper)*(_n - 1)
#              + (Y_upper) + (Y_lower)*(_n - 1) #XXX: probably true
  bounds = (lower_bounds,upper_bounds)

  import datetime
  infofile = 'paramlog'
  _stamp = "_".join([infofile, str(job)])
  from mystic.monitors import VerboseLoggingMonitor
  printmon = VerboseLoggingMonitor(1,1,filename=_stamp+'.txt',info=_stamp)
  printmon.info("%s" % datetime.datetime.now().ctime())
# from mystic.monitors import LoggingMonitor
# printmon = LoggingMonitor(1,filename=_stamp+'.txt',info=_stamp)
  printmon.info("...SETTINGS...")
  printmon.info("npop = %s" % npop)
  printmon.info("maxiter = %s" % maxiter)
  printmon.info("maxfun = %s" % maxfun)
  printmon.info("convergence_tol = %s" % convergence_tol)
  printmon.info("crossover = %s" % crossover)
  printmon.info("percent_change = %s" % percent_change)
  printmon.info("..............\n")

  printmon.info(" model: f(x) = %s(x)" % function_name)
  printmon.info(" target: %s" % str(target))
  printmon.info(" error: %s" % str(error))
  printmon.info(" npts: %s" % str((nx,ny,nz)))
  printmon.info("..............\n")

  param_string = "["
  for i in range(nx):
    param_string += "'wx%s', " % str(i+1)
  for i in range(nx):
    param_string += "'x%s', " % str(i+1)
  for i in range(ny):
    param_string += "'wy%s', " % str(i+1)
  for i in range(ny):
    param_string += "'y%s', " % str(i+1)
  for i in range(nz):
    param_string += "'wz%s', " % str(i+1)
  for i in range(nz):
    param_string += "'z%s', " % str(i+1)
  for i in range(_n):
    param_string += "'Y%s', " % str(i+1)
  param_string = param_string[:-2] + "]"

  printmon.info(" parameters: %s" % param_string)
  printmon.info(" lower bounds: %s" % lower_bounds)
  printmon.info(" upper bounds: %s" % upper_bounds)
# print " ..."

 #pars = (target,error)
 #npts = (nx,ny,nz)
 #bounds = (lower_bounds,upper_bounds)
  solved, diameter = maximize(pars,npts,bounds,initial,job,printmon)

  from numpy import array
  from my_dirac_measure import scenario
  c = scenario()
  c.load(solved,npts)
  printmon.info("solved[wx,x]: %s" % zip(c[0].weights,c[0].coords))
  printmon.info("solved[wy,y]: %s" % zip(c[1].weights,c[1].coords))
  printmon.info("solved[wz,z]: %s" % zip(c[2].weights,c[2].coords))
  printmon.info("solved[Y]: %s" % c.values)
 #print "solved: %s" % str( c.flatten(all=True) )

  printmon.info("fails valid wrt model: %s" % \
        c.valid_wrt_model(model, xtol=Cx, ytol=Cy, blamelist=True, \
                          imax=imax_c, ipop=cde, hausdorff=hausdorff))
  printmon.info("mean(y): %s >= %s" % (str( c.get_mean_value() ), y_mean - y_mean_error))
  printmon.info("sum_wts: %s == 1.0" % [sum(w) for w in c.wts])

# try: _Cx = max(Cx)
# except TypeError: _Cx = Cx
  from mystic.math.paramtrans import graphical_distance
  Ry = graphical_distance(model, c, ytol=Cy, xtol=Cx, cutoff=0.0, \
                          imax=0, ipop=cde, hausdorff=hausdorff)
  printmon.info("vertical_distance: %s" % Ry)#, Cy + _Cx))
  Rv = graphical_distance(model, c, ytol=Cy, xtol=Cx, cutoff=0.0, \
                          imax=imax_c, ipop=cde, hausdorff=hausdorff)
  printmon.info("graphical_distance: %s <= %s" % (Rv, Cy))
  printmon.info("%s" % datetime.datetime.now().ctime())

  if False: #XXX: return 'initial' instead of 'solved' when solver fails ?
    return initial, settings#, False
  else:
    return solved, settings#, True


#######################################################################
# rank, bounds, and restart information 
#######################################################################
if __name__ == '__main__':

  #XXX XXX XXX ADJUST THIS CODE AS NEEDED TO PERFORM ALL RUNS XXX XXX XXX
  def looper(variables): #XXX: HACK
    job, (initial,Cy,theta) = variables
    job = "_".join([str(Cy),str(theta),str(job)])#.replace('.','')
    Cx = [Cy, Cy, 0.0]
   #return outer_loop(initial,Cy=Cy,Cx=0.0,theta=theta,job=job)
    return outer_loop(initial,Cy=Cy,Cx=Cx,theta=theta,job=job)

  Cys = [1.0]
  thetas = [11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0] 
  initial = None
  #XXX XXX XXX ---------------------------------------------- XXX XXX XXX
  Cys = [0.12]   #XXX: TEST
  thetas = [7.0] #XXX: TEST

  # get all the possible runs
  from mystic.math.measures import _pack
  runs = _pack([Cys, thetas])
  runs = list(enumerate([(initial,_cy,_theta) for (_cy,_theta) in runs]))
  print "queue = %s" % dict(runs)

  # with 'serial' python
  results = map(looper, runs)
  # with multiprocessing 
  ##nodes = 3 #len(runs)
  ##from pathos.mp_map import mp_map as map  # multiprocessing
  ##results = map(looper, runs, nproc=nodes)


# EOF
