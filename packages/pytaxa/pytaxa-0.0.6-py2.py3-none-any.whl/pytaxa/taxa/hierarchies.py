from ..utils import *
from .taxon import Hierarchy

class Hierarchies(object):
    """
    Hierarchies class

    Stores one or more `Hierarchy` objects. Prints first 10 Hierarchy's 
    for brevity.

    Usage:::
        
        ## example Hierarchy objects
        from pytaxa import examples
        ex1 = examples.eg_hierarchy("poa")
        ex2 = examples.eg_hierarchy("puma")
        ex3 = examples.eg_hierarchy("salmo")
        
        # make Hierarchies object
        from pytaxa import Hierarchies
        x = Hierarchies(ex1, ex2, ex3)
        x
    """
    def __init__(self, *x: Hierarchy):
      super(Hierarchies, self).__init__()
      self.x = x

    def __repr__(self):
      hier = "<Hierarchies>\n  "
      if len(self.x) == 0:
        txt = "Empty hierarchy\n  "
      elif self.x[0].is_empty(): 
        txt = "Empty hierarchy\n  "
      else:
        z = [self.print_taxon(z) for z in self.x[:10]]
        no_taxa = "no. hierarchies: %d\n  " % len(self.x)
        txt = '\n  '.join(z)
      return hier + txt

    def __len__(self):
      return self.xlen
