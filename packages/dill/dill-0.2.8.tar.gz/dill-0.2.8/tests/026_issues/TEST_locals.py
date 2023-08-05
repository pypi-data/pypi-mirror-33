import dill
#dill.dill._trace(True)

filename = 'test.dill'

try:
    with open(filename, 'rb') as f:
        dic = dill.loads(f.read())
    print("read from file")
except IOError:
    testVar = 42
    dic = locals()

    with open(filename, 'wb') as f:
        f.write(dill.dumps(dic))

    print("wrote to file")

print(list(dic))

"""
It's the module dict detection. Since the __main__ dict is effectivly being pickled, D1 is used and the pickling happens by reference, which then means that nothing is actually saved. You could turn pickler._session on as a fix, or change __name__ to something other that __main__. Interestingly, doing dic = locals().copy() also fixes the problem as the resulting dict does not contain dic and so fails the checks.
"""
