>>> from klepto import lru_cache 
>>> from klepto.archives import dict_archive
>>> 
>>> @lru_cache(maxsize=5, cache=dict_archive('test'))
... def f(x,y):
...   return 3*x+y
... 
>>> fc = f.__cache__()
>>> fc        
dict_archive('test', {}, cached=True)
>>> fc.archive
dict_archive({}, cached=False)
>>> f(1,2)
5
>>> f(1,3)
6
>>> f(1,4)
7
>>> f(1,2)
5
>>> f(2,2)
8
>>> f(3,2)
11
>>> f(1,2)
5
>>> f(3,2)
11
>>>
>>> # we are at maxsize
>>> fc
dict_archive('test', {-961024585388930287: 11, -3911445610263324862: 6, -3911445610264572437: 5, 704235688799487788: 8, -3911445610257086987: 7}, cached=True)
>>> fc.archive
dict_archive({}, cached=False)
>>> 
>>> # push past maxsize...
>>> f(3,3)
12
>>> # the entire cache dumps to the archive, then is cleared... UNEXPECTED
>>> fc
dict_archive('test', {}, cached=True)
>>> fc.archive
dict_archive({-961024585388930287: 11, -3911445610263324862: 6, -3911445610257086987: 7, -961024585387682712: 12, -3911445610264572437: 5, 704235688799487788: 8}, cached=False)
>>>
>>> #FIXME: add option for archived lru_cache to dump LRU (and not clear all)


>>> @lru_cache(maxsize=5, cache=dict_archive('bar', cached=False))
... def p(x,y):
...   return 3*x+y
... 
>>> pc = p.__cache__()
>>> pc
dict_archive({}, cached=False)
>>> pc.archive
dict_archive({}, cached=False)
>>> pc is pc.archive
True
>>> p(1,2)
5
>>> p(1,3)
6
>>> p(1,4)
7
>>> p(2,1)
7
>>> p(2,2)
8
>>> p(1,2)
5
>>> 
>>> # at maxsize
>>> pc
dict_archive({-3911445610263324862: 6, -3911445610264572437: 5, 704235688799487788: 8, -3911445610257086987: 7, 704235688795745063: 7}, cached=False)
>>> pc.archive
dict_archive({-3911445610263324862: 6, -3911445610264572437: 5, 704235688799487788: 8, -3911445610257086987: 7, 704235688795745063: 7}, cached=False)
>>>
>>> # push past maxsize
>>> p(3,2)
11
>>> # the LRU entry is deleted... and not saved anywhere
>>> pc
dict_archive({-961024585388930287: 11, -3911445610264572437: 5, 704235688799487788: 8, -3911445610257086987: 7, 704235688795745063: 7}, cached=False)
>>> pc.archive
dict_archive({-961024585388930287: 11, -3911445610264572437: 5, 704235688799487788: 8, -3911445610257086987: 7, 704235688795745063: 7}, cached=False)




