# pandas: store in dataframe (or series) object; convert to other table objects
'''
pandas has to_dict and from_dict, so should be pretty easy to go to DataFrame
both Index and values can take dill.dumps strings or any (raw) object type

can provide option to apply encoding to Index and values (i.e. none, dill, etc)
encoding may be necessary to convert DataFrame to SQL or HDF5, for example
'''
d = dict(a=1,b=2,c=3)
e = dict(a=2,b=5)    
q = dict(d=d,e=e)
import pandas as pd

#NOTE: easily convert to/from nested dicts
p = pd.DataFrame(q)
print p
print p.to_dict()
print p.from_dict({'g': {'x': 2.0, 'y': 5.0}, 'f': {'a': 1, 'c': 3, 'b': 2}})
print p
#s = pd.Series()
#s = s.from_array(dict(a=1,b=2,c=3))
#print s.to_dict()

#NOTE: can't add new columns (or rows?) with update, only replace existing
p.update(({'g': {'x': 2.0, 'y': 5.0}, 'f': {'a': 1, 'c': 3, 'b': 2}}))
print p
p.update({'e': {'a': 2, 'c': 6, 'b': 5}, 'd': {'a': 1, 'c': 7, 'b': 5}})
print p
p.update({'e': {'a': 2, 'c': 6, 'b': 5}, 'f': {'a': 1, 'c': 7, 'b': 5}})
print p

#NOTE: pandas Series/DataFrame can contain any object type (index or data)
f = lambda x:x
import dill
p.ix[0,0] = f            
print p
del p['e']
p.index = [f, 'b','c']
print p
print p['d'][0]
#NOTE: may be good choices for "encoding" the keys and values...
p.index = [dill.dumps(f), 'b','c']
print p.index[0]      
p.index = ['a', 'b','c']
print p
p.ix[0,0] = dill.dumps(f)
p.ix[0,0] = f 
p.ix[0,0] = 1
print p

print pd.Series([1,2,3], index=['a','b',{'x':3}])

