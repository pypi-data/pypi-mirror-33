from __future__ import division

import math
import numpy
import os

import dill
#from klepto.safe import inf_cache as memoized
from klepto import inf_cache as memoized

from klepto.archives import dir_archive
from klepto.keymaps import picklemap

dumps = picklemap(serializer='dill')


def random_random_3d(bins,npoints,boxsize):
    ndens = npoints / boxsize**3.
    bin_shift = numpy.roll(bins,1)
    bin_shift[0] = 0.

    return npoints * (4./3.) * math.pi * ndens * (bins**3 - bin_shift**3) / 2.
    # 1/2 factor comes from autocorrelation...

def random_random(bins,pimax,npoints,boxsize):
    ndens = npoints / boxsize**3.
    bin_shift = numpy.roll(bins,1)
    bin_shift[0] = 0.

    return npoints * math.pi * ndens * (bins**2 - bin_shift**2) * pimax
    # factor of 2*pimax / 2 = pimax, since 1/2 factor comes from autocorrelation...


@memoized(maxsize=None,cache=dir_archive('wp_cache',serialized=True,cached=True),keymap=dumps)
def data_data(bins,pimax,array_galaxy,boxsize):
    return numpy.zeros(bins.shape)

@memoized(maxsize=None,cache=dir_archive('xsi_cache',serialized=True,cached=True),keymap=dumps)
def data_data_3d(bins,array_galaxy,boxsize):
    return numpy.zeros(bins.shape)


## run script interactively

def runscript(pimax,boxsize,npoints):
    array_galaxy = numpy.random.uniform(0.,boxsize,npoints*3).reshape(-1,3)

    bins = 10.**numpy.linspace(numpy.log10(0.1),numpy.log10(30.),40)

    ## compute correlations
    DD = data_data(bins,pimax,array_galaxy,boxsize)
    RR = random_random(bins,pimax,npoints,boxsize)

    w_p = (DD[1:]/RR[1:] - 1.) * pimax * 2.

    # output
    print "projected correlation function:"
    print w_p
    print ""

    ## compute real-space correlations
    DD_xsi = data_data_3d(bins,array_galaxy,boxsize)
    RR_xsi = random_random_3d(bins,npoints,boxsize)

    xsi = (DD_xsi[1:]/RR_xsi[1:] - 1.)

    print "real-space correlation function:"
    print xsi
    print ""

    return bins,w_p,xsi

# load any generated galaxies from disk
data_data.load()
data_data_3d.load()

bins,wp,xsi = runscript(60., 180.7, 2e4)

# cache our generated galaxies on disk
data_data.dump()
data_data_3d.dump()

print data_data.info()
print data_data_3d.info()
