# I define a subclass of rdflib.Graph:

class Thesaurus(rdflib.graph.Graph):
    freq_predicate = rdflib.URIRef('frequency')

    def get_lin_similarity(self, c1_uri, c2_uri):
        return 1

# Then I dump and load an instance of this class:

path = './tests/data/thesaurus.pkl'
import dill
with open(path, 'wb') as f:
    dill.dump(the, f)
with open(path, 'rb') as f:
    the2 = dill.load(f)
print(the2.get_lin_similarity)

# And I get an error

'''
Traceback (most recent call last):
  File "", line 162, in <module>
    print(the2.get_lin_similarity)
AttributeError: 'Graph' object has no attribute 'get_lin_similarity'
'''

# Am i doing something wrong?
