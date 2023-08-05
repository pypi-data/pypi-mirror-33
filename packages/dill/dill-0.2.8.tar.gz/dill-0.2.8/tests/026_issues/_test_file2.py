'''
I like in pandas how one can read/write w/o actually creating a file object.

e.g.

pd.read_table("Data/file.txt",sep="\t")

In dill it would be nice if one could:

dill.load("Data/file.obj")

instead of:

dill.load(open("Data/file.obj","rb"))

Sometimes I'm being careless and do:

dill.load(open("Data/file.obj","wb"))

which then corrupts my file and I have to recalculate it and serialize. Definitely my fault but it would be harder to do if dill did it for you.
'''
