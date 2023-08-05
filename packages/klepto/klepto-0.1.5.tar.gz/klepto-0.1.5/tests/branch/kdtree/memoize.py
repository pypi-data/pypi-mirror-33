"""
a decorator named 'memoized' that can memoize a *method* on an object.
"""
def isiterable(x):
 #try:
 #    from collections import Iterable
 #    return isinstance(x, Iterable)
 #except ImportError:
  try:
    iter(x)
    return True
  except TypeError: return False

def deep_round_factory(tol):
  def deep_round(*args, **kwds):
    argstype = type(args) 
    _args = list(args)
    _kwds = kwds.copy()
    for i,j in enumerate(args):
      if isinstance(j, float): _args[i] = round(j, tol) # don't round int
      elif isinstance(j, (str, unicode, type(BaseException()))): continue
      elif isinstance(j, dict): _args[i] = deep_round(**j)[1]
      elif isiterable(j): #XXX: fails on the above, so don't iterate them
        jtype = type(j)
        _args[i] = jtype(deep_round(*j)[0])
    for i,j in kwds.items():
      if isinstance(j, float): _kwds[i] = round(j, tol)
      elif isinstance(j, (str, unicode, type(BaseException()))): continue
      elif isinstance(j, dict): _kwds[i] = deep_round(**j)[1]
      elif isiterable(j): #XXX: fails on the above, so don't iterate them
        jtype = type(j)
        _kwds[i] = jtype(deep_round(*j)[0])
    return argstype(_args), _kwds
  return deep_round

"""
>>> deep_round = deep_round_factory(tol=0)  #FIXME: convert to decorator !!!
>>> deep_round([1.12,2,{'x':1.23, 'y':[4.56,5.67]}], x=set([11.22,44,'hi']))
(([1.0, 2, {'y': [5.0, 6.0], 'x': 1.0}],), {'x': set([11.0, 'hi', 44])})
"""

def deep_round(tol=0):
  def dec(f):
    def func(*args, **kwds):
      _deep_round = deep_round_factory(tol)
      _args,_kwds = _deep_round(*args, **kwds)
      return f(*_args, **_kwds)
    return func
  return dec


#FIXME: the below need expiration of cache due to time, calls, etc...
#       and potentially r/w to database, file, or other caching mechanism
#FIXME: memoize*_round fails when decorating a class method


def memoized0_nopickle_round(tol=0):
    """Decorator that memoizes a function's return value each time it is called.
    If called later with the same arguments, the memoized value is returned, and
    not re-evaluated.  This may lead to memory issues, as memo is never cleared.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats.
    This funciton does not pickle, and thus can only handle basic types.
    """
    memo = {}

    @deep_round(tol)
    def rounded_args(*args, **kwds):
        return (args, kwds)

    def dec(f):
        def func(*args, **kwds):
            try:
                _args, _kwds = rounded_args(*args, **kwds)
                argstr = str((_args, _kwds))
                if not memo.has_key(argstr):
                    memo[argstr] = f(*args, **kwds)
                return memo[argstr]
            except: #TypeError
                return f(*args, **kwds)
        func.memo = memo
        return func
    return dec


def memoized0_round(tol=0):
    """Decorator that memoizes a function's return value each time it is called.
    If called later with the same arguments, the memoized value is returned, and
    not re-evaluated.  This may lead to memory issues, as memo is never cleared.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats.
    """
    memo = {}

    @deep_round(tol)
    def rounded_args(*args, **kwds):
        return (args, kwds)

    def dec(f):
        def func(*args, **kwds):
            try:
                _args, _kwds = rounded_args(*args, **kwds)
               #import cPickle as pickle
                import dill as pickle
                argstr = pickle.dumps((_args, _kwds))
                if not memo.has_key(argstr):
                    memo[argstr] = f(*args, **kwds)
                return memo[argstr]
            except: #TypeError
                return f(*args, **kwds)
        func.memo = memo
        return func
    return dec


def memoized0(f):
    """Decorator that memoizes a function's return value each time it is called.
    If called later with the same arguments, the memoized value is returned, and
    not re-evaluated.  This may lead to memory issues, as memo is never cleared.
    """
    memo = {}

    def func(*args, **kwds):
        try:
           #import cPickle as pickle
            import dill as pickle
            argstr = pickle.dumps((args, kwds))
            if not memo.has_key(argstr):
                memo[argstr] = f(*args, **kwds)
            return memo[argstr]
        except: #TypeError
            return f(*args, **kwds)
    func.memo = memo
    return func


class memoized(object):
    """Decorator that memoizes a function's return value each time it is called.
    If called later with the same arguments, the memoized value is returned, and
    not re-evaluated.  This may lead to memory issues, as memo is never cleared.
    """
    def __init__(self, func):
      self.func = func
      self.memo = {}

    def __call__(self, *args, **kwds):
      try:
         #import cPickle as pickle
          import cPickle as pickle
          argstr = pickle.dumps((args, kwds))
          if not self.memo.has_key(argstr):
              self.memo[argstr] = self.func(*args, **kwds)
          return self.memo[argstr]
      except: #TypeError
          return self.func(*args, **kwds)

    def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__

    def __get__(self, obj, objtype):
      """Support instance methods."""
      import functools
      return functools.partial(self.__call__, obj)

# EOF
