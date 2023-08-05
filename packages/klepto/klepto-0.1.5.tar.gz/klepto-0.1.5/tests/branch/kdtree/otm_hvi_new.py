#! /usr/bin/env python
#
# Author: Bo Li
# Galcit, California Institute of Technology
# Copyright (C) reserved
# libo@caltech.edu
#
# Model: evaluate the function by interpolation based on the values at the grid points from a database 
#

import os, sys, math, string

# verbose = False

V = [4.5, 7.0]
H = [0.5, 3.0]
O = [0, 30]

VD = V[1] - V[0]
HD = H[1] - H[0]
OD = O[1] - O[0]

TOLERANCE = 1.0e-8

def regularize(x):
    if x < 1.0:
        return 0.5
    elif x > 2.0:
        return 3.0
    else:
        return 1.5
    
from memoize import memoized0_nopickle_round as memoized

@memoized(tol=3)
def eureka(x, root_path="."):
    """ Notes for now, will be fixed in the future!!!
        Assumption: (1) thickness can only be 0.5, 1.5 or 3.0
                    (2) obliquity must be zero
                    (3) linear interpolation
    """

#   if verbose:
#       print "input is:", x

    """thickness regularization will be removed in the future"""
    thickness = regularize(float(x[0])) 
    velocity  = float(x[1])
    obliquity = float(x[2])

    if thickness < H[0] or thickness > H[1]  \
       or velocity < V[0] or velocity > V[1] \
       or obliquity < O[0] or obliquity > O[1]:
       #raise IOError, "input is out of the range of investigation"
        from numpy import inf
        return inf # "input is out of the range of investigation"
    
    if root_path == ".":
        baseDir = os.path.dirname(__file__)
    else:
        baseDir = root_path            

    foundFromDB = False
    db_file = baseDir + "//otm_hvi_db.py"
    kd_tree = baseDir + "//kdtree.py"
    
    # evaluate the function by interpolation based on grid points in the database
    if True: #os.path.exists(db_file) and os.path.exists(kd_tree):
        from otm_hvi_db import otm_hvi_tests as db_points
        from otm_hvi_db import otm_hvi_perforation as db_values

        # normalize
        data=[]
        indices=[]
        counter=0
        for var in db_points:            
            if math.fabs(var[0] - thickness) < TOLERANCE: # will be removed as the regularization is gone               
                htemp = (var[0]-H[0])/HD
                vtemp = (var[1]-V[0])/VD
                otemp = (var[2]-O[0])/OD
                data.append( (htemp, vtemp, otemp) ) 
                indices.append(counter)
            counter += 1

        thickness = (thickness - H[0]) / HD
        velocity  = (velocity  - V[0]) / VD
        obliquity = (obliquity - O[0]) / OD

        # build a kdtree of the grid points and query for the nearest neighbors
        from kdtree  import KDTree
        tree = KDTree.construct_from_data(data)
        numofNgh = 2
        outsideofNgh = True        
        v0 = 0.0
        v1 = 0.0
        g0 = 0
        g1 = 0

        while ( outsideofNgh and numofNgh < 10 ):
            nearest = tree.query(query_point=(thickness, velocity, obliquity), t=numofNgh)            
            g0 = indices[data.index(nearest[0])]
            v0 = nearest[0][1]
            d0 = math.fabs(v0 - velocity)            
            for i in range(1, len(nearest)):                
                v1 = nearest[i][1]
                length = math.fabs(v1 - v0)
                di = math.fabs(v1 - velocity)                
                if di <= length and d0 <= length:
                    outsideofNgh = False
                    g1 = indices[data.index(nearest[i])]            
            numofNgh += 1
                
        if outsideofNgh:
#           print "warning: couldn't find the neighborhood of the input point", thickness*HD+H[0], velocity*VD+V[0], obliquity*OD+O[0] 
            v1 = nearest[1][1]
            g1 = indices[data.index(nearest[1])]

#       if verbose:
#          print "nearest neighbors are"
#          print db_points[g0], ":", db_values[g0]
#          print db_points[g1], ":", db_values[g1]

        # linear interpolation
        if math.fabs(v0 - v1) < TOLERANCE:
            raise IOError, "warning: duplicated record found in the database"

        Perf = (v1 - velocity) * db_values[g0] / (v1 - v0) + \
               (velocity - v0) * db_values[g1] / (v1 - v0)

#       if verbose:
#           print "calculated perforation area is", Perf
    else:
        raise IOError, "warning: no database or search algorithm has been found"
    
    return Perf


if __name__ == "__main__":

    if len(sys.argv) < 4 :
        raise IOError, """missing arguments:
        0 :  thickness in mm
        1 :  velocity in km/s
        2 :  obliquity in degrees
       """
    pathname = os.path.dirname(sys.argv[0])
    print "perforation area is:", eureka(sys.argv[1:], os.path.abspath(pathname))
