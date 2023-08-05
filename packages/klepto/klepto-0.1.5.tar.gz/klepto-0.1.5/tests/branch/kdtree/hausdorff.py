# results  #XXX: paste from paramlog
solved = [0.72222222212860643, 0.27777777787139357, 3.0, 1.2338940577190955, 1.0, 0.0, 5.5337894951342088, 5.5611284068735243, 1.0, 0.0, 7.0, 25.0, 10.525195965819009, 21.286384951959583]
#XXX XXX XXX XXX XXX XXX XXX

debug = False

# settings
npts = (2,2,1)
hausdorff = (1.0, 1.0, 1.0, 1.0)
Cy = .12; Cx = [Cy * xi for xi in hausdorff[:-1]]
#Cy = .12; Cx = 0.0
imax_c = 300
cde = 20
y_mean = 12.0; y_mean_error = 0.0

from otm_hvi_new import eureka as model

# build a scenario
from numpy import array
from mystic.math.dirac_measure import scenario
c = scenario()
c.load(solved, npts)
if debug:
  print "solved[wx,x]:\n %s" % array(zip(c[0].weights,c[0].coords))
  print "solved[wy,y]:\n %s" % array(zip(c[1].weights,c[1].coords))
  print "solved[wz,z]:\n %s" % array(zip(c[2].weights,c[2].coords))
  print "solved[Y]:\n %s" % array(c.values)

  print "fails valid wrt model:\n %s" % \
        c.valid_wrt_model(model, xtol=Cx, ytol=Cy, blamelist=True, \
                          imax=imax_c, ipop=cde, hausdorff=hausdorff)

  print "mean(y): %s >= %s" % (str( c.get_mean_value() ), y_mean - y_mean_error)
  print "sum_wts: %s == 1.0" % [sum(w) for w in c.wts]

"""
# build a dataset
from mystic.math.legacydata import dataset, datapoint
pts = []
pts.append(datapoint([0.5,5.0,0.], 12., 'a'))
pts.append(datapoint([0.7,5.5,0.], 12., 'b'))
pts.append(datapoint([0.9,6.0,0.], 13., 'c'))
pts.append(datapoint([2.0,6.5,0.], 25., 'd'))
c = dataset(pts)
if debug:
  print "dataset:"
  for i in c: print i
"""

#from mystic.math.paramtrans import graphical_distance
from envelope import graphical_distance
from numpy import set_printoptions
set_printoptions(suppress=True)

# calculate hausdorff distance
print "dH(Cy=%s,Cx=%s):" % (str(Cy),str(array(Cx)))
# 'at the point' (i.e. no optimization steps)
# x,d = graphical_distance(model, c, ytol=Cy, xtol=Cx, ipop=cde, imax=0, hausdorff=hausdorff, cutoff=0.0)
# don't cutoff inside sausage
x,d = graphical_distance(model, c, ytol=Cy, xtol=Cx, ipop=cde, imax=imax_c, hausdorff=hausdorff, cutoff=0.0)
# cutoff inside sausage
#x,d = graphical_distance(model, c, ytol=Cy, xtol=Cx, ipop=cde, imax=imax_c, hausdorff=hausdorff)
print d
print "  at x:\n", x
print "  and Y:\n", array([model(list(xi)) for xi in x])


# EOF
