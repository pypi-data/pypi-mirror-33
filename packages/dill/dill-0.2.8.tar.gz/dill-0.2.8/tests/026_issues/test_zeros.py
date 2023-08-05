'''
klepto uses rounding to provide a cheap interpolation of sorts. For rounding to integers, one may round to zero as 0.0 or -0.0.  klepto should see both as equivalent, Currently it does not, thus two individual cache keys can be produced, when there should only be one (i.e. 0.0).
'''

# simple fix:
k = 0.0
k = -k
print k + 0.0
