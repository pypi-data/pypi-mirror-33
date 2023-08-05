##############################
# [ h    v    a ] & [ Y ]
h_lower = 0.5;  h_upper = 3.0
v_lower = 4.5;  v_upper = 7.0
a_lower = 0.0;  a_upper = 0.0
Y_lower = 8.0;  Y_upper = 35.0
gridsize = 100
##############################

# settings
hausdorff = hdn = (1.0, 1.0, 1.0, 1.0)
Cy = .01
Cx = [Cy * xi for xi in hausdorff[:-1]]
tol = 0.0
verbose = False #True
settings = {'hdn':hdn, 'tol':tol, 'Cx':Cx, 'Cy':Cy, 'verbose':verbose}

# optimizer settings
maxiter = 200 #50
npop = 20
imax = 300 #30
ipop = 20
settings.update({'maxiter': maxiter, 'npop':npop, 'imax':imax, 'ipop':ipop})

from otm_hvi_new import eureka as model

# bounds
lower_bounds = (h_lower, v_lower, a_lower)
upper_bounds = (h_upper, v_upper, a_upper)
bounds = (lower_bounds, upper_bounds)
Y_bounds = (Y_lower, Y_upper)


# EOF
