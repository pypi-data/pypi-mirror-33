def createB():       
     class B(object):
       def __init__(self):
         super(B, self).__init__()
     return B


x = createB()
import dill
dill.copy(x)
