# hickle: store any object in a HDF file
'''
hickle (especially, with dill) can be used to store single objects.

could store dicts of objects, however would need to load the entire dict...

could use directory w/ several HDF5 files as the dict, w/ one hickle per file
'''
d = {'x':3}
class e(object):
  pass
f = lambda x:x
g = e()

import hickle as hkl
import pickle
#NOTE: dill functionality was removed! WTF?
hkl.dump(d, 'test.hkl', 'w')
print hkl.load('test.hkl')

hkl.dump(e, 'test.hkl', 'w')
print pickle.loads(hkl.load('test.hkl').tostring())
#print hkl.load('test.hkl') #WTF: dill

#hkl.dump(f, 'test.hkl', 'w')
#print hkl.load('test.hkl') #WTF: dill

hkl.dump(g, 'test.hkl', 'w')
print pickle.loads(hkl.load('test.hkl').tostring())
#print hkl.load('test.hkl') #WTF: dill
