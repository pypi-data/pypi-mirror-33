from __future__ import with_statement
import dill as pickle

# write python dict to a file
mydict = {'a': 1, 'b': 2, 'c': 3}
with open('myfile.pkl', 'wb') as file:
  pickle.dump(mydict, file)
print mydict

# read python dict back from the file
with open('myfile.pkl', 'rb') as file:
  mydict = pickle.load(file)
print mydict

# use json, or simplejson, if available
try: 
  import simplejson as pickle
 #import json as pickle
except ImportError:
  pass

# update dict and write to the file again
mydict.update({'d': 4})
with open('myfile.jsn', 'wb') as file:
  pickle.dump(mydict, file)

# read python dict back from the file
with open('myfile.jsn', 'rb') as file:
  mydict = pickle.load(file)
print mydict

