from otm_hvi_new import eureka as eureka_new
from otm_hvi import eureka as eureka_old
def new_model(h,v):
  return eureka_new([h,v,0.0])

def old_model(h,v):
  return eureka_old([h,v,0.0])

from numpy import vectorize
new_modelv = vectorize(new_model)
old_modelv = vectorize(old_model)

from numpy import mgrid    
h,v = mgrid[0.5:3.0:100j, 4.5:7.0:100j]
eo = old_modelv(h,v)
en = new_modelv(h,v)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.axes import subplot_class_factory
Subplot3D = subplot_class_factory(Axes3D)

fig = plt.figure()
ax1 = Subplot3D(fig, 2,1,1)
ax1.plot_surface(h,v,eo, cmap=plt.cm.jet, rstride=5, cstride=5)
ax1.set_title('old_model')
ax1.set_xlabel('h')
ax1.set_ylabel('v')

ax2 = Subplot3D(fig, 2,1,2)
ax2.plot_surface(h,v,en, cmap=plt.cm.jet, rstride=5, cstride=5)
ax2.set_title('new model')
ax2.set_xlabel('h')
ax2.set_ylabel('v')
plt.show()

