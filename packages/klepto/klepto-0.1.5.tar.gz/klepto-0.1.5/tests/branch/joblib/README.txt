PATHOS
------
stuff from joblib.parallel.Parallel in pathos.mp
joblib.pool.MemmappingPool... joblib.pool.PicklingPool?
pathos leverage helpers in joblib._multiprocessing

#DILL
#----
#joblib.func_inspect.get_func_code in dill? ...hashability

#KLEPTO
#------
#augment joblib.hashing.hash with dill for use in klepto.keymaps
#(extend hash in klepto with joblib.hashing.hash)
#joblib.func_inspect.filter_args in klepto? to ignore args
#joblib.numpy_pickle.*Pickler for klepto archive or keymap
#use bits of joblib.memory.MemorizedFunc if unmodular
#(MemorizedFunc: use __call__ [call, load_output, _persist*] for dict, not func)
#(d={}; func=d.__getitem__ and other attribs? or use Memory directly d='dir')

--------------------------------
Notes on deleted stuff:
- apparently there were only two files left:
  . stack: which I didn't know what to do with (was _pickle, _dill, then stack)
  . misc: which I assume was leftover code




