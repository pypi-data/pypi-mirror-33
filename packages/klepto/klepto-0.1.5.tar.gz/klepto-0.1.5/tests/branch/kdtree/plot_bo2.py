from otm_hvi_new import eureka as eureka_new
from otm_hvi import eureka as eureka_old
def model_factory(h, a, model):
  def _model(v):
    return model([h,v,a])
  return _model

eureka_new_h05 = model_factory(0.5, 0.0, eureka_new)
eureka_new_h15 = model_factory(1.5, 0.0, eureka_new)
eureka_new_h30 = model_factory(3.0, 0.0, eureka_new)
eureka_old_h05 = model_factory(0.5, 0.0, eureka_old)
eureka_old_h15 = model_factory(1.5, 0.0, eureka_old)
eureka_old_h30 = model_factory(3.0, 0.0, eureka_old)

N = 3; npts = 1001
bounds = zip([4.5]*N, [7.0]*N)
from numpy import linspace
v = linspace(bounds[0][0], bounds[0][1], npts)

from numpy import vectorize
new_modelv_h05 = vectorize(eureka_new_h05)
new_modelv_h15 = vectorize(eureka_new_h15)
new_modelv_h30 = vectorize(eureka_new_h30)
old_modelv_h05 = vectorize(eureka_old_h05)
old_modelv_h15 = vectorize(eureka_old_h15)
old_modelv_h30 = vectorize(eureka_old_h30)

import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax1.plot(v, old_modelv_h05(v), label='h = 0.5')
ax1.plot(v, old_modelv_h15(v), label='h = 1.5')
ax1.plot(v, old_modelv_h30(v), label='h = 3.0')
ax1.set_title('old_model')
ax1.set_xlabel('v')
plt.legend()

ax2 = fig.add_subplot(2,1,2)
ax2.plot(v, new_modelv_h05(v), label='h = 0.5')
ax2.plot(v, new_modelv_h15(v), label='h = 1.5')
ax2.plot(v, new_modelv_h30(v), label='h = 3.0')
ax2.set_title('new_model')
ax2.set_xlabel('v')
plt.show()

# optimization
from mystic.solvers import diffev2
from mystic.monitors import VerboseLoggingMonitor

npop = 40; ftol = 1e-6; gtol = None; maxiter=1000
# minima of old model
def cost(x): return eureka_old_h05(x[0])
Loh05mon = VerboseLoggingMonitor(1,50,filename='min_old_h05.txt')
oldLh05 = diffev2(cost, bounds, npop, itermon=Loh05mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return eureka_old_h15(x[0])
Loh15mon = VerboseLoggingMonitor(1,50,filename='min_old_h15.txt')
oldLh15 = diffev2(cost, bounds, npop, itermon=Loh15mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return eureka_old_h30(x[0])
Loh30mon = VerboseLoggingMonitor(1,50,filename='min_old_h30.txt')
oldLh30 = diffev2(cost, bounds, npop, itermon=Loh30mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

# minima of new model
def cost(x): return eureka_new_h05(x[0])
Lnh05mon = VerboseLoggingMonitor(1,50,filename='min_new_h05.txt')
newLh05 = diffev2(cost, bounds, npop, itermon=Lnh05mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return eureka_new_h15(x[0])
Lnh15mon = VerboseLoggingMonitor(1,50,filename='min_new_h15.txt')
newLh15 = diffev2(cost, bounds, npop, itermon=Lnh15mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return eureka_new_h30(x[0])
Lnh30mon = VerboseLoggingMonitor(1,50,filename='min_new_h30.txt')
newLh30 = diffev2(cost, bounds, npop, itermon=Lnh30mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

# maxima of old model
def cost(x): return -eureka_old_h05(x[0])
Uoh05mon = VerboseLoggingMonitor(1,50,filename='max_old_h05.txt')
oldLh05 = diffev2(cost, bounds, npop, itermon=Uoh05mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return -eureka_old_h15(x[0])
Uoh15mon = VerboseLoggingMonitor(1,50,filename='max_old_h15.txt')
oldLh15 = diffev2(cost, bounds, npop, itermon=Uoh15mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return -eureka_old_h30(x[0])
Uoh30mon = VerboseLoggingMonitor(1,50,filename='max_old_h30.txt')
oldLh30 = diffev2(cost, bounds, npop, itermon=Uoh30mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

# maxima of new model
def cost(x): return -eureka_new_h05(x[0])
Unh05mon = VerboseLoggingMonitor(1,50,filename='max_new_h05.txt')
newLh05 = diffev2(cost, bounds, npop, itermon=Unh05mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return -eureka_new_h15(x[0])
Unh15mon = VerboseLoggingMonitor(1,50,filename='max_new_h15.txt')
newLh15 = diffev2(cost, bounds, npop, itermon=Unh15mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)

def cost(x): return -eureka_new_h30(x[0])
Unh30mon = VerboseLoggingMonitor(1,50,filename='max_new_h30.txt')
newLh30 = diffev2(cost, bounds, npop, itermon=Unh30mon, ftol=ftol, gtol=gtol, \
          maxiter=maxiter, bounds=bounds, full_output=1, disp=0, handler=False)
