# h5py: store objects in a HDF5 hierarchy
'''
h5py allows for a single file to contain a hierarchy of stored objects

a h5py.File object has attrs, which has a (nearly?) complete dict API
however, it appears only basic objects can be stored

could convert objects to pickled strings, but doesn't allow embedded NULLs
so... how convert objects to strings?  (hickle does something like this)

could use h5py for dict in one file, and hickle for directory of files as dict

AHA...
storing any object as a dataset composed of a single pickled object WORKS

also, h5py.File object name and attrs can take protocol=0 strings as names
(thus, we *can* use the 'attrs' dict interface to store our objects)
'''
a = 1
b = 'hello'
d = {'x':3}
class e(object):
  pass
f = lambda x:x
g = e()

"""
import h5py
f = h5py.File('test.hkl','w')
f.attrs['a'] = a
print f.attrs['a']

f.attrs['b'] = b
print f.attrs['b']

f.close()
"""

# however, using hickle's trick... we can store any object as data
import h5py as h5
h = h5.File('test.hkl', 'w')
import dill      
d0 = h.create_dataset(dill.dumps(a,0), data=[dill.dumps(a)])
print dill.loads(d0[0])
d1 = h.create_dataset(dill.dumps(b,0), data=[dill.dumps(b)])
print dill.loads(d1[0])
d2 = h.create_dataset(dill.dumps(d,0), data=[dill.dumps(d)])
print dill.loads(d2[0])
d3 = h.create_dataset(dill.dumps(e,0), data=[dill.dumps(e)])
print dill.loads(d3[0])
d4 = h.create_dataset(dill.dumps(f,0), data=[dill.dumps(f)])
print dill.loads(d4[0])
d5 = h.create_dataset(dill.dumps(g,0), data=[dill.dumps(g)])
print dill.loads(d5[0])

#XXX: use metadata to determine if store directly or as pickled string?
#XXX: use metadata to store object type?
# d0.attrs['type'] = str(type(a))

h.attrs[dill.dumps(a,0)] = dill.dumps(a,0)
print dill.loads(h.attrs[dill.dumps(a,0)])
h.attrs[dill.dumps(b,0)] = dill.dumps(b,0)
print dill.loads(h.attrs[dill.dumps(b,0)])
h.attrs[dill.dumps(d,0)] = dill.dumps(d,0)
print dill.loads(h.attrs[dill.dumps(d,0)])
h.attrs[dill.dumps(e,0)] = dill.dumps(e,0)
print dill.loads(h.attrs[dill.dumps(e,0)])
h.attrs[dill.dumps(f,0)] = dill.dumps(f,0)
print dill.loads(h.attrs[dill.dumps(f,0)])
h.attrs[dill.dumps(g,0)] = dill.dumps(g,0)
print dill.loads(h.attrs[dill.dumps(g,0)])

h.close()


