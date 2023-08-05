import dill

def main():
    class A(object): pass
    class B(A):
        def __init__(self): super(B, self).__init__()
        def do(self): return 5

   #dill.dumps(B())
   #dill.dumps(B(), byref=True)
   #dill.dumps(B(), recurse=True)
    dill.dumps(B(), byref=True, recurse=True)

if __name__ == "__main__":
    main()
