#!/usr/bin/env python
"""
OUQ with model sausage: valid_wrt_model, mean(y), norm(wts)
  with 'wiggle room' around the model in Y
"""

from Looper_BoLiSurr_Cy import *


#######################################################################
# rank, bounds, and restart information 
#######################################################################
if __name__ == '__main__':

  #XXX XXX XXX ADJUST THIS CODE AS NEEDED TO PERFORM ALL RUNS XXX XXX XXX
  def looper(variables): #XXX: HACK
    from Looper_BoLiSurr_Cy import outer_loop, hausdorff
    job, (initial,Cy,theta) = variables
    job = "_".join([str(Cy),str(theta),str(job)])#.replace('.','')
    Cx = [Cy, Cy, 0.0]
   #return outer_loop(initial,Cy=Cy,Cx=0.0,theta=theta,job=job)
    return outer_loop(initial,Cy=Cy,Cx=Cx,theta=theta,job=job)

  Cys = [1.0, 2.0, 2.5, 3.0]
  thetas = [11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0] 
  initial = None
  #XXX XXX XXX ---------------------------------------------- XXX XXX XXX

  # get all the possible runs
  from mystic.math.measures import _pack
  runs = _pack([Cys, thetas])
  runs = list(enumerate([(initial,_cy,_theta) for (_cy,_theta) in runs]))
  print "queue = %s" % dict(runs)

  # with 'serial' python
##results = map(looper, runs)
  # with multiprocessing 
##nodes = 7 #len(runs)
##from pathos.mp_map import mp_map as map  # multiprocessing
##results = map(looper, runs, nproc=nodes)
  # with MPI
# nodes = 7 #len(runs)
# from pyina.ez_map import ez_map2 as map  # mpi4py
# results = map(looper, runs, nnodes=nodes)
  # with MPI on a cluster
  from pyina.ez_map import ez_map2 as map  # mpi4py
  from pyina.launchers import mpirun_launcher, torque_launcher
  from pyina.mappers import carddealer_mapper, equalportion_mapper
  from pyina.schedulers import torque_scheduler
  results = map(looper, runs, nnodes=nodes, queue=queue, timelimit=timelimit, \
                        launcher=mpirun_launcher, scheduler=torque_scheduler)


# EOF
