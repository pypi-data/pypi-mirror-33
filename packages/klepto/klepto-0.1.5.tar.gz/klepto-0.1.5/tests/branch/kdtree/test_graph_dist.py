
def model(x):
	smaller = [x[i] <= 0.0 for i in range(len(x))]
	if all(smaller):
		return 0.0
	else:
		return 5.0

# build a simple dataset
from mystic.math.legacydata import dataset, datapoint
pts = []
pts.append(datapoint([0.,0.,0.], 0., 'a'))
pts.append(datapoint([0.,0.,0.], 1., 'b'))
pts.append(datapoint([0.3,0.3,0.3], 3., 'c'))
pts.append(datapoint([0.3,0.2,0.1], 5., 'd'))
pts.append(datapoint([-0.7,0.,-0.1], 0., 'e'))
pts.append(datapoint([-0.7,0.,-0.1], 3., 'f'))
pts.append(datapoint([-0.7,0.5,-0.1], 0., 'g'))
pts.append(datapoint([0.3,0.3,0.3], 0., 'h'))
d = dataset(pts)
print "dataset:"
for i in d: print i

from mystic.math.paramtrans import graphical_distance
from numpy import set_printoptions
set_printoptions(suppress=True)

# calculate hausdorff distances
Cy = 0.0; Cx = 0.0
hausdorff = (1.0, 1.0, 1.0, 1.0)
print "dH(Cy=0.0,Cx=0.0):", graphical_distance(model, d, ytol=Cy, xtol=Cx, ipop=20, imax=300, hausdorff=hausdorff)

Cy = 0.0; Cx = 0.6
hausdorff = (1.0, 1.0, 1.0, 1.0)
print "dH(Cy=0.0,Cx=0.6):", graphical_distance(model, d, ytol=Cy, xtol=Cx, ipop=20, imax=300, hausdorff=hausdorff)

# Results
"""
dH(Cy=0.0,Cx=0.0): [ 0.  1.  2.  0.  0.  3.  5.  5.]
dH(Cy=0.0,Cx=0.6): [ 0.  1.  2.  0.  0.  2.  0.5  0.9]
"""

