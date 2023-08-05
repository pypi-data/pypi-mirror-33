import dill
dill.dill._trace(1)
from datetime import datetime

def test():
    #from datetime import datetime
    utcNow1 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

dill.settings['recurse'] = True
a = dill.loads(dill.dumps(test))
print(test.__globals__)
print(a.__globals__)
test()
a()
