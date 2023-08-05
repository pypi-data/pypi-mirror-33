from foo import objects
for _type in objects.keys():
    exec "%s = type(objects['%s'])" % (_type,_type)
    
del objects
try:
    del _type
except NameError:
    pass
